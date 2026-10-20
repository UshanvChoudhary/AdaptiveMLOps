import os

with open('backend/app/db/session.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_content = content.replace("pool_size=10 if 'sqlite' not in uri else 5,", "")
new_content = new_content.replace("max_overflow=20 if 'sqlite' not in uri else 10,", "")

with open('backend/app/db/session.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

