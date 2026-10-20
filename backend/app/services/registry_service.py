import os
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from app.db.models.registry import ModelVersion, TrainingRun, Dataset, EvaluationRun, ModelAudit
from app.config import settings

async def get_all_models(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelVersion]:
    return (await db.execute(select(ModelVersion).options(
        joinedload(ModelVersion.training_run).joinedload(TrainingRun.dataset),
        selectinload(ModelVersion.evaluations)
    ).offset(skip).limit(limit))).scalars().unique().all()

async def get_model_by_version(db: AsyncSession, version: str) -> ModelVersion:
    return (await db.execute(select(ModelVersion).options(
        joinedload(ModelVersion.training_run).joinedload(TrainingRun.dataset),
        selectinload(ModelVersion.evaluations)
    ).filter(ModelVersion.version == version))).scalars().unique().first()

async def get_evaluations_for_model(db: AsyncSession, model_version_id: str) -> List[EvaluationRun]:
    return (await db.execute(select(EvaluationRun).filter(EvaluationRun.model_version_id == model_version_id))).scalars().all()

async def get_champion_model(db: AsyncSession, for_update: bool = False) -> ModelVersion:
    query = select(ModelVersion).options(
        selectinload(ModelVersion.evaluations)
    ).filter(ModelVersion.status == 'PRODUCTION')
    if for_update:
        query = query.with_for_update()
    return (await db.execute(query)).scalars().unique().first()

async def evaluate_candidate_for_promotion(db: AsyncSession, candidate: ModelVersion, champion: ModelVersion = None) -> dict:
    if not candidate.evaluations:
        return {'decision': 'REJECT', 'reason': 'No evaluations found for candidate.'}
    
    cand_metrics = candidate.evaluations[-1].metrics
    cand_f1 = float(cand_metrics.get('f1') or cand_metrics.get('f1_score', 0))
    cand_acc = float(cand_metrics.get('accuracy', 0))
    cand_lat = float(cand_metrics.get('latency_p95_ms') or cand_metrics.get('latency_p99_ms', 0))
    
    # Enforce quality gates
    if cand_f1 < settings.MIN_F1 or cand_acc < settings.MIN_ACCURACY:
        return {'decision': 'REJECT', 'reason': f'Metrics below minimum thresholds (F1: {cand_f1:.3f}, Acc: {cand_acc:.3f})'}
        
    if cand_lat > settings.MAX_LATENCY_P95_MS:
        return {'decision': 'REJECT', 'reason': f'Latency too high ({cand_lat}ms)'}

    if not champion:
        return {'decision': 'PROMOTE', 'reason': 'No existing champion model.'}
        
    if not champion.evaluations:
        return {'decision': 'PROMOTE', 'reason': 'Champion has no evaluations.'}
        
    champ_metrics = champion.evaluations[-1].metrics
    champ_f1 = float(champ_metrics.get('f1') or champ_metrics.get('f1_score', 0))
    
    if cand_f1 > champ_f1 + settings.MIN_IMPROVEMENT:
        return {'decision': 'PROMOTE', 'reason': f'Candidate improved F1 by {cand_f1 - champ_f1:.4f}'}
    elif cand_f1 >= champ_f1:
        return {'decision': 'REVIEW', 'reason': f'Candidate slightly better or equal. Requires review. F1 diff: {cand_f1 - champ_f1:.4f}'}
    else:
        return {'decision': 'REJECT', 'reason': f'Candidate performs worse than champion. F1 diff: {cand_f1 - champ_f1:.4f}'}

async def promote_model(db: AsyncSession, version: str) -> dict:
    # Lock candidate model
    candidate = (await db.execute(select(ModelVersion).options(
        selectinload(ModelVersion.evaluations)
    ).filter(ModelVersion.version == version).with_for_update())).scalars().unique().first()
    
    if not candidate:
        raise ValueError('Candidate not found')
        
    if candidate.status == 'PRODUCTION':
        return {'decision': 'REVIEW', 'reason': 'Already in production', 'candidate_version': version, 'champion_version': version}
        
    if candidate.status != 'CANDIDATE':
        return {'decision': 'REJECT', 'reason': f'Cannot promote a model with status {candidate.status}.', 'candidate_version': version, 'champion_version': None}

    # Lock champion model
    champion = await get_champion_model(db, for_update=True)
    
    evaluation_result = await evaluate_candidate_for_promotion(db, candidate, champion)
    
    if evaluation_result['decision'] == 'PROMOTE':
        # Verify artifact exists on disk before promotion
        artifact_path = candidate.artifact_path
        if not os.path.isabs(artifact_path):
            artifact_path = os.path.join(settings.BASE_DIR, artifact_path)

        if not os.path.exists(artifact_path):
            candidate.status = 'REJECTED'
            audit = ModelAudit(model_version_id=candidate.id, action='REJECT', reason=f"Candidate artifact path '{candidate.artifact_path}' does not exist on disk.")
            db.add(audit)
            await db.commit()
            await db.refresh(candidate)
            return {
                'decision': 'REJECT',
                'reason': f"Candidate artifact path '{candidate.artifact_path}' does not exist on disk.",
                'candidate_version': candidate.version,
                'champion_version': champion.version if champion else None
            }

        # Demote previous champion
        if champion:
            champion.status = 'ARCHIVED'
            
        candidate.status = 'PRODUCTION'
        audit = ModelAudit(model_version_id=candidate.id, action='PROMOTE', reason=evaluation_result['reason'])
        db.add(audit)
        await db.commit()
        await db.refresh(candidate)

        # Switch active in-memory prediction service model
        try:
            from app.ml.prediction_service import prediction_service
            prediction_service.artifact_dir = artifact_path
            prediction_service.load_model()
        except Exception:
            pass
        
    elif evaluation_result['decision'] == 'REJECT':
        candidate.status = 'REJECTED'
        audit = ModelAudit(model_version_id=candidate.id, action='REJECT', reason=evaluation_result['reason'])
        db.add(audit)
        await db.commit()
        await db.refresh(candidate)
        
    return {
        'decision': evaluation_result['decision'],
        'reason': evaluation_result['reason'],
        'candidate_version': candidate.version,
        'champion_version': champion.version if champion else None
    }

async def manual_approve_model(db: AsyncSession, version: str) -> ModelVersion:
    candidate = (await db.execute(select(ModelVersion).filter(ModelVersion.version == version).with_for_update())).scalars().first()
    if not candidate:
        raise ValueError('Candidate not found')
        
    if candidate.status != 'CANDIDATE':
        raise ValueError(f'Cannot approve model with status {candidate.status}')
        
    champion = await get_champion_model(db, for_update=True)
    if champion and champion.id != candidate.id:
        champion.status = 'ARCHIVED'
        
    candidate.status = 'PRODUCTION'
    audit = ModelAudit(model_version_id=candidate.id, action='APPROVE', reason='Manual approval')
    db.add(audit)
    await db.commit()
    await db.refresh(candidate)
    return candidate

async def manual_reject_model(db: AsyncSession, version: str) -> ModelVersion:
    candidate = (await db.execute(select(ModelVersion).filter(ModelVersion.version == version).with_for_update())).scalars().first()
    if not candidate:
        raise ValueError('Candidate not found')
        
    if candidate.status != 'CANDIDATE':
        raise ValueError(f'Cannot reject model with status {candidate.status}')
        
    candidate.status = 'REJECTED'
    audit = ModelAudit(model_version_id=candidate.id, action='REJECT', reason='Manual rejection')
    db.add(audit)
    await db.commit()
    await db.refresh(candidate)
    return candidate
