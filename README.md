# High Injury Network Webapp 

Partnering with the Santos Family Foundation and the Volpe National Transportation Systems Center, NHAT was developed by Olin College Students as a Senior Capstone Project in 2023. NHAT is a free national tool that allows communities to generate interactive HIN maps and understand the relationship between safety, equity, and other contextual factors. This project aims to identify and visualize high injury networks in the United States using Fatality Analysis Reporting System (FARS), State Data System (SDS), and Justice 40 equity data. The ultimate goal is to provide a live web-app map that displays the entire national roadway network and highlights areas with high injury rates using kernel density estimation.

The current version of the website is hosted [here](http://34.233.143.226/)

For more information on the usage of the Web-app go [here](https://docs.google.com/document/d/1Ayhyc90FQXBuUS7694T1m7Xpa8PzGiR2jC1KWXh37FA/edit?usp=sharing)

## Table of Contents

1. [How to Access AWS Relational Database (RDS)](#data)
2. [How to Run High Injury Network Algorithm](#high-injury-network)
3. [How to Launch The Web-app](#web-app)

## Data

The data used in this project comes from the following sources:

- [FARS: Fatality Analysis Reporting System](https://www.nhtsa.gov/research-data/fatality-analysis-reporting-system-fars)
- [SDS: Serious Data System](https://www.nhtsa.gov/state-data-programs/sds-overview) 
  - [California SDS](https://dot.ca.gov/programs/research-innovation-system-information/annual-collision-data)
  - [Massachussets SDS](https://apps.impact.dot.state.ma.us/cdp/home)
- [Justice 40: Justice 40 equity data](https://www.transportation.gov/equity-Justice40)

### Crash Data Structure
FARS and SDS data all come in different formats. In order to use them consistently with our web app, we narrowed down several key attributes to retain for each dataset. Our data format is heavily inspired by the Massachusetts SDS format.

```bash
YEAR :			int
IS_FATAL :		int (one-hot)
SEVERITY :		int (1-4 range)
    1 - Fatal
    2 - Injury (Severe)
    3 - Injury (Other Visible)
    4 - Injury (Complaint of Pain)
    0 - PDO (Property Damage/Other)
IS_PED : 		int (one-hot)
IS_CYC : 		int (one-hot)
WEATHER_COND :	int (1-4 range)
    A - Clear
    B - Cloudy
    C - Rain
    D - Snow / Sleet / Hail
    E - Fog / Smog / Smoke
    -  - Other
LIGHT_COND :	int (1-4 range)
    A - Daylight
    B - Dusk - Dawn
    C - Dark - Street Lights
    D - Dark - No Street Lights
    E - Dark - Unknown Street Lights
    -  - Other
ROAD_COND :	int (1-4 range)
    A - Dry
    B - Wet / Water
    C - Snowy / Icy / Slush
    D - Slippery (Muddy, Oily, etc.)
    -  - Not Stated
ROAD_NAME : 	str
IS_INTERSECTION :	int (one-hot)
LAT : 			int
LON : 			int
```

### How to Update the Data

See [`generate_and_upload_everything.py`](generate_and_upload_everything.py), which regenerates/reprocesses all data from its raw source and uploads it to the database.

To add or update SDS data, add the files into `SDS/Data/{state name}/{file name}.csv`. If adding a new state, in [`preprocess_SDS_data.py`](preprocess_SDS_data.py), write a new function that takes in a `pd.DataFrame`, processes it, and returns a `pd.DataFrame`. Then, add that function into `preprocess_func_dict`. Then, reprocess and upload the data.

To add new FARS data, download the data and unzip the `.zip` file. Take the `accident.CSV` file and put it into `FARS/FARS CSVs/*.CSV` . Renaming the `accident.CSV` file is not necessary but recommended for future maintainability. The file extension for these files is `.CSV` instead of `.csv` because that’s what the files came as, and we didn’t change them. Then, reprocess and upload the data.
## High Injury Network

The High Injury Network (HIN) module is responsible for processing the data and generating the high injury network using kernel density estimation. To execute this module, run the [`generate_hin.py`](generate_hin.py) script with the specified state and county IDs, and the choice of table name (either "California" or "Massachusetts") for the SDS dataset.

### Dependencies

To install the required libraries, run the following command:

```bash
pip install --upgrade geoalchemy2 geojson geopandas matplotlib numpy osmnx pandas psycopg2 pyproj scipy shapely sqlalchemy<2
```

### Running the Script

To execute the HIN module, use the following command:

```bash
python generate_hin.py --state_id <STATE_ID> --county_id <COUNTY_ID> --table_name <TABLE_NAME>
```

Replace `<STATE_ID>` with the desired state ID, `<COUNTY_ID>` with the desired county ID, and `<TABLE_NAME>` with either "California" or "Massachusetts" based on the SDS dataset you'd like to use.

### Example

Here's an example of running the script for state ID 6 (California) and county ID 3:

```bash
python generate_hin.py --state_id 6 --county_id 3 --table_name California
```

This command will generate the high injury network for the specified state and county using the California SDS dataset.

## Web-app

The web-app is built on an EC2 server and is responsible for visualizing the high injury network on a live map. This section will guide you on how to interact with the server.

### Interacting with the EC2 server

TODO: Update this

To interact with the EC2 server, please follow these instructions:
```bash
<placeholder_instructions_for_interacting_with_ec2_server>
```
This will allow you to visualize the high injury network on a live map, making it easy for users to explore the data and modify the HIN functionality.


## File Descriptions

Note: This is not a complete list of files. This is all the files with code that is used in the final app.

### [`generate_and_upload_everything.py`](generate_and_upload_everything.py)
This file generates (or regenerates) all of the structured data from the raw data, and uploads all of the data to the RDS.

Booleans do_uploading and do_generating select whether to upload and/or generate data.

### [`census_tracts_split.py`](census_tracts_split.py)
Splits the single census tracts geojson into a geojson for each state.

### [`generate_hin.py`](generate_hin.py)
TODO: add a description

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
