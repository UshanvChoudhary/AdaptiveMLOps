import re

with open('backend/pyproject.toml', 'r', encoding='utf-8') as f:
    content = f.read()

deps = """
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "asyncpg>=0.28.0",
    "aiosqlite>=0.19.0",
"""

content = content.replace('"slowapi>=0.1.8"', '"slowapi>=0.1.8",' + deps)
with open('backend/pyproject.toml', 'w', encoding='utf-8') as f:
    f.write(content)

