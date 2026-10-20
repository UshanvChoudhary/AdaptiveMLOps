import os

# Safe environment helper reading from environment variables
db_url = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URI")
if db_url:
    print("Database URL present in environment.")
else:
    print("No database URL set in environment.")
