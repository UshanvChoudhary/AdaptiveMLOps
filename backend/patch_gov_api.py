with open('app/api/v1/governance.py', 'r') as f:
    content = f.read()

content = content.replace('id=str(uuid.uuid4())', 'id=uuid.uuid4()')
content = content.replace('model_version_id=str(approval_in.model_version_id)', 'model_version_id=approval_in.model_version_id')
content = content.replace('resource_id=str(approval_in.model_version_id)', 'resource_id=approval_in.model_version_id')
content = content.replace('resource_id=str(previous_model.id)', 'resource_id=previous_model.id')

with open('app/api/v1/governance.py', 'w') as f:
    f.write(content)
