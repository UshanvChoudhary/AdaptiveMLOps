import os
import re

def update_models():
    models_dir = 'backend/app/db/models'
    for f in os.listdir(models_dir):
        if not f.endswith('.py') or f == '__init__.py': continue
        filepath = os.path.join(models_dir, f)
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Add index=True to status, version, created_at
        content = re.sub(r'Column\(String\((.*?)\), nullable=False\)', lambda m: m.group(0) if 'status' not in m.string[m.start()-15:m.start()] else m.group(0) + ', index=True', content)
        content = content.replace('version = Column(String(50), nullable=False, unique=True)', 'version = Column(String(50), nullable=False, unique=True, index=True)')
        content = content.replace('created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))', 'created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), index=True)')
        
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)

update_models()
print("Updated models with indexes.")
