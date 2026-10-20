with open('app/db/models/deployment.py', 'r') as f:
    content = f.read()

if 'from sqlalchemy.orm import relationship' not in content:
    content = content.replace('import enum', 'import enum\nfrom sqlalchemy.orm import relationship')

if 'model_version = relationship("ModelVersion")' not in content:
    content = content.replace('health_result = Column(JSON, nullable=True)', 'health_result = Column(JSON, nullable=True)\n    model_version = relationship("ModelVersion")')

with open('app/db/models/deployment.py', 'w') as f:
    f.write(content)
