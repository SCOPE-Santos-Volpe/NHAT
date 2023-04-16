""" Resources:
https://www.geeksforgeeks.org/how-to-insert-a-pandas-dataframe-to-an-existing-postgresql-table/
https://blog.devgenius.io/3-easy-ways-to-import-a-shapefile-into-a-postgresql-database-c1a4c78104af
https://stackoverflow.com/questions/38361336/write-geodataframe-into-sql-database
https://gis.stackexchange.com/questions/239198/adding-geopandas-dataframe-to-postgis-table
https://gis.stackexchange.com/questions/325415/writing-geopandas-data-frame-to-postgis

NOTE: this file must be run in the home directory Santos-Volpe-SCOPE-Project
NOTE: Version of SQLAlchemy version needs to be 1.4.47
Run: pip install sqlalchemy==1.4.47
"""

# Import libraries
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import itertools

from geoalchemy2 import Geometry
import psycopg2

from config.config import config

import os, sys
# To import helper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helper
import preprocess_geojsons
from pathlib import Path
import preprocess_utils

# Establish sqlalchemy connection
sqlalchemy_conn = preprocess_utils.connect_to_sqlalchemy()

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

testing = True

def upload_FARS_data_to_RDS(path='FARS/FARS_w_MPO_County_Identifiers.csv'):
    """Uploads processed, cleaned, and labeled FARS data to RDS.

    Args:
        path: a string defining where the processed FARS data is

    Returns:
        None
    """
    if(testing):
        table_name = "test"
    else:
        table_name = "FARS"
    # Create FARS dataframe
    # fars = helper.load_df_from_csv(path='combined_FARS_preprocessed.csv', low_memory = False)
    fars = helper.load_df_from_csv(path=path, low_memory = False)

    # Load the FARS data into AWS RDS
    fars.to_sql(table_name, con=sqlalchemy_conn, if_exists='replace',
            index=False)
    print("uploaded FARS data")

def upload_SDS_data_to_RDS(path = 'SDS/Output_w_MPO_County_Identifiers/'):
    """Uploads the combined and processed SDS data to RDS. Currently, each state is in a separate table.

    Args:
        path: a string defining where the folder containing all of the processed SDS data is

    Returns:
        None
    """
    # Get all processed SDS
    all_csvs = helper.get_all_csv_filenames(path = path)
    print("Full list of states: " + str(all_csvs))

    # Process each state's crash data one by one
    for csv in all_csvs:
        # Get state name and state initial
        state_name = Path(csv).stem
        
        sds = helper.load_df_from_csv(path = csv, low_memory = False)
        # sds = helper.load_gdf_from_geojson(geojson_path) 
        # sds = preprocess_geojsons.change_gdf_geometry_to_geom()

        # Upload SDS data into AWS RDS
        if(testing):
            sds.to_sql("test", con=sqlalchemy_conn, if_exists='replace', index=False)
        else:
            sds.to_sql('SDS_'+state_name, con=sqlalchemy_conn, if_exists='replace', index=False)
        print("uploaded " + state_name + " SDS data.")

def upload_Justice40_data_to_RDS(path = "Justice40/justice_40_communities_clean.csv"):
    """Uploads the cleaned and processed Justice40 data to RDS.

    Args:
        path: a string defining where the cleaned Justice40 data csv is

    Returns:
        None
    """
    if(testing):
        table_name = "test"
    else:
        table_name = "Justice40"
    justice40 = helper.load_df_from_csv(path = path, low_memory = False)
    # justice40 = preprocess_Justice40_data.preprocess_justice40_data(justice40)
    
    # Load the FARS data into AWS RDS
    justice40.to_sql(table_name, con=sqlalchemy_conn, if_exists='replace',
            index=False)
    print("uploaded justice40 data")

def upload_states_to_RDS(path = 'states.csv'):
    """Uploads the state information to RDS.

    Args:
        path: a string defining where the states.csv file is

    Returns:
        None
    """
    if(testing):
        table_name = "test"
    else:
        table_name = "states"
    # Load state.csv data
    states = helper.load_df_from_csv(path=path, low_memory = False)
    # Load the FARS data into AWS RDS
    states.to_sql(table_name, con=sqlalchemy_conn, if_exists='replace',
            index=False)
    print("uploaded states data")

def upload_geojsons_to_RDS(table_name, preprocessing_func, path = None, drop_exisiting_table = True):
    """Uploads shapefiles to RDS.

    Args:
        table_name: the table name of the RDS to upload into
        preprocessing_func: the function to call to preprocess the data
        path: the path to be passed into preprocessing_func(). Default is None.
        drop_existing_table: a boolean defining whether to drop an existing table called table_name. Default is True.

    Returns:
        None
    """
    # Drop the table if it already exists
    if table_name in table_names and drop_exisiting_table:
        query = "DROP TABLE {}".format(table_name)
        cursor.execute(query)
        print("Dropped {} since it already exists ".format(table_name))

    gdf = preprocess_geojsons.combine_geojsons_to_single_gdf(path)
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

def upload_state_boundaries_to_RDS(path = "Shapefiles/state.geojson"):
    """Uploads the state boundaries to RDS.

    Args:
        path: a string containing the path to the state boundaries geojson

    Returns:
        None
    """
    if(testing):
        table_name = "test"
    else:
        table_name = "boundaries_state"
    upload_geojsons_to_RDS(table_name = table_name, preprocessing_func = preprocess_geojsons.preprocess_state_boundaries_df, path = path)

def upload_mpo_boundaries_to_RDS(path = "Shapefiles/mpo_boundaries_by_state/"):
    """Uploads the MPO boundaries to RDS.

    Args:
        path: a string containing the path to the MPO boundaries geojson

    Returns:
        None
    """
    if(testing):
        table_name = "test"
    else:
        table_name = "boundaries_mpo"
    upload_geojsons_to_RDS(table_name = table_name, preprocessing_func = preprocess_geojsons.preprocess_mpo_boundaries_df, path = path)

def upload_county_boundaries_to_RDS(path = "Shapefiles/county_by_state/"):
    """Uploads the county boundaries to RDS.

    Args:
        path: a string containing the path to the county boundaries geojson

    Returns:
        None
    """
    if(testing):
        table_name = "test"
    else:
        table_name = "boundaries_county"
    upload_geojsons_to_RDS(table_name = table_name, preprocessing_func = preprocess_geojsons.preprocess_county_boundaries_df, path = path)

def upload_census_tract_boundaries_to_RDS(path = "Shapefiles/census_tracts_by_state"):
    """Uploads the census boundaries to RDS.

    Args:
        path: a string containing the path to the folder containing a census tracts geojson for each state

    Returns:
        None
    """
    if(testing):
        table_name = "test"
    else:
        table_name = "boundaries_census_tract_v3"


    # Deal with census tracts separately
    geojson_paths = helper.get_all_filenames(path = path, pattern = '*.geojson')
    print("got all geojson paths")

    print(len(geojson_paths))
    for _, path in enumerate(geojson_paths):
        upload_geojsons_to_RDS(table_name = table_name, preprocessing_func = preprocess_geojsons.preprocess_census_tract_boundaries_df, single_geojson_path = path, drop_exisiting_table = False)
        print("uploaded: ", path)



if __name__=="__main__":


    upload_FARS_data_to_RDS()
    # upload_SDS_data_to_RDS()
    # upload_Justice40_data_to_RDS()
    # upload_states_to_RDS()

    # upload_state_boundaries_to_RDS()
    # upload_mpo_boundaries_to_RDS()
    # upload_county_boundaries_to_RDS()
    # upload_census_tract_boundaries_to_RDS()


