import helper
import pandas as pd
import geopandas as gpd

states_df = helper.load_df_from_csv(path='states.csv', low_memory = False)
# Dictionaries to convert the STATE_INITIAL to STATE_ID & STATE_NAME
d_state_initial2id = dict(zip(states_df.state, states_df.id))
d_state_initial2name = dict(zip(states_df.state, states_df.name))
d_state_id2name = dict(zip(states_df.id, states_df.name))
d_state_name2id = dict(zip(states_df.name, states_df.id))
d_state_name2initial = dict(zip(states_df.name, states_df.state))


convert_column_type_dict = {"YEAR"              : int, 
                            "IS_FATAL"          : int, 
                            "SEVERITY"          : int, 
                            "IS_PED"            : int,  
                            "IS_CYC"            : int,
                            "WEATHER_COND"      : str, 
                            "LIGHT_COND"        : str, 
                            "ROAD_COND"         : str, 
                            "ROAD_NAME"         : str, 
                            "IS_INTERSECTION"   : int,
                            "LAT"               : float,
                            "LON"               : float,
                            }



def convert_columns_to_proper_types(df:pd.DataFrame) -> pd.DataFrame:
    """ Convert columns to the proper types
    """
    # Drop all lat lon that are not numberic
    # df = df[df.f.apply(lambda x: x.isnumeric())]
    df = df[pd.to_numeric(df['LAT'], errors='coerce').notnull()]
    df = df[pd.to_numeric(df['LON'], errors='coerce').notnull()]

    df = df.astype(convert_column_type_dict)

    print(df.dtypes)
    return df

def remove_invalid_lat_lon(df:pd.DataFrame) -> pd.DataFrame:
    """ Takes a preprocessed SDS data and remove points with invalid latitude and longitudes
    """
    # Valid lat and lon range
    lat_range = [-90, 90]
    lon_range = [-180, 180]

    print("LENGTH BEFORE DROPPING: ", df.shape[0])
    # Drop NAs
    df = df.dropna(subset=['LAT', 'LON'], how='all')
    print("LENGTH AFTER DROPPING NANS: ", df.shape[0])

    return df

def create_point_column_from_lat_lon(df: pd.DataFrame, flip_lon_sign = False) -> gpd.GeoDataFrame:
    """ Generate a Point geometry column using latitude and longitude
        We want to use this because then we can use shapely to determine 
        whether each of the points 
        
        Returns
            gdf: 
    """
    if flip_lon_sign:
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(-df['LON'], df['LAT']), crs="EPSG:4269")
    else:
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['LON'], df['LAT']), crs="EPSG:4269")

    return gdf
