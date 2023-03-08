"""This file is to hold a bunch of useful helper functions so that they can be imported into any file
"""

import pandas as pd
import glob
import os
import json
import geopandas as gpd


def get_all_csv_filenames(path: str, filetype: str = None) -> list[str]:
    """Finds and returns the filenames (including the folder) of every CSV in the folder specified at `path`.

    Args:
        path: A string containing the path to the folder containing the .csv files

    Returns:
        A list of strings containing the file path to every csv in the folder at `path`
    """
    if filetype:
        all_filenames = glob.glob(os.path.join(path, "*", filetype))
    else:
        all_filenames = glob.glob(os.path.join(path, "*"))
        
    return all_filenames

def get_all_filenames(path: str, pattern: str, recursive: bool = True) -> list[str]:
    """Finds and returns all filenames within a folder (optionally recursively) with the filename regex pattern match specified by `pattern`.

    Args:
        path: A string containing the path to the folder containing the .csv files
        pattern: S string specifying the regex match for the filename. For example, `pattern = "*.csv"` will return only files with the .csv extension
        recursive: Whether to get filenames from subdirectories recursively. Default is True

    Returns:
        A list strings with each element being the path to a file
    """
    
    if(recursive):
        all_files = []
        for path_i, subdir, files in os.walk(path):
            for filename in glob.glob(os.path.join(path_i, pattern)):
                all_files.append(filename)
    else:
        all_files = glob.glob(os.path.join(path, pattern))
        
    return all_files

def get_all_subdirectories(path: str):
    """Recursively locates all subdirectories within a folder at `path`

    This is necessary to find the subdirectory for each state of the SDS data. That structure is SDS/Data/{Folder for each state}/{file.csv for each year},
    so this function returns a list containing each {Folder for each state}.

    Args:
        path: A string containing the path to the parent folder. The return is a list of all subdirectories of the parent folder.

    Returns:
        A list of strings with each element being the name of a subdirectory of the argument `path`.
    """
    all_subdirs = []
    for path_i, subdir, files in os.walk(path):
        for s in subdir:
            all_subdirs.append(s)
    return all_subdirs

def load_df_from_csv(path:str, **kwargs) -> pd.DataFrame:
    """Loads a dataframe from the csv at `path`.

    Convenience wrapper for `pd.read_csv` because Mira likes wrapping everything in their own helper function

    Args:
        path: A string containing the path to a .csv file
        **kwargs: Pass through other arguments to pd.read_csv

    Returns:
        A `pd.DataFrame` loaded from the .csv
    """
    df=pd.read_csv(path, **kwargs)
    return df

def load_gdf_from_geojson(path:str, **kwargs) -> pd.DataFrame:
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

def get_all_dfs_from_csv(filenames: list[str], required_columns: list[str] = [], **kwargs) -> list[pd.DataFrame]:
    """Returns a list of dataframes loaded from the list of files `filename`.

    If `required_columns` is set then will only load .csvs with every item in `required_columns` in their column names.


    Args:
        filenames: A list of strings containing the filename for each file to load
        required_columns: A list of strings that must be present in the .csv column headers for the csv to be loaded. Default is an empty list

    Returns:
        A list of dataframes containing the dataframe from every csv in the folder at `path`
    """
    all_files = filenames

    dfs=[]

    for filename in all_files:
        df=load_df_from_csv(filename, **kwargs)
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

def write_dataframe_to_file(df: pd.DataFrame, filename: str):
    """Writes a `pd.DataFrame` to a CSV file at `filename`.

    Args:
        df: a `pd.DataFrame` to be written.
        filename: a string specifying where to save the file

    Returns:
        Returns the output of `df.to_csv(filename)`
    """
    
    return df.to_csv(filename)


