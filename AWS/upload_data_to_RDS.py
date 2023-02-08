""" Resources:
https://www.geeksforgeeks.org/how-to-insert-a-pandas-dataframe-to-an-existing-postgresql-table/
NOTE: this file must be run in the home directory Santos-Volpe-SCOPE-Project 
"""

# Import libraries
import pandas as pd
import psycopg2
from config.config import config
from sqlalchemy import create_engine
import json
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# import ../db.py
import helper
from pathlib import Path

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

def upload_FARS_data_to_RDS():
    # Create FARS dataframe
    fars = helper.load_df_from_csv(path='combined_FARS.csv', low_memory = False)

    # Load the FARS data into AWS RDS
    fars.to_sql('FARS(2015-2020)', con=sqlalchemy_conn, if_exists='replace',
            index=False)
    print("uploaded FARS data")

def upload_SDS_data_to_RDS():
    """ Upload combined SDS data to RDS. Currently, each state is in a separate table.
        TODO: remove columns we don't need from each SDS
    """

    # Create SDS dataframe for 
    all_csvs = helper.get_all_csv_filenames(path = 'SDS/Output')
    print("Full list of states: " + str(all_csvs))

    for csv in all_csvs:
        sds = helper.load_df_from_csv(path = csv, low_memory = False)

    # Load the SDS data into AWS RDS
        state = Path(csv).stem
        sds.to_sql('SDS '+state, con=sqlalchemy_conn, if_exists='replace',
                index=False)
        print("uploaded " + state + " SDS data.")

def upload_shapefiles_to_RDS(path = "Shapefiles/"):
    """ Upload shapefiles to RDS
    """

    # Upload state boundaries
    state_path = path+"state.geojson"
    name = Path(state_path).stem
    gdf = helper.load_df_from_geojson(state_path)     # load geojson into a geodataframe
    table_name = "boundaries_"+ name
    gdf.to_sql(table_name, con=sqlalchemy_conn, if_exists='replace',
            index=False)
            

if __name__=="__main__":
    # upload_FARS_data_to_RDS()
    # upload_SDS_data_to_RDS()
    upload_shapefiles_to_RDS()