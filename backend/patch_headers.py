import re

files_to_patch = [
    '../frontend/src/components/Governance.tsx',
    'C:/Users/USER/.gemini/antigravity-ide/brain/3f76bc76-ec9a-4043-bbd9-0ab07069cf59/scratch/verify_phase10.py'
]

for filepath in files_to_patch:
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        content = content.replace("'X-User-Role': 'ADMIN'", "'X-API-Key': 'secret-admin-key'")
        content = content.replace("'X-User-Role': 'REVIEWER'", "'X-API-Key': 'secret-reviewer-key'")
        content = content.replace('"X-User-Role": "ADMIN"', '"X-API-Key": "secret-admin-key"')
        content = content.replace('"X-User-Role": "REVIEWER"', '"X-API-Key": "secret-reviewer-key"')

        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Patched {filepath}")
    except Exception as e:
        print(f"Failed to patch {filepath}: {e}")

