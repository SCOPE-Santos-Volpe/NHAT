"""
Preprocess geojsons bc they are ugly
"""
import pandas as pd
import helper

def combine_geojsons_to_single_df(geojson_folder_path = None, single_geojson_path = None):

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

    # Loop through the gdf and separate out rows where Geometry is MultiPolygon. 
    # Rows with type MultiPolygon need to be separated from polygon because they 
    # require different methods to be pushed to the database.
    multipolygon_list = []
    for i, row in gdf.iterrows():
        type = str(row['geometry'].geom_type)
        if (type != "Polygon"):
            multipolygon_list.append(row)
            gdf.drop(i, inplace=True)
    multipoly_gdf = gdf.GeoDataFrame(multipolygon_list)

    return gdf, multipoly_gdf
