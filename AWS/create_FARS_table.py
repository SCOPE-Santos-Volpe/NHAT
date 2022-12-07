""" Resources:
https://www.geeksforgeeks.org/how-to-insert-a-pandas-dataframe-to-an-existing-postgresql-table/
NOTE: this file must be run in the home directory Santos-Volpe-SCOPE-Project 
"""

# Import libraries
import pandas as pd
import psycopg2
from config.config import config
from sqlalchemy import create_engine
import utils

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

#------------------------------------------------------------
# Create FARS dataframe
fars = utils.load_df_from_csv(path='combined_FARS.csv', low_memory = False)

# Load the FARS data into AWS
fars.to_sql('FARS(2015-2020)', con=sqlalchemy_conn, if_exists='replace',
          index=False)