# Import libraries
import pandas as pd
import psycopg2
from config.config import config

# Connect to PostgreSQL
params = config(config_db = 'database.ini')
con = psycopg2.connect(**params)
print('Python connected to PostgreSQL!')

# Create table
cur = con.cursor()
cur.execute("""
CREATE TABLE customer(
customer_id INT PRIMARY KEY NOT NULL,
name CHAR(50) NOT NULL,
address CHAR(100),
email CHAR(50),
phone_number CHAR(20));
""")
print('Table created in PostgreSQL')

# Close the connection
con.commit()
con.close()