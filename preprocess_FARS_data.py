"""Combines all .csv datasets (intended for FARS data) into 1 `pd.DataFrame` and writes to a single .csv file.

Main function is `combine_FARS_datasets`. Helper functions load and combine all .csv files in the folder path and get all .csv filenames, clean the data, and label by county and MPO region.
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


def combine_FARS_datasets(path: str = 'FARS/FARS CSVs/', output_filename: str = 'FARS/FARS_w_MPO_County_Identifiers.csv', min_year: int = 2015) -> pd.DataFrame:
    """Combines FARS datasets in folder path into a single CSV file at output_filename.

    Calls a series of helper functions, see their docstrings for specifics.

    Args:
        path: A string specifying the folder where the CSVs will be loaded from. Defaults to 'FARS CSVs/'
        output_filename: A string specifying the filename where the combined CSV will be saved. Defaults to 'combined_FARS.csv'
        min_year: An integer specifying the minimum year to be included. Defaults to 2015.
    Returns:
        A `pd.DataFrame` object, which is the combined dataframe of all the FARS data
    """

    all_filenames = helper.get_all_filenames(path, "*.CSV")
    all_dfs = helper.get_all_dfs_from_csv(all_filenames, requiredcolumns_=['LATITUDE', 'LONGITUD'], index_col=None, encoding_errors='ignore', low_memory=False)
    combined_df = helper.concat_pandas_dfs(all_dfs)
    cleaned_df = clean_FARS_dataset(combined_df, min_year)
    labeled_df = label_FARS_with_MPO_and_county_identifiers(cleaned_df)
    # Write updated geojson to file
    helper.write_dataframe_to_file(labeled_df, output_filename)
    return labeled_df

def clean_FARS_dataset(df: pd.DataFrame, min_year: int) -> pd.DataFrame:
    """Perform cleaning steps for FARS dataset.

    Remove all rows with invalid latitude and longitude values. Remove all data that is before the min year. Process data to line up with SDS format.

    Args:
        df: A `pd.DataFrame`
        min_year: An `int` specifying the minimum year to be included
    Returns:
        A `pd.DataFrame` with the cleaned FARS data
    """
    # Remove invalid lat/lon values
    df = preprocess_utils.remove_invalid_lat_lon(df)
    # Filter data for the past 5 years
    df = df.loc[(df["YEAR"] >= min_year)]
    # Drop any empty columns
    nan_value = float("NaN")
    df.replace("", nan_value, inplace=True)
    df = df.dropna(axis=1, how='all')

    # Select which columns we're keeping
    columns = ['YEAR', 'STATE',                                         # Metadata
                'LGT_COND', 'WEATHER',                                  # Accident conditions
                'TYP_INT',                                              # Road type
                'LATITUDE', 'LONGITUD',                                 # Geolocation
                'PEDS',                                                 # Parties involved
    ]
    columns = [x.upper() for x in columns]
    df = df[columns]

    # Rename columns for consistency
    renames = {
        'LATITUDE' : 'LAT',
        'LONGITUD' : 'LON',
        'STATE'    : 'STATE_ID'
    }
    df.rename(columns = renames,inplace = True)

    # Section to make columns align with SDS columns

    # All crashes are fatal
    def is_fatal(row):
            return 1
    df['IS_FATAL'] = df.apply(lambda row: is_fatal(row), axis=1)

    # Severity 1 is fatal
    def severity(row):
        return 1
    df['SEVERITY'] = df.apply(lambda row: severity(row), axis=1)

    # Calculate if involves pedestrians
    def is_ped(row: pd.Series):
        num_peds = row['PEDS']
        if num_peds > 0:
            return 1
        return 0
    df['IS_PED'] = df.apply(lambda row: is_ped(row), axis=1)

    # No bikes in FARS
    def is_cyc(row: pd.Series):
        return "0"
    df['IS_CYC'] = df.apply(lambda row: is_cyc(row), axis=1)

    # Make weather align with SDS
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

    # Make light conditions align with SDS
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

    # We don't know road conditions here
    def road_cond(row: pd.Series):
        return "-"
    df['ROAD_COND'] = df.apply(lambda row: road_cond(row), axis=1)

    # We don't know road name here
    def road_name(row: pd.Series):
        return "-"
    df['ROAD_NAME'] = df.apply(lambda row: road_name(row), axis=1)

    # Calculate if is intersection
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

    return df

def label_FARS_with_MPO_and_county_identifiers(df):
    """Take preprocessed FARS data and label it with MPO and county.

    Args:
        df: a `pd.DataFrame` outputted by `clean_FARS_data`

    Returns:
        A `pd.DataFrame` of FARS data, labeled by MPO and county
    """

    # Create a column with a point opject, and convert to geojson
    df = preprocess_utils.create_point_column_from_lat_lon(df)

    # Add new column for state_id
    def set_state_name(row: pd.Series):
        return preprocess_utils.d_state_id2name[row['STATE_ID']]
    df['STATE_NAME'] = df.apply(lambda row: set_state_name(row), axis=1)

    # Get all County boundaries from the database
    sql = text(""" SELECT * FROM "boundaries_county" """)
    county_boundaries = gpd.read_postgis(sql, con=sqlalchemy_conn)

    # Get all MPO boundaries from the database
    sql = text(""" SELECT * FROM "boundaries_mpo" """)
    mpo_boundaries = gpd.read_postgis(sql, con=sqlalchemy_conn)

    # Perform a spatial join between FARS and county boundaries.
    # This adds a column of which county the point is in.
    FARS_with_county = gpd.sjoin(df,county_boundaries, predicate='intersects', how='left')
    columns = ["YEAR", 'STATE_ID_left', 'STATE_NAME_left', 'COUNTY_ID', "COUNTY_NAME", "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON", "geometry"]
    FARS_with_county = FARS_with_county[columns]
    
    # Perform a spatial join between FARS and MPO boundaries
    # This adds a column of which MPO region the point is in.
    # Also removes the geometry column
    FARS_with_MPOs = gpd.sjoin(FARS_with_county,mpo_boundaries, predicate='intersects', how='left')
    columns = ["YEAR", 'STATE_ID_left', 'STATE_NAME_left', 'COUNTY_ID', "COUNTY_NAME", "MPO_ID", "MPO_NAME", "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON"]
    FARS_altered = FARS_with_MPOs[columns]

    # Rename from joins
    renames = {
        'STATE_ID_left'   : 'STATE_ID',
        'STATE_NAME_left' : 'STATE_NAME',
    }
    FARS_altered = FARS_altered.rename(columns = renames)

    return FARS_altered

if __name__=="__main__":
    df = combine_FARS_datasets()
    print("Ding!")