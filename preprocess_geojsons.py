"""
Preprocess geojsons bc they are ugly
"""
import pandas as pd
import geopandas as gpd
from geoalchemy2 import Geometry, WKTElement
import helper
import math
import preprocess_utils

from shapely.geometry import Point, Polygon, MultiPolygon, shape
from sqlalchemy import create_engine, Table, Column, Integer, String, text

# Establish sqlalchemy connection
conn_string = 'postgresql://scope_team:greenTea123@database-1.ci75bfibgs4e.us-east-1.rds.amazonaws.com/FARS'
db = create_engine(conn_string)
sqlalchemy_conn = db.connect()
print('Python connected to PostgreSQL via Sqlalchemy')

def combine_geojsons_to_single_gdf(geojson_folder_path = None, single_geojson_path = None):

    # Get list of all geojsons paths
    if single_geojson_path is not None:
        geojson_paths = [single_geojson_path]
    else:
        geojson_paths = helper.get_all_filenames(path = geojson_folder_path, pattern = '*.geojson')

    # Combine all geojsons in the folder
    gdf_list = []
    for geojson_path in geojson_paths:
        print('loading df')
        single_gdf = helper.load_gdf_from_geojson(geojson_path)     # load geojson into a geodataframe
        gdf_list.append(single_gdf)
    gdf = pd.concat(gdf_list)

    print("got gdf")

    return gdf


def separate_gdf_into_polygon_multipolygon(gdf: gpd.GeoDataFrame):
    """
    Separate gdf into gdfs with just polgons or multipolygons and change geometry
    """

    # Rows with geometry type MultiPolygon need to be separated from Polygon because they 
    # require different methods to be pushed to the database.
    polygon_gdf = gpd.GeoDataFrame(gdf[gdf['geometry'].geom_type == "Polygon"])
    multipoly_gdf = gpd.GeoDataFrame(gdf[gdf['geometry'].geom_type == "MultiPolygon"])

    # Change geometry column to geom

    # polygon_gdf['geom'] = polygon_gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=4269))
    # polygon_gdf.drop(columns='geometry', axis=1, inplace=True)
    # multipoly_gdf['geom'] = multipoly_gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=4269))
    # multipoly_gdf.drop(columns='geometry', axis=1, inplace=True)

    # Trying to use a function
    polygon_gdf = change_gdf_geometry_to_geom(polygon_gdf)
    multipoly_gdf = change_gdf_geometry_to_geom(multipoly_gdf)

    return polygon_gdf, multipoly_gdf

def change_gdf_geometry_to_geom(gdf: gpd.GeoDataFrame):
    """
    """
    gdf['geom'] = gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=4269))
    gdf.drop(columns='geometry', axis=1, inplace=True)
    return gdf

def preprocess_state_boundaries_df(gdf: gpd.GeoDataFrame):
    """
    """
    # Change STATE_ID column type to int
    gdf['STATE'] = gdf['STATE'].astype(str).astype(int)
    gdf = gdf.rename(columns = {"STATE": "STATE_ID", 
                                "NAME": "STATE_NAME"})
    gdf = gdf.drop(columns=['LSAD', 'GEO_ID', 'CENSUSAREA'])
    # NOTE: DOESN'T HAVE STATE_INITIAL
    print(gdf.columns)
    return gdf

def preprocess_mpo_boundaries_df(gdf: gpd.GeoDataFrame ):
    """
    """
    gdf = gdf.drop(columns=['ID', 'AREA', 'DATA'])
    gdf = gdf.rename(columns={ "STATE": "STATE_INITIAL"})

    gdf['STATE_ID'] = gdf['STATE_INITIAL'].map(preprocess_utils.d_state_initial2id)
    gdf['STATE_NAME'] = gdf['STATE_INITIAL'].map(preprocess_utils.d_state_initial2name)
    gdf = gdf[['STATE_ID', 'STATE_NAME', 'MPO_ID', 'MPO_NAME', 'geometry']]

    convert_column_type_dict = {"STATE_ID"            : int, 
                                "STATE_NAME"          : str, 
                                "MPO_ID"              : int, 
                                "MPO_NAME"            : str
    }
    gdf = gdf.astype(convert_column_type_dict)

    print(gdf.columns)
    return gdf

