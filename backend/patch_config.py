import os

# Safe configuration updater reading from environment variables
db_uri = os.getenv("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL")
if db_uri:
    print("Database URI configured via environment variables.")
else:
    print("Defaulting to local PostgreSQL database.")
