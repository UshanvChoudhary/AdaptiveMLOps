with open('.env', 'r') as f:
    content = f.read()

import re
content = re.sub(r'SQLALCHEMY_DATABASE_URL=.*', 'SQLALCHEMY_DATABASE_URL="postgresql://postgres:fa8c513de6e0734a307047e47ffb862d@bdrb7j6b.ap-southeast.database.insforge.app:5432/insforge?sslmode=require"', content)

with open('.env', 'w') as f:
    f.write(content)
