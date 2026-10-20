with open('app/config.py', 'r') as f:
    content = f.read()

import re
content = re.sub(r'SQLALCHEMY_DATABASE_URI: str = .*', 'SQLALCHEMY_DATABASE_URI: str = "postgresql+psycopg2://postgres:fa8c513de6e0734a307047e47ffb862d@bdrb7j6b.ap-southeast.database.insforge.app:5432/insforge?sslmode=require"', content)

with open('app/config.py', 'w') as f:
    f.write(content)
