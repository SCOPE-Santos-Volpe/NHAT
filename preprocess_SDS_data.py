"""Combines all .csv datasets for each folder (intended for SDS data) into 1 `pd.DataFrame` per folder, cleans it, and writes to a single .csv file per folder.

Main function is `preprocess_SDS_datasets`. Helper functions collect all SDS data, clean it, and categorize it by county and MPO.

https://massdot-impact-crashes-vhb.opendata.arcgis.com/datasets/MassDOT::2021-crashes/about

        * Using 10-15 attributes -> will provide the list
        1. Fatal / serious injury (FSI)
        * We care about the severity of the crash
        2. Date / time is important
        3. Lighting is big attribute because we work on road lighting
        4. Corridor level data (function of the road/road type, intersection related)
        5. Involvement Binary (yes/no) attribute -> pedestrian involved? Bicyclist involved?
        6. Aggressive driving, failure to yield, vehicle left the roadway


Desired columns:
    YEAR : int
    IS_FATAL :          int (one-hot)
    SEVERITY :          int (1-4 range)
        1 - Fatal
        2 - Injury (Severe)
        3 - Injury (Other Visible)
        4 - Injury (Complaint of Pain)
        0 - PDO
    IS_PED :            int (one-hot)
    IS_CYC :            int (one-hot)
    WEATHER_COND :      int (1-4 range)
        A - Clear
        B - Cloudy
        C - Rain
        D - Snow / Sleet / Hail
        E - Fog / Smog / Smoke
        -  - Other
    LIGHT_COND :        int (1-4 range)
        A - Daylight
        B - Dusk - Dawn
        C - Dark - Street Lights
        D - Dark - No Street Lights
        E - Dark - Unknown Street Lights
        -  - Other
    ROAD_COND :         int (1-4 range)
        A - Dry
        B - Wet / Water
        C - Snowy / Icy / Slush
        D - Slippery (Muddy, Oily, etc.)
        -  - Not Stated
    ROAD_NAME :         str 
    # ROAD_TYPE :         int (functional class)
    # VEHC_DIR :          char (E/W/N/S)
    IS_INTERSECTION :   int (one-hot)
    LAT:                int
    LON:                int


"""

import pandas as pd
import geopandas as gpd
import helper
import preprocess_utils
from sqlalchemy import create_engine, text

# Establish sqlalchemy connection
conn_string = 'postgresql://scope_team:greenTea123@database-1.ci75bfibgs4e.us-east-1.rds.amazonaws.com/FARS'
db = create_engine(conn_string)
sqlalchemy_conn = db.connect()


