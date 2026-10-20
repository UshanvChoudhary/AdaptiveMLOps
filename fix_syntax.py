import os
import re

# Fix syntax errors in models
models_dir = 'backend/app/db/models'
for f in os.listdir(models_dir):
    if not f.endswith('.py') or f == '__init__.py': continue
    filepath = os.path.join(models_dir, f)
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = content.replace("Column(String(20), nullable=False), index=True", "Column(String(20), nullable=False, index=True)")
    content = content.replace("Column(String(50), nullable=False), index=True", "Column(String(50), nullable=False, index=True)")
    
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)

# Fix registry_service.py import
reg_service = 'backend/app/services/registry_service.py'
with open(reg_service, 'r', encoding='utf-8') as file:
    content = file.read()

content = content.replace("from sqlalchemy.future import select, joinedload", "from sqlalchemy.future import select\nfrom sqlalchemy.orm import joinedload")

with open(reg_service, 'w', encoding='utf-8') as file:
    file.write(content)

