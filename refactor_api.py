import os
import re

def to_async_api(content):
    content = content.replace("from sqlalchemy.orm import Session", "from sqlalchemy.ext.asyncio import AsyncSession")
    content = content.replace("db: Session", "db: AsyncSession")
    
    # def -> async def (for router functions)
    content = re.sub(r'^@router\.(.*?)\n(?:@.*?\n)*def ', r'@router.\1\nasync def ', content, flags=re.MULTILINE)
    
    # Add await to service calls
    services = ['prediction_repository', 'feedback_repository', 'registry_service', 'retraining_service', 'drift_service']
    for s in services:
        content = re.sub(r'([a-zA-Z0-9_]+ = )(' + s + r'\.[a-zA-Z0-9_]+\()', r'\1await \2', content)
        content = re.sub(r'^(\s+)(' + s + r'\.[a-zA-Z0-9_]+\()', r'\1await \2', content, flags=re.MULTILINE)
        content = re.sub(r'return (' + s + r'\.[a-zA-Z0-9_]+\()', r'return await \1', content)

    # Some functions like health_check might not have @router immediately before, but they are covered if we just do:
    # Actually wait, health_check in router.py needs to be async. We already patched it if we ran this on router.py.

    return content

api_dir = 'backend/app/api/v1'
for f in os.listdir(api_dir):
    if f.endswith('.py'):
        path = os.path.join(api_dir, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        content = to_async_api(content)
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)

with open('backend/app/api/router.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('def health_check', 'async def health_check')
content = content.replace('def ready_check', 'async def ready_check')
with open('backend/app/api/router.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("API refactored.")
