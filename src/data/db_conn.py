# Import libraries
import pandas as pd
import psycopg2
from config.config import config

# Take in a PostgreSQL table and outputs a pandas dataframe
def load_db_table(config_db, query):
    params = config(config_db)
    engine = psycopg2.connect(**params)
    data = pd.read_sql(query, con = engine)
    return data
