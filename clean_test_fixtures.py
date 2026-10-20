import os
import re

for root, _, files in os.walk('backend/tests'):
    for f in files:
        if f.startswith('test_') and f.endswith('.py') and f != 'test_ui.py':
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Remove from 'SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"' up to the first 'async def test_'
            content = re.sub(r'SQLALCHEMY_DATABASE_URL.*?async def test_', 'async def test_', content, flags=re.DOTALL)
            
            # We also need to rewrite test_database_persistence to use sync_db fixture
            # change 	est_database_persistence(client) to 	est_database_persistence(client, async_db)
            content = re.sub(r'async def test_database_persistence\(client\):', 'async def test_database_persistence(client, async_db):', content)
            
            # inside test_database_persistence:
            # db = TestingSessionLocal()
            # db_record = db.query(Prediction).filter(Prediction.id == uuid.UUID(pred_id)).first()
            # db.close()
            content = content.replace("db = TestingSessionLocal()", "")
            content = content.replace("db_record = db.query(Prediction).filter(Prediction.id == uuid.UUID(pred_id)).first()", "from sqlalchemy.future import select\n    db_record = (await async_db.execute(select(Prediction).filter(Prediction.id == uuid.UUID(pred_id)))).scalars().first()")
            content = content.replace("db.close()", "")
            
            # Also in test_registry
            # db_session = TestingSessionLocal()
            # ...
            content = re.sub(r'async def test_manual_approve_reject\(client, monkeypatch\):', 'async def test_manual_approve_reject(client, monkeypatch, async_db):', content)
            content = re.sub(r'async def test_promote_deliberately_bad_model\(client\):', 'async def test_promote_deliberately_bad_model(client, async_db):', content)
            
            content = content.replace("db_session = TestingSessionLocal()", "db_session = async_db")
            content = content.replace("db_session.add(", "async_db.add(")
            content = content.replace("db_session.commit()", "await async_db.commit()")
            content = content.replace("db_session.close()", "")
            
            # In test_retraining:
            # test_retraining_pagination(client, db_session) is already passing db_session, wait, let's see.
            content = content.replace("db_session.add(", "async_db.add(")
            content = content.replace("db_session.commit()", "await async_db.commit()")
            content = re.sub(r'async def test_retraining_pagination\(client, db_session\):', 'async def test_retraining_pagination(client, async_db):', content)
            
            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)

print("Tests fixtures cleaned up.")
