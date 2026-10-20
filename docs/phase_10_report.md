# Phase 10 Report: Governance and Rollback

## Objective
Implement production-style governance with Role-Based Access Control (RBAC), approval workflows, audit logging, and automated rollback capabilities.

## Implementation Details

### Database Schema Updates
- **approvals table**: Records manual approval or rejection of model versions by reviewers. Tracks status (PENDING, APPROVED, REJECTED), reviewer details, and comments.
- **audit_logs table**: Records critical events in the system for compliance and traceability. Tracks action type, actor, resource affected, and detailed reasoning.
- Handled SQLite migration schema conflicts and ensured migrations run smoothly.

### Role-Based Access Control (RBAC)
Implemented decorators and dependencies to enforce role-based access:
- **ADMIN**: Can trigger retraining, perform model promotions, execute rollbacks, and view audit logs.
- **REVIEWER**: Can inspect model metrics and approve or reject candidate models.
- **USER**: Can submit predictions and provide feedback.

### API Endpoints
- POST /api/v1/governance/approvals: Submits an approval or rejection decision for a model candidate (Requires REVIEWER).
- GET /api/v1/governance/approvals: Retrieves a list of pending or completed approvals (Requires REVIEWER).
- GET /api/v1/governance/audit-logs: Retrieves the audit history of critical actions (Requires ADMIN).
- POST /api/v1/governance/models/{version}/rollback: Executes a rollback. Automatically identifies the previous healthy production deployment, activates it by creating a new healthy deployment record, and writes a detailed audit log (Requires ADMIN).

### Audit Actions Tracked
- LOGIN
- PREDICTION
- FEEDBACK_SUBMITTED
- RETRAINING_TRIGGERED
- TRAINING_COMPLETED
- MODEL_APPROVED
- MODEL_REJECTED
- DEPLOYMENT_STARTED
- DEPLOYMENT_SUCCEEDED
- DEPLOYMENT_FAILED
- ROLLBACK

### Frontend Dashboard
Added a new **Governance** tab to the central dashboard comprising:
- **Approvals**: UI to review and approve/reject pending models.
- **Audit Logs**: Read-only timeline of critical actions and model lifecycle events.
- **Rollback**: UI to initiate a manual rollback of a problematic model version in production, allowing administrators to specify a rollback reason.

## Verification
- Wrote and executed automated tests via verify_phase10.py.
- Tests validate the full governance flow: registering a model, submitting an approval, fetching audit logs (validating role enforcement), and successfully triggering a rollback that identifies the last healthy deployment and correctly writes an audit log.
- All verification tests pass successfully.

## Post-Review Fixes
Following the implementation review, several critical issues were addressed:
1. **Security (RBAC)**: Migrated Role-Based Access Control (RBAC) away from the insecure x-user-role header. ADMIN and REVIEWER roles are now strictly verified using cryptographically checked X-API-Key matching secrets configured via environment variables.
2. **API & Pydantic**: Upgraded all Pydantic schemas (e.g., monitoring.py, governance.py) from V1 syntax (class Config:) to V2 model_config = ConfigDict(...) to resolve deprecation warnings and ensure forward compatibility.
3. **Architecture (Relationships)**: Defined the missing model_version ORM relationship on the Deployment model, replacing brittle manual lookups during rollbacks with standard SQLAlchemy elationship navigation.
4. **Testing Environment**: Fixed hardcoded configuration bugs in test cases (e.g. 	est_retraining.py) by automatically injecting the requisite ADMIN_API_KEY into pytest.ini and conftest.py, resulting in 100% test pass rates.
5. **Database constraints**: It was noted that SQLite is not fit for a heavy multi-tenant production load due to write locks, but is formally accepted as a design constraint to meet the requirements of a student MLOps project without over-engineering.
