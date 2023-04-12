# High Injury Network Webapp 

Partnering with the Santos Family Foundation and the Volpe National Transportation Systems Center, NHAT was developed by Olin College Students as a Senior Capstone Project in 2023. NHAT is a free national tool that allows communities to generate interactive HIN maps and understand the relationship between safety, equity, and other contextual factors. This project aims to identify and visualize high injury networks in the United States using Fatality Analysis Reporting System (FARS), State Data System (SDS), and Justice 40 equity data. The ultimate goal is to provide a live web-app map that displays the entire national roadway network and highlights areas with high injury rates using kernel density estimation.

The current version of the website is hosted [here](http://34.233.143.226/)

For more information on the usage of the Web-app go [here](https://docs.google.com/document/d/1Ayhyc90FQXBuUS7694T1m7Xpa8PzGiR2jC1KWXh37FA/edit?usp=sharing)

## Table of Contents

1. [How to Access AWS Relational Database(RDS)](#data)
2. [How to Run High Injury Network Algorithm](#high-injury-network)
3. [How to Launch The Web-app](#web-app)

## Data

The data used in this project comes from the following sources:

- [FARS: Fatality Analysis Reporting System](https://www.nhtsa.gov/research-data/fatality-analysis-reporting-system-fars)
- [SDS: Serious Data System](https://www.nhtsa.gov/state-data-programs/sds-overview) 
  - [California SDS](https://dot.ca.gov/programs/research-innovation-system-information/annual-collision-data)
  - [Massachussets SDS](https://apps.impact.dot.state.ma.us/cdp/home)
- [Justice 40: Justice 40 equity data](https://www.transportation.gov/equity-Justice40)

To access the data, please use the following line of code, replacing `<placeholders>` with the appropriate information:

```bash
<placeholder_code_to_access_database>
```


## High Injury Network

The High Injury Network (HIN) module is responsible for processing the data and generating the high injury network using kernel density estimation. To execute this module, run the `generate_hin.py` script with the desired area and the choice between the FARS or SDS dataset, with the possible additional layer of Justice 40.

### Dependencies

To install the required libraries, run the following command:
```bash
pip install osmnx scipy numpy matplotlib pandas geopandas shapely multiprocessing geojson pyproj
```
### Running the Script

To execute the HIN module, use the following command:

```bash

python generate_hin.py --area <AREA> --dataset <FARS/SDS> [--justice40]

```

Replace <AREA> with the desired geographic area, <FARS/SDS> with either "FARS" or "SDS" based on the dataset you'd like to use, and add --justice40 if you'd like to include the Justice 40 equity data layer.

## Web-app

The web-app is built on an EC2 server and is responsible for visualizing the high injury network on a live map. This section will guide you on how to interact with the server.

### Interacting with the EC2 server

To interact with the EC2 server, please follow these instructions:
```bash
<placeholder_instructions_for_interacting_with_ec2_server>
```
This will allow you to visualize the high injury network on a live map, making it easy for users to explore the data and modify the HIN functionality.



