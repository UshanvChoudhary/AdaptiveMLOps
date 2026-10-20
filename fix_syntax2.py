import os

path = 'backend/tests/test_health.py'
with open(path, 'r', encoding='utf-8') as file:
    content = file.read()
content = content.replace("async async def", "async def")
with open(path, 'w', encoding='utf-8') as file:
    file.write(content)

