import os

with open('backend/app/config.py', 'r', encoding='utf-8') as f:
    content = f.read()

if "SECRET_KEY" not in content:
    content = content.replace(
        "ADMIN_API_KEY: str",
        "ADMIN_API_KEY: str\n    SECRET_KEY: str = 'insecure-default-secret'\n    ALGORITHM: str = 'HS256'\n    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30"
    )

with open('backend/app/config.py', 'w', encoding='utf-8') as f:
    f.write(content)