def preprocess_MA_SDS(df:pd.DataFrame) -> pd.DataFrame:
    """Preprocess the Massachussetts SDS data.

    Args:
        df: a `pd.DataFrame` containing the MA SDS data

    Returns:
        A `pd.DataFrame` containing the preprocessed MA SDS data
    """


    columns = [ 'YEAR',                                                         # Metadata
                'MAX_INJR_SVRTY_CL', 'NUMB_FATAL_INJR', 'NUMB_NONFATAL_INJR',   # Injury level
                'AMBNT_LIGHT_DESCR', 'WEATH_COND_DESCR', 'ROAD_SURF_COND_DESCR', # Accident conditions
                'RDWY', 'RDWY_JNCT_TYPE_DESCR', 'F_CLASS', 'F_F_CLASS',         # Road type
                'LAT', 'LON',                                                   # Geolocation
                'NON_MTRST_TYPE_CL', 'NON_MTRST_ACTN_CL', 'NON_MTRST_LOC_CL',   # Parties involved
    ]
    df = df[columns]

    # Make sure columns are string types
    types = {
        'WEATH_COND_DESCR': str,
        'NON_MTRST_TYPE_CL': str,
        'ROAD_SURF_COND_DESCR': str,
        'RDWY_JNCT_TYPE_DESCR': str,
        'MAX_INJR_SVRTY_CL': str
    }
    df = df.astype(types)
    # df['WEATH_COND_DESCR'] = df['WEATH_COND_DESCR'].astype(str)
    # df['NON_MTRST_TYPE_CL'] = df['NON_MTRST_TYPE_CL'].astype(str)
    # df['ROAD_SURF_COND_DESCR'] = df['ROAD_SURF_COND_DESCR'].astype(str)
    # df['RDWY_JNCT_TYPE_DESCR'] = df['RDWY_JNCT_TYPE_DESCR'].astype(str)
    # df['MAX_INJR_SVRTY_CL'] = df['MAX_INJR_SVRTY_CL'].astype(str)

    renames = {
        'RDWY' : 'ROAD_NAME',
    }
    df = df.rename(columns = renames)

    # Create appropriate columns to match format specified at start of this file

    def is_fatal(row):
        if row['NUMB_FATAL_INJR'] > 0:
            return 1
        return 0
    df['IS_FATAL'] = df.apply(lambda row: is_fatal(row), axis=1)

    def severity(row):
        """
            1 - Fatal
            2 - Injury (Severe)
            3 - Injury (Other Visible)
            4 - Injury (Complaint of Pain)
            0 - PDO
        """
        severity_str = row['MAX_INJR_SVRTY_CL']
        if "No injury" in severity_str or "No Apparent Injury (O)" in severity_str:
            return 0
        elif "Non-fatal injury - Possible" in severity_str or "Non-fatal injury - Non-incapacitating" in severity_str or "Suspected Minor Injury" in severity_str :
            return 4
        elif "Possible Injury" in severity_str or "Non-fatal injury - Incapacitating" in severity_str:
            return 3
        elif "Suspected Serious Injury" in severity_str:
            return 2
        elif "Fatal injury" in severity_str:
            return 1
        return 0
    df['SEVERITY'] = df.apply(lambda row: severity(row), axis=1)

    def is_ped(row: pd.Series):
        if "Pedestrian" in row['NON_MTRST_TYPE_CL']:
            return 1
        return 0
    df['IS_PED'] = df.apply(lambda row: is_ped(row), axis=1)

    def is_cyc(row: pd.Series):
        if "Cyclist" in row['NON_MTRST_TYPE_CL']:
            return 1
        return 0
    df['IS_CYC'] = df.apply(lambda row: is_cyc(row), axis=1)

    def is_intersection(row: pd.Series):
        junction_str = row['RDWY_JNCT_TYPE_DESCR'].lower()
        if "intersection" in junction_str:
            return 1
        return 0
    df['IS_INTERSECTION'] = df.apply(lambda row: is_intersection(row), axis=1)

    def weather_cond(row: pd.Series):
        weather_str = row['WEATH_COND_DESCR'].lower()
        if "fog" in weather_str or "smog" in weather_str or "smoke" in weather_str:
            return "E"
        elif "snow" in weather_str or "sleet" in weather_str or "hail" in weather_str:
            return "D"
        elif "rain" in weather_str:
            return "C"
        elif "cloudy" in weather_str:
            return "B"
        elif "clear" in weather_str:
            return "A"
        else:
            return "-"
    df['WEATHER_COND'] = df.apply(lambda row: weather_cond(row), axis=1)

    def light_cond(row: pd.Series):
        light_str = row['AMBNT_LIGHT_DESCR'].lower()
        if "daylight" in light_str:
            return "A"
        elif "dusk" in light_str or "dawn" in light_str:
            return "B"
        elif "dark - lighted roadway" in light_str:
            return "C"
        elif "dark - roadway not lighted" in light_str:
            return "D"
        elif "dark - unknown roadway lighting" in light_str:
            return "E"
        else:
            return "-"
    df['LIGHT_COND'] = df.apply(lambda row: light_cond(row), axis=1)

    def road_cond(row: pd.Series):
        road_surf_str = row['ROAD_SURF_COND_DESCR'].lower()
        if "dry" in road_surf_str:
            return "A"
        elif "wet" in road_surf_str or  "water" in road_surf_str:
            return "B"
        elif "ice" in road_surf_str or "snow" in road_surf_str or "slush" in road_surf_str:
            return "C"
        elif "oil" in road_surf_str or "mud" in road_surf_str:
            return "D"
        else:
            return "-"
    df['ROAD_COND'] = df.apply(lambda row: road_cond(row), axis=1)
    
    # Trim columns again
    new_columns = ["YEAR", "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON"]
    df = df[new_columns]

    return df

