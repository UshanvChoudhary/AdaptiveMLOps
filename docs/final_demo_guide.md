# AdaptiveMLOps — Final Academic Demonstration Guide

This guide provides a reliable, deterministic 7–10 minute demonstration sequence showcasing the full machine learning operations lifecycle for academic review.

---

## 1. Prerequisites and Setup

1. **Verify Services Running:**
   ```bash
   docker-compose up -d
   ```
   Ensure the following containers are up:
   - `adaptive-mlops-postgres-1` (Port 5432)
   - `adaptive-mlops-backend-1` (Port 8000)
   - `adaptive-mlops-frontend-1` (Port 5173 / 3000)

2. **Verify Service Readiness:**
   Open `http://localhost:8000/api/v1/ready` in your browser.  
   Expected JSON response:
   ```json
   {
     "status": "ready",
     "database": "connected",
     "model": "loaded",
     "model_version": "1.0.0"
   }
   ```

3. **Open the Dashboard:**
   Navigate to `http://localhost:5173` (or `http://localhost:3000`).  
   Log in using the administrator demo credentials:
   - **Username:** `admin`
   - **Password:** `password`

4. **Demo Mode Notification:**
   Notice the warning badge: `PROFESSOR DEMO MODE ENABLED (ENABLE_DEMO_MODE=true)`.  
   In production (`ENABLE_DEMO_MODE=false`), demo credentials and mutation endpoints are strictly disabled.

---

## 2. Step-by-Step Demonstration Sequence

### Step 1: Initial System State & Baseline Model (1 min)
- **Action:** In the **Demo Controls** tab, click **`Seed Data`**.
- **Under the Hood:** Initializes the database with roles (`admin`, `reviewer`, `user`), seeds the baseline Customer Support Intent Classifier (`TF-IDF + Logistic Regression v1.0.0`), and writes initial audit logs.
- **Narrative to Professor:**  
  *"We begin with our production champion model (v1.0.0) loaded in memory, serving four customer support intent categories: billing, technical support, refund, and account management. The system is fully operational and healthy."*

### Step 2: Live Inference & Feedback Ingestion (1.5 min)
- **Action:** Navigate to **Predictions & Feedback** tab. Enter a query:
  - Text: `"My internet connection keeps dropping and lights are red"`
  - Click **Predict**.
  - Review the response: Predicted label `technical_support` with confidence and latency metrics.
  - Submit human feedback correcting or confirming the intent.
  - Alternatively, in **Demo Controls**, click **`1. Generate Feedback`** to batch-simulate incoming real-world traffic.
- **Narrative to Professor:**  
  *"Users submit natural language inquiries to the inference endpoint. When human agents or customers provide ground-truth corrections, the feedback records accumulate with status NEW, awaiting the next retraining cycle."*

### Step 3: Monitoring & Concept Drift Alert (1 min)
- **Action:** In **Demo Controls**, click **`8. Simulate Drift`**.
- **UI Check:** Navigate to **Monitoring & Drift** tab.
- **Expected Result:** A drift alert appears showing that input vocabulary distributions have shifted.
- **Narrative to Professor:**  
  *"Our continuous monitoring detects distribution drift. Critically, as required by enterprise governance, a drift alert does not automatically trigger unvetted deployment—it alerts reviewers and flags the need for automated retraining."*

### Step 4: Automated Model Retraining & Artifact Creation (1.5 min)
- **Action:** In **Demo Controls**, click **`2. Trigger Retraining`** (or invoke the retraining engine via API).
- **UI Check:** Navigate to **Retraining Engine** tab.
- **Expected Result:** A new retraining job executes:
  - Fetches base dataset and merges with new feedback.
  - Computes a SHA-256 dataset checksum.
  - Trains a new TF-IDF vectorizer and Logistic Regression classifier.
  - Evaluates validation accuracy, macro F1, and p95 latency.
  - Persists real candidate artifacts (`model.joblib`, `vectorizer.joblib`, `metadata.json`) to `ml/artifacts/{candidate_version}/`.
- **Narrative to Professor:**  
  *"Rather than mocking metrics, our retraining engine generates a genuine scikit-learn candidate pipeline serialized to disk, recording the exact dataset checksum, code revision, and real evaluation metrics."*

### Step 5: Server-Side Quality Gates & Candidate Rejection (1.5 min)
- **Action:** In **Demo Controls**, click **`3b. Create Bad Challenger`**.
- **Expected Result:** A sub-par candidate is registered (e.g. F1=0.72 failing the 0.80 threshold).
- **Action:** Attempt to promote this bad candidate.
- **Expected Result:** Promotion is rejected with `HTTP 400 Bad Request: Candidate failed quality gate (min_f1=0.80)`.
- **UI Check:** Verify the production champion remains intact at `v1.0.0`.
- **Narrative to Professor:**  
  *"Here we demonstrate our server-side safety barrier. A degraded challenger candidate can never replace the production model, even if an operator attempts promotion."*

### Step 6: Valid Candidate Promotion & Zero-Downtime Hot Reload (1 min)
- **Action:** In **Demo Controls**, click **`3a. Create Good Challenger`**, then click **`4. Run Quality Gate`**, and finally **`5. Promote Model`**.
- **Expected Result:** Quality gates pass. The candidate is promoted to `PRODUCTION`, the prior model is marked `ARCHIVED`, and the in-memory prediction service hot-reloads the new model artifact immediately.
- **Verification:** Run a new prediction in the **Predictions** tab to verify that inference is served by the new champion version with zero container downtime.
- **Narrative to Professor:**  
  *"Upon passing quality gates, the new model is promoted. The prediction service atomically updates its in-memory weights directly from the verified disk artifact without restarting the API service."*

### Step 7: Automated Deployment Rollback (1 min)
- **Action:** In **Demo Controls**, click **`6. Simulate Deploy Fail`**, then click **`7. Rollback`**.
- **Expected Result:** The system restores the previous known healthy model (`v1.0.0`), reloads its verified artifact from disk, creates an auditable rollback deployment record, and updates the registry status.
- **UI Check:** Navigate to **Governance** tab to show the full immutable audit trail.
- **Narrative to Professor:**  
  *"If a newly deployed model exhibits anomalies in production, the rollback engine restores the last verified healthy artifact from disk, updates in-memory weights, and records the incident in the audit trail."*

### Step 8: Security and RBAC Negative Proof (1 min)
- **Action:** Log out of the dashboard.
- **Test 1:** Attempt to access an admin endpoint unauthenticated (`curl -X POST http://localhost:8000/api/v1/registry/models/cand-1/promote`). Result: `401 Unauthorized`.
- **Test 2:** Log in as `user` (Role: USER). Attempt to trigger a deployment or promotion. Result: `403 Forbidden (Admin privileges required)`.
- **Test 3:** Demonstrate that setting `ENABLE_DEMO_MODE=false` in `.env` blocks all demo accounts and `/demo/*` endpoints.
- **Narrative to Professor:**  
  *"Finally, we demonstrate strict security. Every administrative action enforces JWT or API-key RBAC, and all demonstration shortcuts are completely locked out outside local testing environments."*

---

## 3. Summary of Demonstrated Capabilities

1. **Full Closed-Loop MLOps:** Live predictions, ground-truth feedback collection, automated retraining, and artifact management.
2. **Deterministic Governance:** Cryptographic dataset checksums, server-side quality gates, and immutable audit logs.
3. **High Availability:** Hot-reloading of model weights and zero-downtime automated rollback.
4. **Hardened Security:** Role-based access control, environment-gated demo configurations, and no hardcoded production credentials.
