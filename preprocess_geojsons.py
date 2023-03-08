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

def combine_geojsons_to_single_gdf(geojson_folder_path = None, single_geojson_path = None):

    # Get list of all geojsons paths
    if single_geojson_path is not None:
        geojson_paths = [single_geojson_path]
    else:
        geojson_paths = helper.get_all_filenames(path = geojson_folder_path, pattern = '*.geojson')

    # Combine all geojsons in the folder
    gdf_list = []
    for geojson_path in geojson_paths:
        single_gdf = helper.load_gdf_from_geojson(geojson_path)     # load geojson into a geodataframe
        gdf_list.append(single_gdf)
    gdf = pd.concat(gdf_list)

    return gdf


def separate_gdf_into_polygon_multipolygon(gdf: gpd.GeoDataFrame):
    """
    Separate gdf into gdfs with just polgons or multipolygons and change geometry
    """

    # Loop through the gdf and separate out rows where Geometry is MultiPolygon. 
    # Rows with type MultiPolygon need to be separated from polygon because they 
    # require different methods to be pushed to the database.
    multipolygon_list = []
    for i, row in gdf.iterrows():
        type = str(row['geometry'].geom_type)
        if (type != "Polygon"):
            multipolygon_list.append(row)
            gdf.drop(i, inplace=True)
    multipoly_gdf = gpd.GeoDataFrame(multipolygon_list)

    # Change geometry column to geom
    gdf['geom'] = gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=4269))
    gdf.drop('geometry', 1, inplace=True)
    multipoly_gdf['geom'] = multipoly_gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=4269))
    multipoly_gdf.drop('geometry', 1, inplace=True)

    return gdf, multipoly_gdf


def preprocess_state_boundaries_df(gdf: gpd.GeoDataFrame):
    """
    """
    # Change STATE_ID column type to int
    gdf['STATE'] = gdf['STATE'].astype(str).astype(int)
    gdf = gdf.rename(columns = {"STATE": "STATE_ID", "NAME": "STATE_NAME"})
    gdf = gdf.drop(columns=['LSAD', 'GEO_ID', 'CENSUSAREA'])
    # NOTE: DOESN'T HAVE STATE_INITIAL
    print(gdf.columns)
    return gdf

def preprocess_mpo_boundaries_df(gdf: gpd.GeoDataFrame ):
    """
    """
    gdf = gdf.drop(columns=['ID', 'AREA', 'DATA', 'MPO_ID'])
    gdf = gdf.rename(columns={"STATE": "STATE_INITIAL",})

    gdf['STATE_ID'] = gdf['STATE_INITIAL'].map(d_state_initial2id)
    gdf['STATE_NAME'] = gdf['STATE_INITIAL'].map(d_state_initial2name)
    gdf = gdf[['MPO_NAME', 'STATE_ID', 'STATE_NAME', 'geometry']]

    print(gdf.columns)
    return gdf

def preprocess_county_boundaries_df(gdf: gpd.GeoDataFrame ):
    """
    """
    gdf = gdf.drop(columns=['COUNTYNS', 'COUNTYFP', 'AFFGEOID', 'GEOID', 'LSAD', 'ALAND', 'AWATER'])
    gdf = gdf.rename(columns={"STATEFP": "STATE_ID",})

    gdf['STATE_NAME'] = gdf['STATE_ID'].map(d_state_id2name)
    # gdf = gdf[['MPO_NAME', 'STATE_ID', 'STATE_NAME', 'geometry']]

    print(gdf.columns)
    return gdf

if __name__ == "__main__":
    # gdf = combine_geojsons_to_single_gdf(single_geojson_path = "Shapefiles/state.geojson")
    # gdf = preprocess_state_boundaries_df(gdf)

    gdf = combine_geojsons_to_single_gdf(geojson_folder_path = "Shapefiles/county_by_state/")
    gdf = preprocess_county_boundaries_df(gdf)

    # gdf = combine_geojsons_to_single_gdf(geojson_folder_path = "Shapefiles/mpo_boundaries_by_state/")
    # gdf = preprocess_mpo_boundaries_df(gdf)
    print(gdf.head)

