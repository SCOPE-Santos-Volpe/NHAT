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

    # Create SDS dataframe for 
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
        # sds.to_sql('SDS_'+state, con=sqlalchemy_conn, if_exists='replace',
        #         index=False)
        print("uploaded " + state + " SDS data.")

def upload_geojsons_to_RDS(table_name, geojson_folder_path = None, single_geojson_path = None):
    """ Upload shapefiles to RDS
    """
    # print("table names:" ,table_names)
    # Drop the mpo table if it already exists
    if table_name in table_names:
        query = "DROP TABLE {}".format(table_name)
        cursor.execute(query)
        print("Dropped {} since it already exists ".format(table_name))

    # Get list of all MPO geojsons paths
    if single_geojson_path is not None:
        geojson_paths = [single_geojson_path]
    else:
        geojson_paths = helper.get_all_filenames(path = geojson_folder_path, pattern = '*.geojson')

    # List to store MultiPolygon rows. Rows with type MultiPolygon need to be separated 
    # from polygon because they require different methods to be pushed to the database.
    multipolygon_list = []

    for geojson_path in geojson_paths:
        gdf = helper.load_gdf_from_geojson(geojson_path)     # load geojson into a geodataframe
        
        for i, row in gdf.iterrows():                        # Loop through the gdf and separate out rows where Geometry is MultiPolygon
            type = str(row['geometry'].geom_type)
            if (type != "Polygon"):
                multipolygon_list.append(row)
                gdf.drop(i, inplace=True)

        # Change geometry column to geom
        gdf['geom'] = gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=4269))
        gdf.drop('geometry', 1, inplace=True)
        # multipoly_gdf.rename(columns={"STATE": "state_id", "NAME": "sta"})
        # Change STATE_ID column type to int
        gdf['STATE'] = gdf['STATE'].astype(str).astype(int)
        # print("DTYPES: ", gdf.dtypes)

        gdf.to_sql(table_name, con=sqlalchemy_conn, if_exists='append', index=False, dtype={'geom': Geometry(geometry_type='POLYGON', srid=4269)})
        
    # Alter table so that the geom column accepts any type
    query = "ALTER TABLE {} ALTER COLUMN geom TYPE geometry(Geometry,4269);".format(table_name)
    cursor.execute(query)
    # cursor.execute("""ALTER TABLE (%s,) ALTER COLUMN geom TYPE geometry(Geometry,4269);""", (table_name,))

    # Convert multipolygon list to gpd and upload to database. 
    multipoly_gdf = gpd.GeoDataFrame(multipolygon_list)
    multipoly_gdf['geom'] = multipoly_gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=4269))
    multipoly_gdf.drop('geometry', 1, inplace=True)
    
    multipoly_gdf['STATE'] = multipoly_gdf['STATE'].astype(str).astype(int)

    multipoly_gdf.to_sql(table_name, con=sqlalchemy_conn, if_exists='append', index=False, dtype={'geom': Geometry(geometry_type='MULTIPOLYGON', srid=4269)})
    
    # gdf.to_postgis(table_name, con=sqlalchemy_conn, if_exists='replace', index=False)
    print("uploaded {} table to RDS".format(table_name))

def upload_states_to_RDS():
    # Load state.csv data
    states = helper.load_df_from_csv(path='states.csv', low_memory = False)
    # Load the FARS data into AWS RDS
    states.to_sql('states', con=sqlalchemy_conn, if_exists='replace',
            index=False)
    print("uploaded states data")


if __name__=="__main__":

    # Drop the mpo table if it already exists
    # cursor.execute("DROP TABLE boundaries_mpo")

    # upload_FARS_data_to_RDS()
    # upload_SDS_data_to_RDS()
    upload_states_to_RDS()

    # upload_geojsons_to_RDS(table_name = 'boundaries_state', single_geojson_path = "Shapefiles/state.geojson")
    # upload_geojsons_to_RDS(table_name = 'boundaries_mpo', geojson_folder_path = "Shapefiles/mpo_boundaries_by_state/")
    # upload_geojsons_to_RDS(table_name = 'boundaries_county', geojson_folder_path = "Shapefiles/county_by_state/")

    # sql = """ SELECT * FROM "boundaries_mpo_AK" """
    # df = gpd.read_postgis(sql, con=sqlalchemy_conn)  
    # print (df)