import os
import re

with open('backend/pytest.ini', 'a', encoding='utf-8') as f:
    f.write("\nasyncio_mode = auto\n")

def to_async_test(content):
    # def test_ -> async def test_
    content = re.sub(r'^def test_', 'async def test_', content, flags=re.MULTILINE)
    
    # client.post -> await client.post
    content = re.sub(r'client\.(get|post|put|delete|patch)\(', r'await client.\1(', content)
    
    return content

for root, _, files in os.walk('backend/tests'):
    for f in files:
        if f.startswith('test_') and f.endswith('.py') and f != 'test_ui.py':
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            content = to_async_test(content)
            
            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)

print("Tests async refactored.")
