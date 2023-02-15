"""Combines all .csv datasets (intended for FARS data) into 1 pd.DataFrame and writes to a single .csv file.

Main function is combine_FARS_datasets. Helper functions take the folder path and get all .csv filenames, read a list of filenames into pd.DataFrame objects, and concatenate a list of pd.DataFrame objects into a single pd.DataFrame.

"""

import pandas as pd
import helper

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
    all_dfs = helper.get_all_dfs_from_csv(all_filenames, required_columns=['LATITUDE', 'LONGITUD'], index_col=None, encoding_errors='ignore', low_memory=False)
    combined_df = helper.concat_pandas_dfs(all_dfs)
    df = filter_FARS_dataset(combined_df, min_year)
    helper.write_dataframe_to_file(df, output_filename)
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


if __name__=="__main__":
    combine_FARS_datasets()