def preprocess_CA_SDS(df:pd.DataFrame) -> pd.DataFrame:
    """Preprocess the California SDS data.

    Args:
        df: a `pd.DataFrame` containing the CA SDS data

    Returns:
        A `pd.DataFrame` containing the preprocessed CA SDS data
    """

    columns = ['ACCIDENT_YEAR',                                                 # Metadata
                'COLLISION_SEVERITY', 'NUMBER_KILLED', 'NUMBER_INJURED',        # Injury level
                'WEATHER_1','ROAD_SURFACE', 'ROAD_COND_1', 'LIGHTING',          # Accident conditions
                'PRIMARY_RD', 'SECONDARY_RD', 'DIRECTION', 'INTERSECTION',      # Road type
                'LATITUDE', 'LONGITUDE',                                        # Geolocation
                'PEDESTRIAN_ACCIDENT', 'BICYCLE_ACCIDENT', 'MOTORCYCLE_ACCIDENT', 'TRUCK_ACCIDENT', # Parties involved
                'PRIMARY_COLL_FACTOR', 'TYPE_OF_COLLISION', 'ALCOHOL_INVOLVED'  # Accident reason
    ]
    columns = [x.upper() for x in columns]
    df = df[columns]

    renames = {
        'ACCIDENT_YEAR' : 'YEAR',
        'COLLISION_SEVERITY' : 'SEVERITY',
        'ROAD_SURFACE' : 'ROAD_COND',
        'PRIMARY_RD' : 'ROAD_NAME',
        'LIGHTING' : 'LIGHT_COND',
        'LATITUDE' : 'LAT',
        'LONGITUDE' : 'LON'
    }
    df = df.rename(columns = renames)

    def is_fatal(row):
        if row['NUMBER_KILLED'] > 0:
            return 1
        return 0
    df['IS_FATAL'] = df.apply(lambda row: is_fatal(row), axis=1)
    
    def is_ped(row: pd.Series):
        str = row['PEDESTRIAN_ACCIDENT']
        if str == "Y":
            return 1
        return 0
    df['IS_PED'] = df.apply(lambda row: is_ped(row), axis=1)

    def is_cyc(row: pd.Series):
        str = row['BICYCLE_ACCIDENT']
        if str == "Y":
            return 1
        return 0
    df['IS_CYC'] = df.apply(lambda row: is_cyc(row), axis=1)

    def weather_cond(row: pd.Series):
        weather_str = row['WEATHER_1']
        if weather_str == "F" or weather_str == "G":
            return "-"
        return weather_str
    df['WEATHER_COND'] = df.apply(lambda row: weather_cond(row), axis=1)

    def is_intersection(row: pd.Series):
        str = row['INTERSECTION']
        if str == "Y":
            return 1
        return 0
    df['IS_INTERSECTION'] = df.apply(lambda row: is_intersection(row), axis=1)

    # Trim columns again
    new_columns = ["YEAR", "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON"]
    df = df[new_columns]
    
    return df

# A dictionary with state names as keys and the corresponding preprocessing functions as values
preprocess_func_dict = {
    'California': preprocess_CA_SDS,
    'Massachusetts': preprocess_MA_SDS
}

