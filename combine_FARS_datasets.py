import glob
import pandas as pd
import numpy as np
import os

def combine_FARS_datasets(path='FARS CSVs/', output_filename='combined_FARS.csv'):
    all_filenames = get_all_csv_filenames(path)
    all_files = get_all_dfs_from_csv(all_filenames)
    df = concat_pandas_dfs(all_files)
    write_to_file(df, output_filename)


def write_to_file(df, filename):
    df.to_csv(filename)

def get_all_csv_filenames(path):
    all_filenames = glob.glob(os.path.join(path, "*.CSV"))
    return all_filenames

def get_all_dfs_from_csv(filenames, only_include_df_with_lat_lon=True):
    all_files = filenames


    dfs=[]

    for filename in all_files:
        df=pd.read_csv(filename,index_col=None, encoding_errors='ignore', low_memory=False)
        if(('LATITUDE' in df.columns and 'LONGITUD' in df.columns) or only_include_df_with_lat_lon):
            dfs.append(df)
    return dfs
    

def concat_pandas_dfs(dfs):
    return pd.concat(dfs, axis=0, ignore_index=True)
        

if __name__=="__main__":
    combine_FARS_datasets()