import os

with open('backend/app/db/session.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("poolclass=pool.NullPool if 'sqlite' in uri else pool.QueuePool", "poolclass=pool.NullPool if 'sqlite' in uri else None")

with open('backend/app/db/session.py', 'w', encoding='utf-8') as f:
    f.write(content)

