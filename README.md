# National High Injury Network (HIN) Analysis Tool (NHAT) Web App 

Partnering with the Santos Family Foundation and the Volpe National Transportation Systems Center, NHAT was developed by Olin College Students as a Senior Capstone Project in 2023. NHAT is a free national tool that allows communities to generate interactive HIN maps and understand the relationship between safety, equity, and other contextual factors. This project aims to generate and visualize a High Injury Network for every geographic area in the United States using Fatality Analysis Reporting System (FARS), State Data System (SDS), and Justice 40 equity data. The ultimate goal is to provide a live web-app map that displays the entire national roadway network and highlights areas with the highest injury rates using an algorithm based on kernel density estimation.

The current version of the website is hosted [here](http://34.233.143.226/)

For more information on the usage of the web app go [here](https://docs.google.com/document/d/1Ayhyc90FQXBuUS7694T1m7Xpa8PzGiR2jC1KWXh37FA/edit?usp=sharing)

## Table of Contents

1. [How to Access AWS Relational Database (RDS)](#data)
2. [How to Run High Injury Network Algorithm](#high-injury-network)
3. [How to Launch the Web App](#web-app)

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

This command will generate the High Injury Network for the specified state and county using the California SDS dataset.

## Web App

The web app is built on an EC2 server and is responsible for visualizing the High Injury Network on a live map. This section will guide you on how to interact with the server. Visualizing on a live map makes it easy for users to explore the data and modify functionality.

### Change and Test Flask App Locally

The branch that the web app code is contained in is called “ec2”. Run this command to get code from that branch and get into the virtual environment.
```bash
git checkout ec2
cd flask_hin_app
source venv/bin/activate 
```
Now, you can edit the code. To test the changes you made, start up the flask app by running the following command:
```bash
python3 demo.py
```
While demo.py is running locally, go here to see the local website: http://127.0.0.1:5000 


### Setting up the EC2 Instance 

Use this tutorial to deploy a Flask application on EC2, but substitute the code contained in the EC2 branch for the example Flask app given in the tutorial: [Flask App on AWS Tutorial](https://medium.com/techfront/step-by-step-visual-guide-on-deploying-a-flask-application-on-aws-ec2-8e3e8b82c4f7)  


Firstly, you will need the RSA private key file for your EC2 instance in order to log into it remotely. It will be a file with the extension '.pem’. The file contents should look something like this:
```bash
-----BEGIN RSA PRIVATE KEY-----
<alphanumeric RSA key here>
-----END RSA PRIVATE KEY-----
```

To SSH into the EC2 instance, open up your terminal and run this command, replacing the location of the key file and the Public IPv4 DNS address of the EC2 instance.
```bash
ssh -i ~/Downloads/key_file_name.pem ubuntu@ec2-34-233-143-226.compute-1.amazonaws.com
```
  
Next, clone this repository, check out the "ec2" branch where the web app code is located, and start up the virtual environment.
```bash
git clone https://github.com/SCOPE-Santos-Volpe/SCOPE-Santos-Volpe-Project
git checkout ec2
cd flask_hin_app
source venv/bin/activate 
```
 
Once you have started the web app service, go to the EC2 instance's IP address to see the web app, but make sure to use http rather than https. For example: http://34.233.143.226


### Command Lines
To interact with and refresh the systemctl web app service, here is a list of commands:
  
TO REFRESH WEB APP:
```bash
sudo systemctl daemon-reload
sudo systemctl restart helloworld.service
```
  
TO CHECK STATUS:
```bash
systemctl status helloworld.service
systemctl status
```

TO START THE WEBAPP SERVICE:
```bash
sudo systemctl start helloworld.service
sudo systemctl enable helloworld.service
curl localhost:8010
sudo nano /etc/nginx/sites-available/default
```

TO RESTART THE WEBAPP SERVICE:
```bash
sudo systemctl daemon-reload
sudo systemctl restart helloworld.service
sudo systemctl restart nginx
systemctl status helloworld.service
```

TO STOP THE WEBAPP SERVICE:
```bash
sudo systemctl disable helloworld.service
sudo systemctl stop helloworld.service
```

### Editing the Web App Code

To modify and edit the web app code, there are four main files:
```bash
demo.py
demo.js
demo.css 
index.html
```

### VS Code Extension
 
To connect and edit the files on EC2 in VS Code, follow these instructions: 
  - First, go to extensions and look up “Remote-SSH”. Install the plugin with this name. 
  - Next, go to the command palette and look up “Remote-SSH: connect to host”. Click “Configure SSH hosts”, then select the SSH configuration file to update. This might be called C:\Users\username\.ssh\config, replacing “username” with your own username. This will open your SSH configuration file. 
  - Paste in the following contents and save the file. Now you have added the EC2 instance as an SSH host. 
```bash
Host aws-ec2
  HostName ec2-34-233-143-226.compute-1.amazonaws.com
  IdentityFile ~/Downloads/scope_team.pem
  User ubuntu
```
  - To connect to the EC2 instance, again go to the command palette and look up “Remote-SSH: connect to host”. Click on “aws-ec2”. This will open a new VS Code window that is connected to the EC2 instance. 
  - Go to the file explorer tab. Click “Open Folder”, then click “OK”. The files from the EC2 instance are shown on the left sidebar, and you can open and edit them.   
  - If you encounter a problem with VS Code crashing when you try to edit the code, follow this tutorial: 
https://medium.com/good-robot/use-visual-studio-code-remote-ssh-sftp-without-crashing-your-server-a1dc2ef0936d
    - If it still crashes, restart the EC2 Instance. Go to your EC2 instance on the AWS dashboard. Click on “Instance State” → “Stop Instance” and wait until the Instance State turns from “Stopping” to “Stopped”. Then click on “Instance State” → “Start Instance” and wait until the Instance State turns to “Running” again. 

  
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
