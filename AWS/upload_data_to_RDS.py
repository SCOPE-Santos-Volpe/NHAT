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
import preprocess_SDS_data
import preprocess_Justice40_data
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
print(query, table_names)

cursor.execute('CREATE EXTENSION IF NOT EXISTS postgis')

def upload_FARS_data_to_RDS():
    # Create FARS dataframe
    # fars = helper.load_df_from_csv(path='combined_FARS_preprocessed.csv', low_memory = False)
    fars = helper.load_df_from_csv(path='FARS/FARS_w_MPO_County_Identifiers.csv', low_memory = False)
    
    # Load the FARS data into AWS RDS
    fars.to_sql('FARS', con=sqlalchemy_conn, if_exists='replace',
            index=False)
    print("uploaded FARS data")

def upload_SDS_data_to_RDS():
    """ Upload combined SDS data to RDS. Currently, each state is in a separate table.
    """
    # Get all processed SDS
    all_csvs = helper.get_all_csv_filenames(path = 'SDS/Output_w_MPO_County_Identifiers/')
    print("Full list of states: " + str(all_csvs))

    # Process each state's crash data one by one
    for csv in all_csvs:
        # Get state name and state initial
        state_name = Path(csv).stem
        
        sds = helper.load_df_from_csv(path = csv, low_memory = False)
        # sds = helper.load_gdf_from_geojson(geojson_path) 
        # sds = preprocess_geojsons.change_gdf_geometry_to_geom()

        # Upload SDS data into AWS RDSv    
        sds.to_sql('SDS_'+state_name, con=sqlalchemy_conn, if_exists='replace',
                index=False)
        print("uploaded " + state_name + " SDS data.")

def upload_Justice40_data_to_RDS():
    """ Upload Justice40 data to RDS
        Note: make sure to run the preprocessing script before this function
    """
    justice40 = helper.load_df_from_csv(path = "Justice40/justice_40_communities_clean.csv", low_memory = False)
    # justice40 = preprocess_Justice40_data.preprocess_justice40_data(justice40)
    
    # Load the FARS data into AWS RDS
    justice40.to_sql('Justice40', con=sqlalchemy_conn, if_exists='replace',
            index=False)
    print("uploaded justice40 data")

def upload_states_to_RDS():
    # Load state.csv data
    states = helper.load_df_from_csv(path='states.csv', low_memory = False)
    # Load the FARS data into AWS RDS
    states.to_sql('states', con=sqlalchemy_conn, if_exists='replace',
            index=False)
    print("uploaded states data")

def upload_geojsons_to_RDS(table_name, preprocessing_func, geojson_folder_path = None, single_geojson_path = None, drop_exisiting_table = True):
    """ Upload shapefiles to RDS
    """
    # Drop the table if it already exists
    if table_name in table_names and drop_exisiting_table:
        query = "DROP TABLE {}".format(table_name)
        cursor.execute(query)
        print("Dropped {} since it already exists ".format(table_name))

    gdf = preprocess_geojsons.combine_geojsons_to_single_gdf(geojson_folder_path, single_geojson_path)
    # gdf = combine_geojsons_to_single_gdf(single_geojson_path = "Shapefiles/census_tracts.geojson")
    # gdf = preprocess_census_tract_boundaries_df(gdf)

    print("preprocessing")
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

def upload_state_boundaries_to_RDS():
    """ 
    """
    upload_geojsons_to_RDS(table_name = 'boundaries_state', preprocessing_func = preprocess_geojsons.preprocess_state_boundaries_df, single_geojson_path = "Shapefiles/state.geojson")

def upload_mpo_boundaries_to_RDS():
    """ 
    """
    upload_geojsons_to_RDS(table_name = 'boundaries_mpo', preprocessing_func = preprocess_geojsons.preprocess_mpo_boundaries_df, geojson_folder_path = "Shapefiles/mpo_boundaries_by_state/")

def upload_county_boundaries_to_RDS():
    """ 
    """
    upload_geojsons_to_RDS(table_name = 'boundaries_county', preprocessing_func = preprocess_geojsons.preprocess_county_boundaries_df, geojson_folder_path = "Shapefiles/county_by_state/")

def upload_census_tract_boundaries_to_RDS():
    """
    """
    uploaded_already = ["Shapefiles/census_tracts_by_state/census_tract_NE.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_IN.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_NY.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_DE.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_Northern Mariana Islands.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_American Samoa.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_SC.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_NM.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_UT.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_ND.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_CO.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_Guam.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_Virgin Islands.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_WY.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_AK.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_ID.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_PR.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_MI.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_OR.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_RI.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_GA.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_IL.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_LA.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_MA.geojson", 
    "Shapefiles/census_tracts_by_state/census_tract_MT.geojson", ]
    # Drop the table if it already exists
    # if 'boundaries_census_tract' in table_names:
    #     query = "DROP TABLE {}".format('boundaries_census_tract')
    #     cursor.execute(query)
    #     print("Dropped {} since it already exists ".format('boundaries_census_tract'))

    # processed_paths = []
    processed_paths = open("processed_census_tract_paths.txt", "w")

    # Deal with census tracts separately
    geojson_paths = helper.get_all_filenames(path = "Shapefiles/census_tracts_by_state", pattern = '*.geojson')
    print("got all geojson paths")

    print(len(geojson_paths))
    for i, path in enumerate(geojson_paths):
        if path not in uploaded_already:
            upload_geojsons_to_RDS(table_name = 'boundaries_census_tract_v3', preprocessing_func = preprocess_geojsons.preprocess_census_tract_boundaries_df, single_geojson_path = path, drop_exisiting_table = False)
            print("uploaded: ", path)
            processed_paths.write(path)
            processed_paths.write("\n")
        # processed_paths.append(path)
    
    print("PROCESSED PATHS: ", processed_paths)
    processed_paths.close()


if __name__=="__main__":

    
    # upload_FARS_data_to_RDS()
    # upload_SDS_data_to_RDS()
    # upload_Justice40_data_to_RDS()
    # upload_states_to_RDS()
    
    # upload_state_boundaries_to_RDS()
    # upload_mpo_boundaries_to_RDS()
    # upload_county_boundaries_to_RDS()
    upload_census_tract_boundaries_to_RDS()


