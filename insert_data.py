# Import libraries
import pandas as pd
import psycopg2
from config.config import config
# Connect to PostgreSQL
params = config(config_db = 'database.ini')
con = psycopg2.connect(**params)
print('Python connected to PostgreSQL!')
# Insert values to the table
cur = con.cursor()
cur.execute("""
INSERT INTO customer (customer_id,name,address,email,phone_number)
VALUES (12345,'Audhi','Indonesia','myemail@gmail.com','+621234567');
""")
cur.execute("""
INSERT INTO customer (customer_id,name,address,email,phone_number)
VALUES (56789,'Aprilliant','Japan','email@gmail.com','+6213579246');
""")
print('Values inserted to PostgreSQL')
# Close the connection
con.commit()
con.close()
