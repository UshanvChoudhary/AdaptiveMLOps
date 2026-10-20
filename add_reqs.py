import os

req_path = 'backend/requirements.txt'
with open(req_path, 'a') as f:
    f.write('\npython-jose[cryptography]==3.3.0\npasslib[bcrypt]==1.7.4\nasyncpg==0.28.0\naiosqlite==0.19.0\nhttpx==0.24.1\n')

