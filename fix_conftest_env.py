import os

with open('backend/tests/conftest.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('os.environ["ADMIN_API_KEY"] = "secret-admin-key"', '')
content = 'import os\nos.environ["ADMIN_API_KEY"] = "secret-admin-key"\n' + content

with open('backend/tests/conftest.py', 'w', encoding='utf-8') as f:
    f.write(content)