def preprocess_county_boundaries_df(gdf: gpd.GeoDataFrame ):
    """
    """
    gdf = gdf.drop(columns=['COUNTYNS', 'AFFGEOID', 'GEOID', 'LSAD', 'ALAND', 'AWATER'])
    gdf = gdf.rename(columns={  "STATEFP": "STATE_ID", 
                                "NAME": "COUNTY_NAME",
                                "COUNTYFP" : "COUNTY_ID"
                            })
    gdf['STATE_ID'] = gdf['STATE_ID'].astype(str).astype(int)

    gdf['STATE_NAME'] = gdf['STATE_ID'].map(preprocess_utils.d_state_id2name)
    gdf = gdf[['STATE_ID', 'STATE_NAME', 'COUNTY_ID', 'COUNTY_NAME', 'geometry']]

    convert_column_type_dict = {"STATE_ID"            : int, 
                                "STATE_NAME"          : str, 
                                "COUNTY_ID"           : int, 
                                "COUNTY_NAME"         : str
    }
    gdf = gdf.astype(convert_column_type_dict)

    print(gdf.columns)
    return gdf

def preprocess_census_tract_boundaries_df(gdf: gpd.GeoDataFrame ):
    """
    """
    renames = {
        'SF' : 'STATE_NAME',
        'CF' : 'COUNTY_NAME',
        'GEOID10' : 'CENSUS_TRACT_ID'
    }
    gdf.rename(columns = renames,inplace = True)


    gdf['STATE_ID'] = gdf['STATE_NAME'].map(preprocess_utils.d_state_name2id)
    
    # Convert the state ids that are NAN to 0 - these are gonna be the islands
    def convert_invalid_state_ids_to_0(row):
        if row['STATE_ID'] is None or math.isnan(row['STATE_ID']):
            return 0
        else:
            return row['STATE_ID']
    gdf['STATE_ID'] = gdf.apply(lambda row: convert_invalid_state_ids_to_0(row), axis=1)

    # print("unique state_ids: ", gdf['STATE_ID'].unique())
    gdf = gdf[['STATE_ID', 'STATE_NAME', 'COUNTY_NAME', 'CENSUS_TRACT_ID', 'geometry']]
    # Make sure column types are correct
    column_type_dict = {"STATE_ID"                      : int, 
                        "STATE_NAME"                    : str, 
                        "CENSUS_TRACT_ID"               : int, 
                        "COUNTY_NAME"                   : str,  
    }
    gdf = gdf.astype(column_type_dict)

    # Remove the str "County" from each entry in the county column
    def remove_county_str(row):
            return row['COUNTY_NAME'].rsplit(' ', 1)[0]
    gdf['COUNTY_NAME'] = gdf.apply(lambda row: remove_county_str(row), axis=1)

    state_id = gdf['STATE_ID'][0]
    
    # Add County ID to each row
    def set_county_id(row):
        if state_id != 0: 
            county_name = row['COUNTY_NAME']
            # If county name is
            if "'" in county_name:
                county_name = county_name.replace("'", "''")
            # print("Getting COUNTY boundaries for state_id: ", state_id, ", county: ", county_name)
            sql = text(""" SELECT * FROM "boundaries_county" WHERE "STATE_ID" = {} AND "COUNTY_NAME" = '{}' LIMIT 1 """.format(state_id, county_name))
            county_boundaries = gpd.read_postgis(sql, con=sqlalchemy_conn)
            if not county_boundaries.empty:
                county_id = county_boundaries['COUNTY_ID'][0]
            else:
                county_id = None
        else:
            county_id = None   
        return county_id
    gdf['COUNTY_ID'] = gdf.apply(lambda row: set_county_id(row), axis=1)

    # Join census tract data with MPO data
    if state_id != 0: 
        # Get MPO boundaries for this state    
        print("Getting all MPO boundaries for state_id: ", state_id)
        sql = text(""" SELECT * FROM "boundaries_mpo" WHERE "STATE_ID" = {} """.format(state_id))
        mpo_boundaries = gpd.read_postgis(sql, con=sqlalchemy_conn)
        print("Got all MPO boundaries")

        # Perform spatial join between MPO boundaries and county boundaries
        gdf = gdf.to_crs(4269)
        gdf = gpd.sjoin(gdf,mpo_boundaries, predicate='intersects', how='left')

        columns = ['STATE_ID_left', 'STATE_NAME_left', 'COUNTY_ID', 'COUNTY_NAME', 'MPO_ID', 'MPO_NAME', 'CENSUS_TRACT_ID', 'geometry']
        gdf = gdf[columns]

        # Rename some columns
        renames = {
            'STATE_ID_left' : 'STATE_ID',
            'STATE_NAME_left' : 'STATE_NAME',
        }
        gdf.rename(columns = renames,inplace = True)
    else:
        def set_to_none(row):
            return None
        gdf['MPO_ID'] = gdf.apply(lambda row: set_to_none(row), axis=1)
        gdf['MPO_NAME'] = gdf.apply(lambda row: set_to_none(row), axis=1)
        columns = ['STATE_ID', 'STATE_NAME', 'COUNTY_ID', 'COUNTY_NAME', 'MPO_ID', 'MPO_NAME', 'CENSUS_TRACT_ID', 'geometry']
        gdf = gdf[columns]

    # Join census tract data with justice40 stats
    justice40 = helper.load_df_from_csv(path = "Justice40/justice_40_communities_clean.csv", low_memory = False)
    gdf = pd.merge(gdf,justice40[['CENSUS_TRACT_ID','IDENTIFIED_AS_DISADVANTAGED']],on='CENSUS_TRACT_ID', how='left')

    print(gdf.head)

    return gdf

