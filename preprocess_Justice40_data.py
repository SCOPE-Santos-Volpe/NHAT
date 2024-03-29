"""Loads, cleans, and saves the Justice40 data.

https://screeningtool.geoplatform.gov/en/#3/33.47/-97.5
"""

import geopandas as gpd
import pandas as pd

import helper
import preprocess_utils


def preprocess_justice40_data(path: str = "Justice40/justice_40_communities.csv", output_path: str = "Justice40/justice_40_communities_clean") -> pd.DataFrame:
    """Load and preprocess Justice40 data.

    Args:
        path: a string path pointing to the base data
        output_path: a string path pointing to where to save the updated data

    Returns:
        A `pd.DataFrame` with the cleaned Justice40 data
    """
    # Load the Justice40 data
    df = helper.load_df_from_csv(path=path, low_memory=False)

    # Rename some columns
    renames = {
        'State/Territory': 'STATE_NAME',
        'Census tract ID': 'CENSUS_TRACT_ID',
        'County Name': 'COUNTY_NAME',
        'Identified as disadvantaged': 'IDENTIFIED_AS_DISADVANTAGED'
    }
    df.rename(columns=renames, inplace=True)

    # Get state ID and initial from name
    df['STATE_ID'] = df['STATE_NAME'].map(preprocess_utils.d_state_name2id)
    df['STATE_INITIAL'] = df['STATE_NAME'].map(
        preprocess_utils.d_state_name2initial)

    # Convert True/False to 1/0
    def is_disadvantaged(row):
        if row['IDENTIFIED_AS_DISADVANTAGED'] == True:
            return 1
        return 0
    df['IDENTIFIED_AS_DISADVANTAGED'] = df.apply(
        lambda row: is_disadvantaged(row), axis=1)

    # Select only necessary columns
    columns = ['STATE_ID', 'STATE_NAME', 'CENSUS_TRACT_ID',
               'COUNTY_NAME', 'IDENTIFIED_AS_DISADVANTAGED']
    df = df[columns]

    # Convert types
    column_type_dict = {"STATE_ID": 'Int64',
                        "STATE_NAME": str,
                        "CENSUS_TRACT_ID": 'Int64',
                        "COUNTY_NAME": str,
                        "IDENTIFIED_AS_DISADVANTAGED": 'Int64'
                        }
    df = df.astype(column_type_dict)

    # Write output file
    helper.write_dataframe_to_file(df, output_path+".csv")
    return df


if __name__ == "__main__":
    # census_tract_shp_2_geojson()
    preprocess_justice40_data()
