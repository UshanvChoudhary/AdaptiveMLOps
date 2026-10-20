import os

schemas_dir = 'app/schemas'
for filename in os.listdir(schemas_dir):
    if filename.endswith('.py'):
        filepath = os.path.join(schemas_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
        
        if 'class Config:' in content:
            content = content.replace('from pydantic import BaseModel', 'from pydantic import BaseModel, ConfigDict')
            content = content.replace('    class Config:\n        from_attributes = True', '    model_config = ConfigDict(from_attributes=True)')
            content = content.replace('    class Config:\n        orm_mode = True', '    model_config = ConfigDict(from_attributes=True)')
            with open(filepath, 'w') as f:
                f.write(content)
