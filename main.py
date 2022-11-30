# Import libraries
from src.data.db_conn import load_db_table
from config.config import get_project_root

# Project root
PROJECT_ROOT = get_project_root()
print(PROJECT_ROOT)

# Read database - PostgreSQL
df = load_db_table(config_db = 'database.ini', query = 'SELECT * FROM customer LIMIT 5')
print(df)