def preprocess_HIN_df(gdf: gpd.GeoDataFrame):
    # gdf = gdf.drop(columns=['COUNTYNS', 'AFFGEOID', 'GEOID', 'LSAD', 'ALAND', 'AWATER'])
    # gdf = gdf.rename(columns={  "STATEFP": "STATE_ID", 
    #                             "NAME": "COUNTY_NAME",
    #                             "COUNTYFP" : "COUNTY_ID"
    #                         })
    # gdf['STATE_ID'] = gdf['STATE_ID'].astype(str).astype(int)

    # gdf['STATE_NAME'] = gdf['STATE_ID'].map(preprocess_utils.d_state_id2name)
    # gdf = gdf[['STATE_ID', 'STATE_NAME', 'COUNTY_ID', 'COUNTY_NAME', 'geometry']]

    # convert_column_type_dict = {"STATE_ID"            : int, 
    #                             "STATE_NAME"          : str, 
    #                             "COUNTY_ID"           : int, 
    #                             "COUNTY_NAME"         : str
    # }
    # gdf = gdf.astype(convert_column_type_dict)

    print(gdf.columns)
    return gdf


if __name__ == "__main__":
    # gdf = combine_geojsons_to_single_gdf(single_geojson_path = "Shapefiles/state.geojson")
    # gdf = preprocess_state_boundaries_df(gdf)

    # gdf = combine_geojsons_to_single_gdf(geojson_folder_path = "Shapefiles/county_by_state/")
    # gdf = preprocess_county_boundaries_df(gdf)

    # gdf = combine_geojsons_to_single_gdf(geojson_folder_path = "Shapefiles/mpo_boundaries_by_state/")
    # gdf = preprocess_mpo_boundaries_df(gdf)

    # gdf = combine_geojsons_to_single_gdf(single_geojson_path = "Shapefiles/census_tracts_by_state/census_tract_CO.geojson")
    # gdf = preprocess_census_tract_boundaries_df(gdf)
    # print("saving modified census tracts to file")
    # gdf.to_file('Shapefiles/clean_geojsons/census_tracts.geojson', driver='GeoJSON')  

    # helper.write_geodataframe_to_file(gdf, "filename")

    gdf = combine_geojsons_to_single_gdf(single_geojson_path = "Shapefiles/HIN/alameda_000_threshold_hin.geojson")
    print(gdf.head)
    # gdf = preprocess_HIN_df(gdf)


    # print(gdf)

    # polygon_gdf, multipolygon_gdf = separate_gdf_into_polygon_multipolygon(gdf)
    # print(polygon_gdf.head(10))

