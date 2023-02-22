""" Resources:
https://www.geeksforgeeks.org/how-to-insert-a-pandas-dataframe-to-an-existing-postgresql-table/
NOTE: this file must be run in the home directory Santos-Volpe-SCOPE-Project 
"""

# Import libraries
import pandas as pd
import psycopg2
from config.config import config
from sqlalchemy import create_engine

# Establish sqlalchemy connection
conn_string = 'postgresql://scope_team:greenTea123@database-1.ci75bfibgs4e.us-east-1.rds.amazonaws.com/FARS'
db = create_engine(conn_string)
sqlalchemy_conn = db.connect()
print('Python connected to PostgreSQL via Sqlalchemy')

# Establish psycogp2 connection
params = config(config_db = 'database.ini')
conn = psycopg2.connect(**params)
conn.autocommit = True
cursor = conn.cursor()
print('Python connected to PostgreSQL via Psycogp2!')

# Create FARS dataframe
df = pd.read_csv("FARS/combined_FARS.csv") 

# Get the first 10 rows to test
df_trimmed = df.head(10)
print(df_trimmed)

# Load the FARS data into AWS
df_trimmed.to_sql('data', con=sqlalchemy_conn, if_exists='replace',
          index=False)

# # Create table
# cur = con.cursor()
# cur.execute("""
# CREATE TABLE customer(
# customer_id INT PRIMARY KEY NOT NULL,
# name CHAR(50) NOT NULL,
# address CHAR(100),
# email CHAR(50),
# phone_number CHAR(20));
# """)
# print('Table created in PostgreSQL')

# # Close the connection
# con.commit()
# con.close()