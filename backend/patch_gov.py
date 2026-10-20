with open('app/api/v1/governance.py', 'r') as f:
    content = f.read()

replacement = '''previous_model = db.query(ModelVersion).filter(ModelVersion.id == previous_deployment.model_version_id).first()
    if not previous_model:
        raise HTTPException(status_code=404, detail="Previous model version not found")'''

content = content.replace('previous_model = previous_deployment.model_version', replacement)

with open('app/api/v1/governance.py', 'w') as f:
    f.write(content)
