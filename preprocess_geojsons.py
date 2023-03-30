"""
Preprocess geojsons bc they are ugly
"""
import pandas as pd
import geopandas as gpd
from geoalchemy2 import Geometry, WKTElement
import helper

states_df = helper.load_df_from_csv(path='states.csv', low_memory = False)
# Dictionaries to convert the STATE_INITIAL to STATE_ID & STATE_NAME
d_state_initial2id = dict(zip(states_df.state, states_df.id))
d_state_initial2name = dict(zip(states_df.state, states_df.name))
d_state_id2name = dict(zip(states_df.id, states_df.name))
d_state_name2id = dict(zip(states_df.name, states_df.id))


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
    polygon_gdf['geom'] = polygon_gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=4269))
    polygon_gdf.drop(columns='geometry', axis=1, inplace=True)
    multipoly_gdf['geom'] = multipoly_gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=4269))
    multipoly_gdf.drop(columns='geometry', axis=1, inplace=True)

    return polygon_gdf, multipoly_gdf


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

    gdf['STATE_ID'] = gdf['STATE_INITIAL'].map(d_state_initial2id)
    gdf['STATE_NAME'] = gdf['STATE_INITIAL'].map(d_state_initial2name)
    gdf = gdf[['STATE_ID', 'STATE_NAME', 'MPO_ID', 'MPO_NAME', 'geometry']]

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

    gdf['STATE_NAME'] = gdf['STATE_ID'].map(d_state_id2name)
    gdf = gdf[['STATE_ID', 'STATE_NAME', 'COUNTY_ID', 'COUNTY_NAME', 'geometry']]

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

    gdf['STATE_ID'] = gdf['STATE_NAME'].map(d_state_name2id)
    gdf = gdf[['STATE_ID', 'STATE_NAME', 'COUNTY_NAME', 'CENSUS_TRACT_ID', 'geometry']]

    column_type_dict = {"STATE_ID"                      : float, 
                        "STATE_NAME"                    : str, 
                        "CENSUS_TRACT_ID"               : float, 
                        "COUNTY_NAME"                   : str,  
    }
    gdf = gdf.astype(column_type_dict)

    # Join census tract data with justice40 stats
    justice40 = helper.load_df_from_csv(path = "Justice40/justice_40_communities_clean.csv", low_memory = False)
    gdf = pd.merge(gdf,justice40[['CENSUS_TRACT_ID','IDENTIFIED_AS_DISADVANTAGED']],on='CENSUS_TRACT_ID', how='left')

    return gdf


if __name__ == "__main__":
    # gdf = combine_geojsons_to_single_gdf(single_geojson_path = "Shapefiles/state.geojson")
    # gdf = preprocess_state_boundaries_df(gdf)

    # gdf = combine_geojsons_to_single_gdf(geojson_folder_path = "Shapefiles/county_by_state/")
    # gdf = preprocess_county_boundaries_df(gdf)

    # gdf = combine_geojsons_to_single_gdf(geojson_folder_path = "Shapefiles/mpo_boundaries_by_state/")
    # gdf = preprocess_mpo_boundaries_df(gdf)

    gdf = combine_geojsons_to_single_gdf(single_geojson_path = "Shapefiles/census_tracts.geojson")
    gdf = preprocess_census_tract_boundaries_df(gdf)
    print("saving modified census tracts to file")
    # gdf.to_file('Shapefiles/clean_geojsons/census_tracts.geojson', driver='GeoJSON')  

    # helper.write_geodataframe_to_file(gdf, "filename")

    print(gdf)

    # polygon_gdf, multipolygon_gdf = separate_gdf_into_polygon_multipolygon(gdf)
    # print(polygon_gdf.head(10))

