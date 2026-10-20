import os
import glob

for file_path in glob.glob('backend/tests/test_*.py'):
    with open(file_path, 'r') as f:
        content = f.read()

    # Common override fix
    if "app.dependency_overrides[get_db] = override_get_db" in content and "def override_db_dependency" not in content:
        target = "app.dependency_overrides[get_db] = override_get_db"
        if "test_retraining.py" in file_path:
            replacement = '''@pytest.fixture(autouse=True)
def override_db_dependency():
    app.dependency_overrides[get_db] = override_get_db
    old_session = app.db.session.SessionLocal
    app.db.session.SessionLocal = TestingSessionLocal
    yield
    app.dependency_overrides.clear()
    app.db.session.SessionLocal = old_session'''
        else:
            replacement = '''@pytest.fixture(autouse=True)
def override_db_dependency():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()'''
        content = content.replace(target, replacement)
    
    # Also move create_all into an autouse fixture if it's at module level
    if "Base.metadata.create_all(bind=engine)" in content and "test_retraining.py" not in file_path:
        # test_retraining already has a setup_db fixture
        content = content.replace("Base.metadata.drop_all(bind=engine)\nBase.metadata.create_all(bind=engine)", 
'''@pytest.fixture(autouse=True)
def setup_db_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)''')

    with open(file_path, 'w') as f:
        f.write(content)
