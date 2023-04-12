import geopandas as gpd

def load_gdf_from_geojson(path:str, **kwargs) -> gpd.GeoDataFrame:
    """Loads a geodataframe from the geojson at `path`.

    Args:
        path: A string containing the path to a .csv file
        **kwargs: Pass through other arguments to pd.read_csv

    Returns:
        A GeoDataFrame loaded from the .geojson
    """
    gdf = gpd.read_file(path)
    # print(gdf)

    # Drop nulls in the geometry column
    # print('Dropping ' + str(gdf.geometry.isna().sum()) + ' nulls.')
    gdf = gdf.dropna(subset=['geometry'])

    return gdf


if __name__ == "__main__":

    # QUICK FIX: GET ALAMEDA BOUNDARY TO PLAY WITH
    # SAM: DON'T COMMENT THIS IN BC I DONT THINK U HAVE THE DATABASE CONNECTION YET
    # state_id = 6
    # print("Getting ALEMEDA COUNTY for state_id: ", state_id)
    # sql = text(""" SELECT * FROM "boundaries_county" WHERE "STATE_ID" = 6 AND "COUNTY_NAME" = 'Alameda' """)
    # boundaries = gpd.read_postgis(sql, con=sqlalchemy_conn)
    # boundaries.to_file('Shapefiles/Alameda.geojson', driver='GeoJSON')  



    gpd = load_gdf_from_geojson("Shapefiles/Alameda.geojson")
    
    print(gpd)
    print(type(gpd.geometry[0]))