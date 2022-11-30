# Import libraries
import pandas as pd
import psycopg2
from config.config import config
# Connect to PostgreSQL
params = config(config_db = 'database.ini')
con = psycopg2.connect(**params)
print('Python connected to PostgreSQL!')
# Read the table
cur = con.cursor()
cur.execute("""
SELECT customer_id,name,email FROM customer LIMIT 5;
""")
print('Read table in PostgreSQL')
# Close the connection
con.commit()
con.close()