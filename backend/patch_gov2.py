with open('app/api/v1/governance.py', 'r') as f:
    content = f.read()

content = content.replace('resource_id=previous_model.id', 'resource_id=str(previous_model.id)')

with open('app/api/v1/governance.py', 'w') as f:
    f.write(content)
