"""Combines all .csv datasets (intended for FARS data) into 1 pd.DataFrame and writes to a single .csv file.

Main function is combine_FARS_datasets. Helper functions take the folder path and get all .csv filenames, read a list of filenames into pd.DataFrame objects, and concatenate a list of pd.DataFrame objects into a single pd.DataFrame.

https://crashstats.nhtsa.dot.gov/Api/Public/ViewPublication/813254

"""

import pandas as pd
import geopandas as gpd
import helper
import preprocess_utils

from sqlalchemy import create_engine, Table, Column, Integer, String, text

# Establish sqlalchemy connection
conn_string = 'postgresql://scope_team:greenTea123@database-1.ci75bfibgs4e.us-east-1.rds.amazonaws.com/FARS'
db = create_engine(conn_string)
sqlalchemy_conn = db.connect()
print('Python connected to PostgreSQL via Sqlalchemy')


def combine_FARS_datasets(path: str = 'FARS/FARS CSVs/', output_filename: str = 'combined_FARS.csv', min_year: int = 2015) -> pd.DataFrame:
    """Combines FARS datasets in folder path into a single CSV file at output_filename.

    Calls a series of helper functions, see their docstrings for specifics.

    Args:
        path: A string specifying the folder where the CSVs will be loaded from. Defaults to 'FARS CSVs/'
        output_filename: A string specifying the filename where the combined CSV will be saved. Defaults to 'combined_FARS.csv'
        min_year: An integer specifying the minimum year to be included. Defaults to 2015.
    Returns:
        A pd.DataFrame object, which is the combined dataframe of all the FARS data
    """

    all_filenames = helper.get_all_filenames(path, "*.CSV")
    all_dfs = helper.get_all_dfs_from_csv(all_filenames, requiredcolumns_=['LATITUDE', 'LONGITUD'], index_col=None, encoding_errors='ignore', low_memory=False)
    combined_df = helper.concat_pandas_dfs(all_dfs)
    df = filter_FARS_dataset(combined_df, min_year)
    return df

def filter_FARS_dataset(df: pd.DataFrame, min_year: int) -> pd.DataFrame:
    """Remove all rows with invalid latitude and longitude values. Remove all data that is not between 2015-2020.

    Args:
        df: A pd.DataFrame
        min_year: An int specifying the minimum year to be included
    Returns:
        df_clean: A pd.DataFrame
    """
    # Delete invalid lat/long
    df_clean = df.loc[(df["LATITUDE"] >=-90) & (df["LATITUDE"] <=90) & 
                      (df["LONGITUD"] >=-180) & (df["LONGITUD"] <=180)]
    # Filter data for the past 5 years
    df_clean = df_clean.loc[(df_clean["YEAR"] >= min_year)]
    # Drop any empty columns 
    nan_value = float("NaN")
    df_clean.replace("", nan_value, inplace=True)
    df_clean = df_clean.dropna(axis=1, how='all')

    return df_clean

def preprocess_FARS(df:pd.DataFrame) -> pd.DataFrame:
    print(df.columns)

    columns = ['YEAR', 'STATE',                                         # Metadata
                'LGT_COND', 'WEATHER',                                  # Accident conditions
                'TYP_INT',                                              # Road type
                'LATITUDE', 'LONGITUD',                                 # Geolocation
                'PEDS',                                                 # Parties involved
    ]
    columns = [x.upper() for x in columns]
    df = df[columns]

    renames = {
        'LATITUDE' : 'LAT',
        'LONGITUD' : 'LON',
        'STATE'    : 'STATE_ID'
    }
    df.rename(columns = renames,inplace = True)

    def is_fatal(row):
            return 1
    df['IS_FATAL'] = df.apply(lambda row: is_fatal(row), axis=1)

    def severity(row):
        return 1
    df['SEVERITY'] = df.apply(lambda row: severity(row), axis=1)
    
    def is_ped(row: pd.Series):
        num_peds = row['PEDS']
        if num_peds > 0:
            return 1
        return 0
    df['IS_PED'] = df.apply(lambda row: is_ped(row), axis=1)

    def is_cyc(row: pd.Series):
        return "0"
    df['IS_CYC'] = df.apply(lambda row: is_cyc(row), axis=1)

    def weather_cond(row: pd.Series):
        weather = row['WEATHER']
        if weather == 1:
            return "A"
        if weather == 2:
            return "C"
        if weather == 3 or weather == 4:
            return "D"
        if weather == 5:
            return "E"
        if weather == 10:
            return "B"
        else:
            return "-"
    df['WEATHER_COND'] = df.apply(lambda row: weather_cond(row), axis=1)

    def light_cond(row: pd.Series):
        light = row['LGT_COND']
        if light == 1:
            return "A"
        if light == 2:
            return "D"
        if light == 3:
            return "C"
        if light == 4 or light == 5:
            return "B"
        if light == 6:
            return "E"
        else:
            return "-"
    df['LIGHT_COND'] = df.apply(lambda row: light_cond(row), axis=1)

    def road_cond(row: pd.Series):
        return "-"
    df['ROAD_COND'] = df.apply(lambda row: road_cond(row), axis=1)
    
    def road_name(row: pd.Series):
        return "-"
    df['ROAD_NAME'] = df.apply(lambda row: road_name(row), axis=1)

    def is_intersection(row: pd.Series):
        inter = row['TYP_INT']
        if inter != 1:
            return 1
        return 0
    df['IS_INTERSECTION'] = df.apply(lambda row: is_intersection(row), axis=1)

    # Trim columns again
    new_columns = ["YEAR", 'STATE_ID', "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON"]
    df = df[new_columns]

    df = preprocess_utils.convert_columns_to_proper_types(df)
    df = preprocess_utils.remove_invalid_lat_lon(df)

    return df

