import os

with open('backend/tests/test_retraining.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('async def test_retraining_no_eligible_feedback(client, db_session):', 'async def test_retraining_no_eligible_feedback(client, async_db):')

# Remove the trailing fixture
content = content.split('@pytest.fixture\ndef db_session():')[0]

with open('backend/tests/test_retraining.py', 'w', encoding='utf-8') as f:
    f.write(content)
