with open('app/db/models/deployment.py', 'r') as f:
    content = f.read()

if 'model_version = relationship("ModelVersion")' not in content:
    content = content.replace('health_result = Column(String)', 'health_result = Column(String)\n    model_version = relationship("ModelVersion")')
    with open('app/db/models/deployment.py', 'w') as f:
        f.write(content)

with open('app/api/v1/governance.py', 'r') as f:
    content = f.read()

replacement = '''previous_model = db.query(ModelVersion).filter(ModelVersion.id == previous_deployment.model_version_id).first()
    if not previous_model:
        raise HTTPException(status_code=404, detail="Previous model version not found")'''

if replacement in content:
    content = content.replace(replacement, 'previous_model = previous_deployment.model_version')
    with open('app/api/v1/governance.py', 'w') as f:
        f.write(content)
