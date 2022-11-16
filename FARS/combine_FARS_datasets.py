"""Combines all .csv datasets (intended for FARS data) into 1 `pd.DataFrame` and writes to a single .csv file.

Main function is combine_FARS_datasets. Helper functions take the folder path and get all .csv filenames, read a list of filenames into `pd.DataFrame` objects, and concatenate a list of `pd.DataFrame` objects into a single `pd.DataFrame`.

"""

import glob
import pandas as pd
import os

def combine_FARS_datasets(path: str = 'FARS/FARS CSVs/', output_filename: str = 'combined_FARS.csv') -> pd.DataFrame:
    """ Combines FARS datasets in folder `path` into a single CSV file at `output_filename`.

    Calls a series of helper functions, see their docstrings for specifics.
    
    Args: 
        path: A string specifying the folder where the CSVs will be loaded from. Defaults to 'FARS CSVs/'
        output_filename: A string specifying the filename where the combined CSV will be saved. Defaults to 'combined_FARS.csv'

    Returns:
        A `pd.DataFrame object, which is the combined dataframe of all the FARS data
    """

    all_filenames = get_all_csv_filenames(path)
    all_dfs = get_all_dfs_from_csv(all_filenames)
    df = concat_pandas_dfs(all_dfs)
    write_dataframe_to_file(df, output_filename)
    return df

def write_dataframe_to_file(df: pd.DataFrame, filename: str):
    """Writes a `pd.DataFrame` to a CSV file at `filename`.

    Args:
        df: a `pd.DataFrame` to be written.
        filename: a string specifying where to save the file

    Returns:
        Returns the output of `df.to_csv(filename)`
    """
    
    return df.to_csv(filename)

def get_all_csv_filenames(path: str) -> list[str]:
    """Finds and returns the filenames (including the folder) of every CSV in the folder specified at `path`.

    Args:
        path: A string containing the path to the folder containing the .csv files

    Returns:
        A list of strings containing the file path to every csv in the folder at `path`
    """
    all_filenames = glob.glob(os.path.join(path, "*.CSV"))
    print(all_filenames)
    return all_filenames

def get_all_dfs_from_csv(filenames: list[str], required_columns: list[str] = ['LATITUDE','LONGITUD']) -> list[pd.DataFrame]:
    """Returns a list of dataframes loaded from the list of files `filename`.

    If `required_columns` is set then will only load .csvs with every item in `required_columns` in their column names.


    Args:
        filenames: A list of strings containing the filename for each file to load
        required_columns: A list of strings that must be present in the .csv column headers for the csv to be loaded. Default: `['LATITUDE','LONGITUD']`

    Returns:
        A list of dataframes containing the dataframe from every csv in the folder at `path`
    """
    all_files = filenames

    dfs=[]

    for filename in all_files:
        df=pd.read_csv(filename,index_col=None, encoding_errors='ignore', low_memory=False)
        if(all(elem in df.columns for elem in required_columns)):
            dfs.append(df)

    return dfs
    
def concat_pandas_dfs(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    """Wrapper for pd.concat to make maintennance easier

    Args:
        dfs: A list of `pd.DataFrame`
    Returns:
        A single `pd.DataFrame`
    """
    
    return pd.concat(dfs, axis=0, ignore_index=True)
        

if __name__=="__main__":
    combine_FARS_datasets()