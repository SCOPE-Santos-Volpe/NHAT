# Olin College Santos Volpe SCOPE Team

Docstring format is [Google Python Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings), copied to [`google_python_style_guide.md`](google_python_style_guide.md#38-comments-and-docstrings). We're not completely following that style guide.

## File Descriptions

Note: This is not a complete list of files. This is all the files with code that is used in the final app.

### [`generate_and_upload_everything.py`](generate_and_upload_everything.py)
This file generates (or regenerates) all of the structured data from the raw data, and uploads all of the data to the RDS.

Booleans do_uploading and do_generating select whether to upload and/or generate data.

### [`census_tracts_split.py`](census_tracts_split.py)
Splits the single census tracts geojson into a geojson for each state.

### [`helper.py`](helper.py)
This file is to hold a bunch of useful helper functions so that they can be imported into any file.

### [`preprocess_FARS_data.py`](preprocess_FARS_data.py)
Combines all .csv datasets (intended for FARS data) into 1 `pd.DataFrame` and writes to a single .csv file.

Main function is `combine_FARS_datasets`. Helper functions load and combine all .csv files in the folder path and get all .csv filenames, clean the data, and label by county and MPO region.

### [`preprocess_geojsons.py`](preprocess_geojsons.py)
Provides code to preprocess state, county, MPO, and census tract boundaries. Functions called by upload_data_to_RDS.py.

### [`preprocess_Justice40_data.py`](preprocess_Justice40_data.py)
Loads, cleans, and saves the Justice40 data.

### [`preprocess_SDS_data.py`](preprocess_SDS_data.py)
Combines all .csv datasets for each folder (intended for SDS data) into 1 `pd.DataFrame` per folder and writes to a single .csv file per folder.

Main function is combine_SDS_datasets. Helper functions take the folder path and get all .csv filenames, read a list of filenames into `pd.DataFrame` objects, and concatenate a list of `pd.DataFrame` objects into a single `pd.DataFrame`.

### [`preprocess_utils.py`](preprocess_utils.py)
This file is to hold a bunch of useful helper functions for preprocessing so that they can be imported into any file.


### [`AWS/upload_data_to_RDS.py`](AWS/upload_data_to_RDS.py)
Functions to upload each type of table to the relational database.

### [`sqlalchemy_conn_string.txt`](sqlalchemy_conn_string.txt)
Holds the secret connection string for the RDB. Not uploaded to GitHub.
