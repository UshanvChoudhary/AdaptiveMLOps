# AdaptiveMLOps - Phase 1 Report

## Objective
Create a reproducible baseline ML training and evaluation pipeline for customer-support ticket classification using TF-IDF and Logistic Regression.

## Implementation Details

1. **Dataset Generation & Loading:**
   - Synthetic data created and stored at ml/data/demo_dataset.csv.
   - load_and_clean_data in ackend/app/ml/data_validation.py handles missing values and duplicates via pandas, and drops any structurally invalid records.

2. **Schema Validation:**
   - Designed a Pydantic schema TicketData in ackend/app/ml/schema.py which enforces structure and constraints.
   - Enforces classification labels strictly against IntentEnum (billing, refund, technical_support, account_management).
   - This schema is integrated actively during the loading process to sanitize inputs natively.

3. **Preprocessing:**
   - Implemented TF-IDF vectorization with a max feature limit in ackend/app/ml/preprocessing.py.

4. **Model Architecture:**
   - Uses LogisticRegression from scikit-learn in ackend/app/ml/model.py.
   - The ML logic remains decoupled from FastAPI per architectural principles.

5. **Scripts:**
   - **Validation:** ml/scripts/validate_data.py ensures the dataset can be cleaned properly.
   - **Training:** ml/scripts/train.py handles deterministic splitting, fitting the vectorizer and model, calculating actual metrics (ccuracy, precision, ecall, 1_score, confusion_matrix), and saving artifacts. It extracts a designated 	est_dataset.csv explicitly for validation.
   - **Evaluation:** ml/scripts/evaluate.py cleanly loads serialized artifacts and independently evaluates them against the holdout 	est_dataset.csv (preventing data leakage).

6. **Artifact Metadata:**
   - Handled via ackend/app/ml/artifacts.py.
   - The metadata captures model and dataset versions, dataset SHA-256 checksums, timestamps, deterministic random seeds, hyper-parameters, test metrics, and the source Git commit.
   
7. **Testing & Framework:**
   - Pydantic Settings updated to V2 standard pydantic_settings.
   - Verified functionality with comprehensive pytest unit tests (ackend/tests/test_ml.py), testing the exact model serialization mechanisms as well.

## Status
**Phase 1 Complete.** 
Ready to proceed with subsequent phases.
