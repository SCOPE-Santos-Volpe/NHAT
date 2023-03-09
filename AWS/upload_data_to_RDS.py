""" Resources:
https://www.geeksforgeeks.org/how-to-insert-a-pandas-dataframe-to-an-existing-postgresql-table/
https://blog.devgenius.io/3-easy-ways-to-import-a-shapefile-into-a-postgresql-database-c1a4c78104af
https://stackoverflow.com/questions/38361336/write-geodataframe-into-sql-database
https://gis.stackexchange.com/questions/239198/adding-geopandas-dataframe-to-postgis-table
https://gis.stackexchange.com/questions/325415/writing-geopandas-data-frame-to-postgis

NOTE: this file must be run in the home directory Santos-Volpe-SCOPE-Project 
"""

# Import libraries
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import geopandas as gpd
import postgis
import itertools

from geoalchemy2 import Geometry, WKTElement
import psycopg2

from config.config import config
from sqlalchemy import create_engine, Table, Column, Integer, String

import json
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# import ../db.py
import helper
import preprocess_geojsons
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

# Print all table names in the database
query = """ SELECT table_name FROM information_schema.tables WHERE table_schema='public'"""
table_names = pd.read_sql(query, con=sqlalchemy_conn).values.tolist()
table_names = list(itertools.chain(*table_names))
# print(query, table_names)



cursor.execute('CREATE EXTENSION IF NOT EXISTS postgis')


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

    # Create SDS dataframe
    all_csvs = helper.get_all_csv_filenames(path = 'SDS/Output')
    print("Full list of states: " + str(all_csvs))

    for csv in all_csvs:
        sds = helper.load_df_from_csv(path = csv, low_memory = False)

        col_list = []
        # filter SDS 
        for col in sds.columns:
            col_list.append(col)
        print(col_list)

    # Load the SDS data into AWS RDSv
        state = Path(csv).stem
        print('SDS_'+state)
        sds.to_sql('SDS_'+state, con=sqlalchemy_conn, if_exists='replace',
                index=False)
        print("uploaded " + state + " SDS data.")

def upload_geojsons_to_RDS(table_name, preprocessing_func, geojson_folder_path = None, single_geojson_path = None):
    """ Upload shapefiles to RDS
    """
    # Drop the mpo table if it already exists
    if table_name in table_names:
        query = "DROP TABLE {}".format(table_name)
        cursor.execute(query)
        print("Dropped {} since it already exists ".format(table_name))

    gdf = preprocess_geojsons.combine_geojsons_to_single_gdf(geojson_folder_path, single_geojson_path)
    print("about to preprocess using passed in function")
    gdf = preprocessing_func(gdf)
    polygon_gdf, multipoly_gdf = preprocess_geojsons.separate_gdf_into_polygon_multipolygon(gdf)

    # Upload polygon_gdf to RDS
    polygon_gdf.to_sql(table_name, con=sqlalchemy_conn, if_exists='append', index=False, dtype={'geom': Geometry(geometry_type='POLYGON', srid=4269)})
    # Alter table so that the geom column accepts any type
    query = "ALTER TABLE {} ALTER COLUMN geom TYPE geometry(Geometry,4269);".format(table_name)
    cursor.execute(query)
    # Upload multipolygon_gdf to RDS
    multipoly_gdf.to_sql(table_name, con=sqlalchemy_conn, if_exists='append', index=False, dtype={'geom': Geometry(geometry_type='MULTIPOLYGON', srid=4269)})
    
    print("uploaded {} table to RDS".format(table_name))

def upload_states_to_RDS():
    # Load state.csv data
    states = helper.load_df_from_csv(path='states.csv', low_memory = False)
    # Load the FARS data into AWS RDS
    states.to_sql('states', con=sqlalchemy_conn, if_exists='replace',
            index=False)
    print("uploaded states data")


if __name__=="__main__":
    
    # upload_FARS_data_to_RDS()
    # upload_SDS_data_to_RDS()
    # upload_states_to_RDS()

    # upload_geojsons_to_RDS(table_name = 'boundaries_state', preprocessing_func = preprocess_geojsons.preprocess_state_boundaries_df, single_geojson_path = "Shapefiles/state.geojson")
    # upload_geojsons_to_RDS(table_name = 'boundaries_mpo', preprocessing_func = preprocess_geojsons.preprocess_mpo_boundaries_df, geojson_folder_path = "Shapefiles/mpo_boundaries_by_state/")
    # upload_geojsons_to_RDS(table_name = 'boundaries_county', preprocessing_func = preprocess_geojsons.preprocess_county_boundaries_df, geojson_folder_path = "Shapefiles/county_by_state/")
