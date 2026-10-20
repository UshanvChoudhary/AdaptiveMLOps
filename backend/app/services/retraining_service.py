import os
import json
import uuid
import time
import hashlib
import logging
from datetime import datetime, timezone
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import joblib

from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.retraining import RetrainingJob
from app.db.models.feedback import Feedback
from app.db.models.prediction import Prediction
from app.db.models.registry import Dataset, TrainingRun, ModelVersion, EvaluationRun
from app.schemas.retraining import RetrainingTriggerRequest
from app.config import settings

logger = logging.getLogger(__name__)

async def trigger_retraining(db: AsyncSession, request: RetrainingTriggerRequest) -> RetrainingJob:
    existing = (await db.execute(select(RetrainingJob).filter(RetrainingJob.status.in_(["QUEUED", "RUNNING"])).with_for_update())).scalars().first()
    if existing:
        raise ValueError("A retraining job is already in progress.")

    feedback_count = (await db.execute(select(func.count(Feedback.id)).filter(
        Feedback.is_correct == False,
        Feedback.corrected_label != None,
        Feedback.feedback_status == "pending"
    ))).scalar() or 0

    if request.trigger_type == "FEEDBACK_THRESHOLD":
        threshold = getattr(settings, "RETRAIN_FEEDBACK_THRESHOLD", 5)
        if feedback_count < threshold:
            raise ValueError(f"Feedback count ({feedback_count}) below threshold ({threshold}).")

    job = RetrainingJob(
        trigger_type=request.trigger_type,
        reason=request.reason or "Automatic trigger",
        feedback_count=feedback_count,
        status="QUEUED"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

async def run_retraining_job(db: AsyncSession, job_id: uuid.UUID):
    job = (await db.execute(select(RetrainingJob).filter(RetrainingJob.id == job_id))).scalars().first()
    if not job:
        return

    # Secondary concurrency check
    running_job = (await db.execute(select(RetrainingJob).filter(RetrainingJob.status == "RUNNING"))).scalars().first()
    if running_job and running_job.id != job_id:
        job.status = "FAILED"
        job.error_message = "Aborted: Another job is currently running."
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()
        return

    job.status = "RUNNING"
    job.started_at = datetime.now(timezone.utc)
    await db.commit()

    try:
        feedbacks = (await db.execute(select(Feedback).filter(
            Feedback.is_correct == False,
            Feedback.corrected_label != None,
            Feedback.feedback_status == "pending"
        ))).scalars().all()

        if not feedbacks:
            job.status = "FAILED"
            job.error_message = "No eligible feedback to train on."
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()
            return

        # Load base demo dataset
        base_data_path = os.path.join(settings.BASE_DIR, "ml", "data", "demo_dataset.csv")
        if os.path.exists(base_data_path):
            base_df = pd.read_csv(base_data_path)
        else:
            base_df = pd.DataFrame([
                {"text": "I was charged twice on my invoice", "intent": "billing"},
                {"text": "My service is down and not responding", "intent": "technical_support"},
                {"text": "I would like to request a refund", "intent": "refund"},
                {"text": "Update my email address and password", "intent": "account_management"}
            ])

        # Augment with verified feedback corrections
        feedback_rows = []
        for fb in feedbacks:
            pred = (await db.execute(select(Prediction).filter(Prediction.id == fb.prediction_id))).scalars().first()
            input_text = pred.input_text if pred else f"Feedback inquiry for {fb.corrected_label}"
            feedback_rows.append({"text": input_text, "intent": fb.corrected_label})
            
        fb_df = pd.DataFrame(feedback_rows)
        combined_df = pd.concat([base_df, fb_df], ignore_index=True)
        combined_df['text'] = combined_df['text'].fillna('').astype(str)
        combined_df = combined_df[combined_df['text'].str.strip() != '']

        # Compute checksum
        data_bytes = combined_df.to_csv(index=False).encode('utf-8')
        dataset_checksum = hashlib.sha256(data_bytes).hexdigest()
        
        new_version = f"v1.0+{len(feedbacks)}f"
        dataset = (await db.execute(select(Dataset).filter(Dataset.version == new_version))).scalars().first()
        if not dataset:
            dataset = Dataset(version=new_version, checksum=dataset_checksum)
            db.add(dataset)
            await db.commit()
            await db.refresh(dataset)
        
        job.dataset_id = dataset.id
        
        # Train actual TF-IDF + Logistic Regression
        X_train, X_test, y_train, y_test = train_test_split(
            combined_df['text'], combined_df['intent'], test_size=0.2, random_state=42
        )
        
        vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        X_train_vec = vectorizer.fit_transform(X_train)
        
        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(X_train_vec, y_train)
        
        X_test_vec = vectorizer.transform(X_test)
        y_pred = model.predict(X_test_vec)
        
        # Calculate real metrics
        real_accuracy = float(accuracy_score(y_test, y_pred))
        real_f1 = float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
        real_precision = float(precision_score(y_test, y_pred, average='weighted', zero_division=0))
        real_recall = float(recall_score(y_test, y_pred, average='weighted', zero_division=0))
        
        # Latency benchmark
        sample_texts = list(X_test[:10]) or ["billing issue", "refund please"]
        lats = []
        for s in sample_texts:
            t0 = time.perf_counter()
            v = vectorizer.transform([s])
            model.predict(v)
            lats.append((time.perf_counter() - t0) * 1000)
        p95_lat = float(pd.Series(lats).quantile(0.95)) if lats else 15.0

        hyperparameters = model.get_params()
        run = TrainingRun(
            dataset_id=dataset.id,
            git_commit="latest-feedback",
            hyperparameters={"C": 1.0, "penalty": "l2", "solver": "lbfgs"},
            status="COMPLETED"
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)

        # Create candidate artifact on disk
        cand_version = f"cand-{uuid.uuid4().hex[:6]}"
        cand_rel_dir = os.path.join("ml", "artifacts", cand_version)
        cand_abs_dir = os.path.join(settings.BASE_DIR, cand_rel_dir)
        os.makedirs(cand_abs_dir, exist_ok=True)
        
        joblib.dump(model, os.path.join(cand_abs_dir, "model.joblib"))
        joblib.dump(vectorizer, os.path.join(cand_abs_dir, "vectorizer.joblib"))
        
        eval_metrics = {
            "accuracy": real_accuracy,
            "f1": real_f1,
            "f1_score": real_f1,
            "precision": real_precision,
            "recall": real_recall,
            "latency_p95_ms": p95_lat,
            "metric_type": "real_evaluation"
        }
        
        metadata = {
            "model_version": cand_version,
            "algorithm": "Logistic Regression + TF-IDF",
            "dataset_version": new_version,
            "dataset_checksum": dataset_checksum,
            "training_timestamp": datetime.now(timezone.utc).isoformat(),
            "evaluation_metrics": eval_metrics,
            "source_git_commit": "latest"
        }
        with open(os.path.join(cand_abs_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, default=str)

        model_version_obj = ModelVersion(
            version=cand_version,
            algorithm="Logistic Regression + TF-IDF",
            training_run_id=run.id,
            artifact_path=cand_rel_dir,
            status="CANDIDATE"
        )
        db.add(model_version_obj)
        await db.commit()
        await db.refresh(model_version_obj)

        job.candidate_model_version_id = model_version_obj.id

        eval_run = EvaluationRun(
            model_version_id=model_version_obj.id,
            dataset_id=dataset.id,
            metrics=eval_metrics
        )
        db.add(eval_run)
        
        for fb in feedbacks:
            fb.feedback_status = "processed"
            
        job.status = "COMPLETED"
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()

    except Exception as e:
        logger.error(f"Retraining job failed: {e}")
        await db.rollback()
        try:
            job = (await db.execute(select(RetrainingJob).filter(RetrainingJob.id == job_id))).scalars().first()
            if job:
                job.status = "FAILED"
                job.error_message = str(e)
                job.completed_at = datetime.now(timezone.utc)
                await db.commit()
        except Exception as inner_e:
            logger.error(f"Failed to record job failure: {inner_e}")
