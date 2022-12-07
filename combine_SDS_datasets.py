"""Combines all .csv datasets (intended for FARS data) into 1 `pd.DataFrame` and writes to a single .csv file.

Main function is combine_FARS_datasets. Helper functions take the folder path and get all .csv filenames, read a list of filenames into `pd.DataFrame` objects, and concatenate a list of `pd.DataFrame` objects into a single `pd.DataFrame`.

"""

import pandas as pd
import utils

def combine_SDS_datasets(path: str = '', output_path: str = 'SDS/Output') -> pd.DataFrame:
    """Combines FARS datasets in folder `path` into a single CSV file at `output_filename`.

    Calls a series of helper functions, see their docstrings for specifics.
    
    Args: 
        path: A string specifying the folder where the CSVs will be loaded from. Defaults to 'FARS CSVs/'
        output_filename: A string specifying the filename where the combined CSV will be saved. Defaults to 'combined_FARS.csv'

    Returns:
        A `pd.DataFrame object, which is the combined dataframe of all the FARS data
    """

    # all_filenames = utils.get_all_filenames(path = path, extension="*")
    all_dirs = utils.get_all_subdirectories(path = path)
    print("Full list of states: " + str(all_dirs))
    for state_dir in all_dirs:
        print("Processing: "+state_dir)
        all_filenames = utils.get_all_filenames(path+state_dir,"*.csv")
        all_dfs_state = utils.get_all_dfs_from_csv(all_filenames, index_col=None, encoding_errors='ignore', low_memory=False)
        combined_df = utils.concat_pandas_dfs(all_dfs_state)
        utils.write_dataframe_to_file(combined_df, output_path+state_dir+".csv")
    return combined_df

if __name__=="__main__":
    combine_SDS_datasets(path = 'SDS/Data/', output_path='SDS/Output/')