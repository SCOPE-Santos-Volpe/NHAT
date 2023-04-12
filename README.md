# Olin College Santos Volpe SCOPE Team

Docstring format is [Google Python Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings), copied to [`google_python_style_guide.md`](google_python_style_guide.md#38-comments-and-docstrings). We're not completely following that style guide.

## File Descriptions

Note: This is not a complete list of files. This is all the files with code that is used in the final app.

### [`census_tracts_split.py`](census_tracts_split.py)
Splits the single census tracts geojson into a geojson for each state.

### [`dataset_categorize_shapefile.py`](dataset_categorize_shapefile.py)
Categorizes each row of a dataframe into categories as defined by shapefiles. The main interface function is `categorize_df_to_shapefiles.`

THIS FILE IS USELESS, CONFIRM THAT WE DONT NEED IT

### [`helper.py`](helper.py)
This file is to hold a bunch of useful helper functions so that they can be imported into any file.

### [`preprocess_FARS_data.py`](preprocess_FARS_data.py)
Combines all .csv datasets (intended for FARS data) into 1 `pd.DataFrame` and writes to a single .csv file.

Main function is `combine_FARS_datasets`. Helper functions load and combine all .csv files in the folder path and get all .csv filenames, clean the data, and label by county and MPO region.

### [`preprocess_geojsons.py`](preprocess_geojsons.py)
Preprocess geojsons bc they are ugly

TODO: document this file

### [`preprocess_Justice40_data.py`](preprocess_Justice40_data.py)
No description yet

TODO: Document this file

### [`preprocess_SDS_data.py`](preprocess_SDS_data.py)
Combines all .csv datasets for each folder (intended for SDS data) into 1 `pd.DataFrame` per folder and writes to a single .csv file per folder.

Main function is combine_SDS_datasets. Helper functions take the folder path and get all .csv filenames, read a list of filenames into `pd.DataFrame` objects, and concatenate a list of `pd.DataFrame` objects into a single `pd.DataFrame`.

### [`preprocess_utils.py`](preprocess_utils.py)
No description yet

TODO: Document this file

### ['AWS/upload_data_to_RDS.py`](AWS/upload_data_to_RDS.py)
No description yet

TODO: Document this file