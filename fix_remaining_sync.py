import os
import re

# Fix remaining db.query in API
api_dir = 'backend/app/api/v1'
for f in os.listdir(api_dir):
    if f.endswith('.py'):
        path = os.path.join(api_dir, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        content = content.replace("db.query(RetrainingJob).count()", "(await db.execute(select(func.count(RetrainingJob.id)))).scalar()")
        if "from sqlalchemy import func" not in content and "func.count" in content:
            content = "from sqlalchemy import func\n" + content
        if "from sqlalchemy.future import select" not in content and "select(" in content:
            content = "from sqlalchemy.future import select\n" + content
        
        content = content.replace("db.query(ModelVersion).count()", "(await db.execute(select(func.count(ModelVersion.id)))).scalar()")
        
        # fix missing await for save_prediction
        content = re.sub(r'(\s+)save_prediction\(', r'\1await save_prediction(', content)
        
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)

# Fix tests using TestClient
for root, _, files in os.walk('backend/tests'):
    for f in files:
        if f.startswith('test_') and f.endswith('.py') and f != 'test_ui.py':
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Remove TestClient import and fixture
            content = re.sub(r'from fastapi\.testclient import TestClient\n', '', content)
            content = re.sub(r'@pytest\.fixture\s*def client\(.*?\):\s*with TestClient\(app\) as [a-z]+:\s*yield [a-z]+', '', content, flags=re.DOTALL)
            content = re.sub(r'@pytest\.fixture\s*def client\(\):\s*with TestClient\(app\) as [a-z]+:\s*yield [a-z]+', '', content, flags=re.DOTALL)
            
            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)

print("Tests & API fixed.")