def preprocess_SDS_datasets(path: str = 'SDS/Data/', output_path: str = 'SDS/Output_w_MPO_County_Identifiers/') -> dict[str,pd.DataFrame]:
    """Combines folders of SDS datasets in folder `path` into a single CSV file for each folder in `output_path`. Also runs the appropriate preprocessing and labeling function for each state.

    Args:
        path: A string specifying the folders where the CSVs will be loaded from. Defaults to 'SDS/Data/'
        output_path: A string specifying the path to the directory where the combined CSV for each source folder will be saved. Defaults to 'SDS/Output_w_MPO_County_Identifiers/'

    Returns:
        A dictionary where the keys are the subdirectories of 'path' (which should be state names) and the values are the `pd.DataFrame` of all the CSV files contained within that folder.
    """

    all_dirs = helper.get_all_subdirectories(path = path)

    # Dictionary to store all preprocessed dataframes with state names as keys
    output = {}
    for state in all_dirs:
        print("Processing: "+state)
        # Get all SDS filenames within that state (files for different years)
        all_filenames = helper.get_all_filenames(path+state,"*.csv")

        # Get a list of dataframes loaded from the filenames for this state
        all_dfs_state = helper.get_all_dfs_from_csv(all_filenames, index_col=None, encoding_errors='ignore', low_memory=False)
        for df in all_dfs_state:
            df.columns =  df.columns.str.upper()

        # Concatenate all the dataframes into one
        df = helper.concat_pandas_dfs(all_dfs_state)

        # Run preprocessing function for the particular state
        if state in preprocess_func_dict:
            df = preprocess_func_dict[state](df)
            df = preprocess_utils.convert_columns_to_proper_types(df)
            df = preprocess_utils.remove_invalid_lat_lon(df)
            df = label_SDS_with_MPO_and_county_identifiers(df, state)

        # Write the preprocessed and labeled data to a file
        # helper.write_dataframe_to_file(df, output_path+state+".csv")
        helper.write_dataframe_to_file(df, output_path+state+".csv")

        # Add preprocessed data to the output dictionary
        output[state] = df

    # Return output dictionary
    return output

def label_SDS_with_MPO_and_county_identifiers(df, state_name):
    """Loops through all MPO and county shapefiles and check whether each point is inside the polygon boundary.

    Args:
        df: a `pd.DataFrame` of the cleaned and combined SDS data
        state_name: a string of which state is currently being worked on
    Returns:
        A `pd.DataFrame` with the labeled SDS data
    """

    SDS_df = df

    # Cursed magic, I blame Jackie
    if state_name == "California":
        flip_lon_sign = True
    else:
        flip_lon_sign = False
    SDS_gdf = preprocess_utils.create_point_column_from_lat_lon(SDS_df, flip_lon_sign)

    # Convert state name to state id
    state_id = preprocess_utils.d_state_name2id[state_name]

    # Get all County boundaries within state
    sql = text(""" SELECT * FROM "boundaries_county" WHERE "STATE_ID" = {} """.format(state_id))
    county_boundaries = gpd.read_postgis(sql, con=sqlalchemy_conn)


    # Get all MPO boundaries within state
    sql = text(""" SELECT * FROM "boundaries_mpo" WHERE "STATE_ID" = {} """.format(state_id))
    mpo_boundaries = gpd.read_postgis(sql, con=sqlalchemy_conn)

    # Perform a spatial join between SDS and county boundaries
    SDS_with_county = gpd.sjoin(SDS_gdf,county_boundaries, predicate='intersects', how='left')
    columns = ["YEAR", 'COUNTY_ID', "COUNTY_NAME", "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON", "geometry"]
    SDS_with_county = SDS_with_county[columns]

    # Perform a spatial join between SDS and mpo boundaries, but don't include the geometry column
    SDS_with_MPOs = gpd.sjoin(SDS_with_county,mpo_boundaries, predicate='intersects', how='left')
    columns = ["YEAR", 'COUNTY_ID', "COUNTY_NAME", "MPO_ID", "MPO_NAME", "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON"]
    SDS_altered = SDS_with_MPOs[columns]

    # Make sure all the types of the columns are correct
    added_column_type_dict = {  "MPO_ID"                : float, 
                                "MPO_NAME"              : str, 
                                "COUNTY_ID"             : float,
                                "COUNTY_NAME"           : str
    }
    SDS_altered = SDS_altered.astype(added_column_type_dict)

    return SDS_altered



if __name__=="__main__":

    preprocess_SDS_datasets()