def label_FARS_with_MPO_and_county_identifiers():

    """ Take processed FARs and label it with MPO and county 
        TODO: GET HELP FROM ZDR FOR THIS
    """
    # Get FARS data
    processed_FARS_path = 'combined_FARS_preprocessed.csv'
    FARS_df = helper.load_df_from_csv(processed_FARS_path)
    print("Got FARS data")
    print(FARS_df.head)
    
    FARS_df = preprocess_utils.create_point_column_from_lat_lon(FARS_df)
    print("made point columns from lat long and is now geojson")

    # Add new column for state_id
    def set_state_name(row: pd.Series):
        return preprocess_utils.d_state_id2name[row['STATE_ID']]
    FARS_df['STATE_NAME'] = FARS_df.apply(lambda row: set_state_name(row), axis=1)

    # Get all County boundaries
    print("Getting all County boundaries")
    sql = text(""" SELECT * FROM "boundaries_county" """)
    county_boundaries = gpd.read_postgis(sql, con=sqlalchemy_conn)
    print("Got all County boundaries")
    print(county_boundaries.head)

    # Get all MPO boundaries
    print("Getting all MPO boundaries")
    sql = text(""" SELECT * FROM "boundaries_mpo" """)
    mpo_boundaries = gpd.read_postgis(sql, con=sqlalchemy_conn)
    print("Got all MPO boundaries")
    print(mpo_boundaries.head)

    # Perform a spatial join between SDS and county boundaries
    FARS_with_county = gpd.sjoin(FARS_df,county_boundaries, predicate='intersects', how='left')
    print(FARS_with_county.columns)
    columns = ["YEAR", 'STATE_ID_left', 'STATE_NAME_left', 'COUNTY_ID', "COUNTY_NAME", "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON", "geometry"]
    FARS_with_county = FARS_with_county[columns]
    
    # Perform a spatial join between SDS and mpo boundaries, but remove the geometry column 
    FARS_with_MPOs = gpd.sjoin(FARS_with_county,mpo_boundaries, predicate='intersects', how='left')
    columns = ["YEAR", 'STATE_ID_left', 'STATE_NAME_left', 'COUNTY_ID', "COUNTY_NAME", "MPO_ID", "MPO_NAME", "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON"]
    FARS_altered = FARS_with_MPOs[columns]

    renames = {
        'STATE_ID_left'   : 'STATE_ID',
        'STATE_NAME_left' : 'STATE_NAME',
    }
    FARS_altered.rename(columns = renames,inplace = True)

    # Write updated geojson to file
    helper.write_dataframe_to_file(FARS_altered, "FARS/FARS_w_MPO_County_Identifiers.csv")

def label_FARS_with_census_tract_identifiers():

    """ Take processed FARs and label it with MPO and county 
    """
    # Get FARS data
    print("Getting all FARS boundaries")
    sql = text(""" SELECT * FROM "FARS" """)
    FARS_df = gpd.read_postgis(sql, con=sqlalchemy_conn)
    print("Got all FARS")
    print(FARS_df.head)
    
    # Get all census tract boundaries
    print("Getting all census tract boundaries")
    sql = text(""" SELECT * FROM "boundaries_census_tract" """)
    census_tract_boundaries = gpd.read_postgis(sql, con=sqlalchemy_conn)
    print("Got all census tract boundaries")
    print(census_tract_boundaries.head)

    # Perform a spatial join between SDS and county boundaries
    FARS_with_county = gpd.sjoin(FARS_df,census_tract_boundaries, predicate='intersects', how='left')
    print(FARS_with_county.columns)
    columns = ["YEAR", 'STATE_ID_left', 'STATE_NAME_left', 'COUNTY_ID', "COUNTY_NAME", "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON", "geometry"]
    FARS_with_county = FARS_with_county[columns]
    
    # Perform a spatial join between SDS and mpo boundaries
    FARS_with_MPOs = gpd.sjoin(FARS_with_county,mpo_boundaries, predicate='intersects', how='left')
    columns = ["YEAR", 'STATE_ID_left', 'STATE_NAME_left', 'COUNTY_ID', "COUNTY_NAME", "MPO_ID", "MPO_NAME", "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON", "geometry"]
    FARS_altered = FARS_with_MPOs[columns]

    renames = {
        'STATE_ID_left'   : 'STATE_ID',
        'STATE_NAME_left' : 'STATE_NAME',
    }
    FARS_altered.rename(columns = renames,inplace = True)

    # Write updated geojson to file
    helper.write_dataframe_to_file(FARS_altered, "FARS/FARS_w_MPO_County_Identifiers.csv")


if __name__=="__main__":
    # combine_FARS_datasets()
    # df = helper.load_df_from_csv('combined_FARS.csv')
    # df = preprocess_FARS(df)
    # helper.write_dataframe_to_file(df, 'combined_FARS_preprocessed.csv')

    label_FARS_with_MPO_and_county_identifiers()