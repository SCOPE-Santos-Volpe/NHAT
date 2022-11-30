"""Combines all .csv datasets (intended for FARS data) into 1 `pd.DataFrame` and writes to a single .csv file.

Main function is combine_FARS_datasets. Helper functions take the folder path and get all .csv filenames, read a list of filenames into `pd.DataFrame` objects, and concatenate a list of `pd.DataFrame` objects into a single `pd.DataFrame`.

"""

import pandas as pd
import utils

def combine_FARS_datasets(path: str = 'FARS/FARS CSVs/', output_filename: str = 'combined_FARS.csv') -> pd.DataFrame:
    """Combines FARS datasets in folder `path` into a single CSV file at `output_filename`.

    Calls a series of helper functions, see their docstrings for specifics.
    
    Args: 
        path: A string specifying the folder where the CSVs will be loaded from. Defaults to 'FARS CSVs/'
        output_filename: A string specifying the filename where the combined CSV will be saved. Defaults to 'combined_FARS.csv'

    Returns:
        A `pd.DataFrame object, which is the combined dataframe of all the FARS data
    """

    all_filenames = utils.get_all_csv_filenames(path)
    all_dfs = utils.get_all_dfs_from_csv(all_filenames, required_columns=['LATITUDE', 'LONGITUD'], index_col=None, encoding_errors='ignore', low_memory=False)
    df = utils.concat_pandas_dfs(all_dfs)
    utils.write_dataframe_to_file(df, output_filename)
    return df


if __name__=="__main__":
    combine_FARS_datasets()