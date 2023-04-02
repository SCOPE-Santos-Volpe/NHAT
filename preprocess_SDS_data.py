"""Combines all .csv datasets for each folder (intended for SDS data) into 1 `pd.DataFrame` per folder and writes to a single .csv file per folder.

Main function is combine_SDS_datasets. Helper functions take the folder path and get all .csv filenames, read a list of filenames into `pd.DataFrame` objects, and concatenate a list of `pd.DataFrame` objects into a single `pd.DataFrame`.

https://massdot-impact-crashes-vhb.opendata.arcgis.com/datasets/MassDOT::2021-crashes/about

        * Using 10-15 attributes -> will provide the list
        1. Fatal / serious injury (FSI)
        * We care about the severity of the crash
        2. Date / time is important
        3. Lighting is big attribute because we work on road lighting
        4. Corridor level data (function of the road/road type, intersection related)
        5. Involvement Binary (yes/no) attribute -> pedestrian involved? Bicyclist involved?
        6. Aggressive driving, failure to yield, vehicle left the roadway


Desired columns:
    YEAR : int
    IS_FATAL :          int (one-hot)
    SEVERITY :          int (1-4 range)
        1 - Fatal
        2 - Injury (Severe)
        3 - Injury (Other Visible)
        4 - Injury (Complaint of Pain)
        0 - PDO
    IS_PED :            int (one-hot)
    IS_CYC :            int (one-hot)
    WEATHER_COND :      int (1-4 range)
        A - Clear
        B - Cloudy
        C - Rain
        D - Snow / Sleet / Hail
        E - Fog / Smog / Smoke
        -  - Other
    LIGHT_COND :        int (1-4 range)
        A - Daylight
        B - Dusk - Dawn
        C - Dark - Street Lights
        D - Dark - No Street Lights
        E - Dark - Unknown Street Lights
        -  - Other
    ROAD_COND :         int (1-4 range)
        A - Dry
        B - Wet / Water
        C - Snowy / Icy / Slush
        D - Slippery (Muddy, Oily, etc.)
        -  - Not Stated
    ROAD_NAME :         str 
    # ROAD_TYPE :         int (functional class)
    # VEHC_DIR :          char (E/W/N/S)
    IS_INTERSECTION :   int (one-hot)
    LAT:                int
    LON:                int


"""

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from geoalchemy2 import Geometry, WKTElement

import helper
from shapely.geometry import Point, Polygon, MultiPolygon, shape
from sqlalchemy import create_engine, Table, Column, Integer, String, text



# Establish sqlalchemy connection
conn_string = 'postgresql://scope_team:greenTea123@database-1.ci75bfibgs4e.us-east-1.rds.amazonaws.com/FARS'
db = create_engine(conn_string)
sqlalchemy_conn = db.connect()
print('Python connected to PostgreSQL via Sqlalchemy')

# Dictionary of the list of columns retained for each state
SDS_columns = {
    "Massachusetts": 
                ['OBJECTID', 'CRASH_NUMB', 'CITY_TOWN_NAME', 'CRASH_DATE_TEXT', 'CRASH_DATE', 'CRASH_HOUR', 'CRASH_TIME_2', 'CRASH_STATUS', 'CRASH_SEVERITY_DESCR', 'MAX_INJR_SVRTY_CL', 'NUMB_VEHC', 'NUMB_NONFATAL_INJR', 'NUMB_FATAL_INJR', 'POLC_AGNCY_TYPE_DESCR', 'MANR_COLL_DESCR', 'VEHC_MNVR_ACTN_CL', 'VEHC_TRVL_DIRC_CL', 'VEHC_SEQ_EVENTS_CL', 'AMBNT_LIGHT_DESCR', 'WEATH_COND_DESCR', 'ROAD_SURF_COND_DESCR', 'FIRST_HRMF_EVENT_DESCR', 'MOST_HRMFL_EVT_CL', 'DRVR_CNTRB_CIRC_CL', 'VEHC_CONFIG_CL', 'STREET_NUMB', 'RDWY', 'DIST_DIRC_FROM_INT', 'NEAR_INT_RDWY', 'MM_RTE', 'DIST_DIRC_MILEMARKER', 'MILEMARKER', 'EXIT_RTE', 'DIST_DIRC_EXIT', 'EXIT_NUMB', 'DIST_DIRC_LANDMARK', 'LANDMARK', 'RDWY_JNCT_TYPE_DESCR', 'TRAF_CNTRL_DEVC_TYPE_DESCR', 'TRAFY_DESCR_DESCR', 'JURISDICTN', 'FIRST_HRMF_EVENT_LOC_DESCR', 'NON_MTRST_TYPE_CL', 'NON_MTRST_ACTN_CL', 'NON_MTRST_LOC_CL', 'IS_GEOCODED', 'GEOCODING_METHOD_NAME', 'X', 'Y', 'LAT', 'LON', 'RMV_DOC_IDS', 'CRASH_RPT_IDS', 'YEAR', 'AGE_DRVR_YNGST', 'AGE_DRVR_OLDEST', 'AGE_NONMTRST_YNGST', 'AGE_NONMTRST_OLDEST', 'DRVR_DISTRACTED_CL', 'DISTRICT_NUM', 'RPA_ABBR', 'VEHC_EMER_USE_CL', 'VEHC_TOWED_FROM_SCENE_CL', 'CNTY_NAME', 'FMCSA_RPTBL_CL', 'FMCSA_RPTBL', 'HIT_RUN_DESCR', 'LCLTY_NAME', 'ROAD_CNTRB_DESCR', 'SCHL_BUS_RELD_DESCR', 'SPEED_LIMIT', 'TRAF_CNTRL_DEVC_FUNC_DESCR', 'WORK_ZONE_RELD_DESCR', 'AADT', 'AADT_YEAR', 'PK_PCT_SUT', 'AV_PCT_SUT', 'PK_PCT_CT', 'AV_PCT_CT', 'CURB', 'TRUCK_RTE', 'LT_SIDEWLK', 'RT_SIDEWLK', 'SHLDR_LT_W', 'SHLDR_LT_T', 'SURFACE_WD', 'SURFACE_TP', 'SHLDR_RT_W', 'SHLDR_RT_T', 'NUM_LANES', 'OPP_LANES', 'MED_WIDTH', 'MED_TYPE', 'URBAN_TYPE', 'F_CLASS', 'URBAN_AREA', 'FD_AID_RTE', 'FACILITY', 'OPERATION', 'CONTROL', 'PEAK_LANE', 'SPEED_LIM', 'STREETNAME', 'FROMSTREETNAME', 'TOSTREETNAME', 'CITY', 'STRUCT_CND', 'TERRAIN', 'URBAN_LOC_TYPE', 'AADT_DERIV', 'STATN_NUM', 'OP_DIR_SL', 'SHLDR_UL_T', 'SHLDR_UL_W', 'T_EXC_TYPE', 'T_EXC_TIME', 'F_F_CLASS', 'CRASH_DATETIME', 'SHAPE', 'CRASH_TIME'],
    #SEVERITY: Fatal, NonFatal, Property Damage Only, Other
    #
    "California":
                ['CASE_ID', 'ACCIDENT_YEAR', 'PROC_DATE', 'JURIS', 'COLLISION_DATE', 'COLLISION_TIME', 'OFFICER_ID', 'REPORTING_DISTRICT', 'DAY_OF_WEEK', 'CHP_SHIFT', 'POPULATION', 'CNTY_CITY_LOC', 'SPECIAL_COND', 'BEAT_TYPE', 'CHP_BEAT_TYPE', 'CITY_DIVISION_LAPD', 'CHP_BEAT_CLASS', 'BEAT_NUMBER', 'PRIMARY_RD', 'SECONDARY_RD', 'DISTANCE', 'DIRECTION', 'INTERSECTION', 'WEATHER_1', 'WEATHER_2', 'STATE_HWY_IND', 'CALTRANS_COUNTY', 'CALTRANS_DISTRICT', 'STATE_ROUTE', 'ROUTE_SUFFIX', 'POSTMILE_PREFIX', 'POSTMILE', 'LOCATION_TYPE', 'RAMP_INTERSECTION', 'SIDE_OF_HWY', 'TOW_AWAY', 'COLLISION_SEVERITY', 'NUMBER_KILLED', 'NUMBER_INJURED', 'PARTY_COUNT', 'PRIMARY_COLL_FACTOR', 'PCF_CODE_OF_VIOL', 'PCF_VIOL_CATEGORY', 'PCF_VIOLATION', 'PCF_VIOL_SUBSECTION', 'HIT_AND_RUN', 'TYPE_OF_COLLISION', 'MVIW', 'PED_ACTION', 'ROAD_SURFACE', 'ROAD_COND_1', 'ROAD_COND_2', 'LIGHTING', 'CONTROL_DEVICE', 'CHP_ROAD_TYPE', 'PEDESTRIAN_ACCIDENT', 'BICYCLE_ACCIDENT', 'MOTORCYCLE_ACCIDENT', 'TRUCK_ACCIDENT', 'NOT_PRIVATE_PROPERTY', 'ALCOHOL_INVOLVED', 'STWD_VEHTYPE_AT_FAULT', 'CHP_VEHTYPE_AT_FAULT', 'COUNT_SEVERE_INJ', 'COUNT_VISIBLE_INJ', 'COUNT_COMPLAINT_PAIN', 'COUNT_PED_KILLED', 'COUNT_PED_INJURED', 'COUNT_BICYCLIST_KILLED', 'COUNT_BICYCLIST_INJURED', 'COUNT_MC_KILLED', 'COUNT_MC_INJURED', 'PRIMARY_RAMP', 'SECONDARY_RAMP', 'LATITUDE', 'LONGITUDE', 'Unnamed: 76']
    
}

states_df = helper.load_df_from_csv(path='states.csv', low_memory = False)
# Dictionaries to convert the STATE_INITIAL to STATE_ID & STATE_NAME
# d_state_initial2id = dict(zip(states_df.state, states_df.id))
# d_state_initial2name = dict(zip(states_df.state, states_df.name))
# d_state_id2name = dict(zip(states_df.id, states_df.name))
d_state_name2id = dict(zip(states_df.name, states_df.id))
# d_state_name2initial = dict(zip(states_df.name, states_df.state))

class preprocess_SDS_data:
    def __init__(self) -> None:
        self.preprocess_func_dict = {
            'California': self.preprocess_CA_SDS,
            'Massachusetts': self.preprocess_MA_SDS
        }
        
        self.convert_column_type_dict = {"YEAR"              : int, 
                                        "IS_FATAL"          : int, 
                                        "SEVERITY"          : int, 
                                        "IS_PED"            : int,  
                                        "IS_CYC"            : int,
                                        "WEATHER_COND"      : str, 
                                        "LIGHT_COND"        : str, 
                                        "ROAD_COND"         : str, 
                                        "ROAD_NAME"         : str, 
                                        "IS_INTERSECTION"   : int,
                                        "LAT"               : float,
                                        "LON"               : float,
            }
    


    # TODO: rename this to preprocess_SDS_datasets
    def preprocess_SDS_datasets(self, path: str = 'SDS/Data/', output_path: str = 'SDS/Output/') -> dict[str,pd.DataFrame]:
        """Combines folders of SDS datasets in folder `path` into a single CSV file for each folder in `output_path`. Also runs the sppropriate preprocessing function for each state

        Args: 
            path: A string specifying the folders where the CSVs will be loaded from. Defaults to 'FARS CSVs/'
            output_path: A string specifying the path to the directory where the combined CSV for each source folder will be saved. Defaults to 'SDS/Output/'

        Returns:
            A dictionary where the keys are the subdirectories of `path` and the values are the `pd.DataFrame` of all the CSV files contained within that folder.
        """

        all_dirs = helper.get_all_subdirectories(path = path)
        print("Full list of states: " + str(all_dirs))
        output = {}
        for state in all_dirs:
            print("Processing: "+state)
            all_filenames = helper.get_all_filenames(path+state,"*.csv")

            all_dfs_state = helper.get_all_dfs_from_csv(all_filenames, index_col=None, encoding_errors='ignore', low_memory=False)
            for df in all_dfs_state:
                df.columns =  df.columns.str.upper()
            df = helper.concat_pandas_dfs(all_dfs_state)

            # Run preprocessing function for the particular state
            if state in self.preprocess_func_dict:
                df = self.preprocess_func_dict[state](df)
                df = self.convert_columns_to_proper_types(df)
                df = self.remove_invalid_lat_lon(df)
                # Create the geometry column
                df = self.create_geometry_column_from_lat_lon(df)

            helper.write_dataframe_to_file(df, output_path+state+".csv")
            output[state] = df
        return output

    def preprocess_MA_SDS(self, df:pd.DataFrame) -> pd.DataFrame:
        """
        """
  
        # df = helper.load_df_from_csv('SDS/Output/Massachusetts.csv')

        columns = [ 'YEAR',                                                         # Metadata
                    'MAX_INJR_SVRTY_CL', 'NUMB_FATAL_INJR', 'NUMB_NONFATAL_INJR',   # Injury level
                    'AMBNT_LIGHT_DESCR', 'WEATH_COND_DESCR', 'ROAD_SURF_COND_DESCR', # Accident conditions
                    'RDWY', 'RDWY_JNCT_TYPE_DESCR', 'F_CLASS', 'F_F_CLASS',         # Road type
                    'LAT', 'LON',                                                   # Geolocation
                    'NON_MTRST_TYPE_CL', 'NON_MTRST_ACTN_CL', 'NON_MTRST_LOC_CL',   # Parties involved
        ]
        df = df[columns]

        # Make sure columns are string types
        df['WEATH_COND_DESCR'] = df['WEATH_COND_DESCR'].astype(str)
        df['NON_MTRST_TYPE_CL'] = df['NON_MTRST_TYPE_CL'].astype(str)
        df['ROAD_SURF_COND_DESCR'] = df['ROAD_SURF_COND_DESCR'].astype(str)   
        df['RDWY_JNCT_TYPE_DESCR'] = df['RDWY_JNCT_TYPE_DESCR'].astype(str)   
        df['MAX_INJR_SVRTY_CL'] = df['MAX_INJR_SVRTY_CL'].astype(str)   

        renames = {
            'RDWY' : 'ROAD_NAME',
        }
        df.rename(columns = renames,inplace = True)

        # Create appropriate columns

        def is_fatal(row):
            if row['NUMB_FATAL_INJR'] > 0:
                return 1
            return 0
        df['IS_FATAL'] = df.apply(lambda row: is_fatal(row), axis=1)

        def severity(row):
            """
                1 - Fatal
                2 - Injury (Severe)
                3 - Injury (Other Visible)
                4 - Injury (Complaint of Pain)
                0 - PDO
            """
            severity_str = row['MAX_INJR_SVRTY_CL']
            if "No injury" in severity_str or "No Apparent Injury (O)" in severity_str:
                return 0
            elif "Non-fatal injury - Possible" in severity_str or "Non-fatal injury - Non-incapacitating" in severity_str or "Suspected Minor Injury" in severity_str :
                return 4
            elif "Possible Injury" in severity_str or "Non-fatal injury - Incapacitating" in severity_str:
                return 3
            elif "Suspected Serious Injury" in severity_str:
                return 2
            elif "Fatal injury" in severity_str:
                return 1
            return 0
        df['SEVERITY'] = df.apply(lambda row: severity(row), axis=1)

        def is_ped(row: pd.Series):
            if "Pedestrian" in row['NON_MTRST_TYPE_CL']:
                return 1
            return 0
        df['IS_PED'] = df.apply(lambda row: is_ped(row), axis=1)

        def is_cyc(row: pd.Series):
            if "Cyclist" in row['NON_MTRST_TYPE_CL']:
                return 1
            return 0
        df['IS_CYC'] = df.apply(lambda row: is_cyc(row), axis=1)

        def is_intersection(row: pd.Series):
            junction_str = row['RDWY_JNCT_TYPE_DESCR'].lower()
            if "intersection" in junction_str:
                return 1
            return 0
        df['IS_INTERSECTION'] = df.apply(lambda row: is_intersection(row), axis=1)

        def weather_cond(row: pd.Series):
            weather_str = row['WEATH_COND_DESCR'].lower()
            if "fog" in weather_str or "smog" in weather_str or "smoke" in weather_str:
                return "E"
            elif "snow" in weather_str or "sleet" in weather_str or "hail" in weather_str:
                return "D"
            elif "rain" in weather_str:
                return "C"
            elif "cloudy" in weather_str:
                return "B"
            elif "clear" in weather_str:
                return "A"
            else:
                return "-"
        df['WEATHER_COND'] = df.apply(lambda row: weather_cond(row), axis=1)
 
        def light_cond(row: pd.Series):
            light_str = row['AMBNT_LIGHT_DESCR'].lower()
            if "daylight" in light_str:
                return "A"
            elif "dusk" in light_str or "dawn" in light_str:
                return "B"
            elif "dark - lighted roadway" in light_str:
                return "C"
            elif "dark - roadway not lighted" in light_str:
                return "D"
            elif "dark - unknown roadway lighting" in light_str:
                return "E"
            else:
                return "-"
        df['LIGHT_COND'] = df.apply(lambda row: light_cond(row), axis=1)

        def road_cond(row: pd.Series):
            road_surf_str = row['ROAD_SURF_COND_DESCR'].lower()
            if "dry" in road_surf_str:
                return "A"
            elif "wet" in road_surf_str or  "water" in road_surf_str:
                return "B"
            elif "ice" in road_surf_str or "snow" in road_surf_str or "slush" in road_surf_str:
                return "C"
            elif "oil" in road_surf_str or "mud" in road_surf_str:
                return "D"
            else:
                return "-"
        df['ROAD_COND'] = df.apply(lambda row: road_cond(row), axis=1)
        
        # Trim columns again
        new_columns = ["YEAR", "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON"]
        df = df[new_columns]
        
        # print("unique: ", df['MAX_INJR_SVRTY_CL'].unique())
        # print("number injury: ", df['MAX_INJR_SVRTY_CL'].value_counts())
        # print("number cyc: ", df['IS_CYC'].value_counts())

        return df

    def preprocess_CA_SDS(self, df:pd.DataFrame) -> pd.DataFrame:
        # df = helper.load_df_from_csv('SDS/Output/California.csv')
        columns = ['ACCIDENT_YEAR',                                                 # Metadata
                    'COLLISION_SEVERITY', 'NUMBER_KILLED', 'NUMBER_INJURED',        # Injury level
                    'WEATHER_1','ROAD_SURFACE', 'ROAD_COND_1', 'LIGHTING',          # Accident conditions
                    'PRIMARY_RD', 'SECONDARY_RD', 'DIRECTION', 'INTERSECTION',      # Road type
                    'LATITUDE', 'LONGITUDE',                                        # Geolocation
                    'PEDESTRIAN_ACCIDENT', 'BICYCLE_ACCIDENT', 'MOTORCYCLE_ACCIDENT', 'TRUCK_ACCIDENT', # Parties involved
                    'PRIMARY_COLL_FACTOR', 'TYPE_OF_COLLISION', 'ALCOHOL_INVOLVED'  # Accident reason
        ]
        columns = [x.upper() for x in columns]
        df = df[columns]

        renames = {
            'ACCIDENT_YEAR' : 'YEAR',
            'COLLISION_SEVERITY' : 'SEVERITY',
            'ROAD_SURFACE' : 'ROAD_COND',
            'PRIMARY_RD' : 'ROAD_NAME',
            'LIGHTING' : 'LIGHT_COND',
            'LATITUDE' : 'LAT',
            'LONGITUDE' : 'LON'
        }
        df.rename(columns = renames,inplace = True)

        def is_fatal(row):
            if row['NUMBER_KILLED'] > 0:
                return 1
            return 0
        df['IS_FATAL'] = df.apply(lambda row: is_fatal(row), axis=1)
        
        def is_ped(row: pd.Series):
            str = row['PEDESTRIAN_ACCIDENT']
            if str == "Y":
                return 1
            return 0
        df['IS_PED'] = df.apply(lambda row: is_ped(row), axis=1)

        def is_cyc(row: pd.Series):
            str = row['BICYCLE_ACCIDENT']
            if str == "Y":
                return 1
            return 0
        df['IS_CYC'] = df.apply(lambda row: is_cyc(row), axis=1)

        def weather_cond(row: pd.Series):
            weather_str = row['WEATHER_1']
            if weather_str == "F" or weather_str == "G":
                return "-"
            return weather_str
        df['WEATHER_COND'] = df.apply(lambda row: weather_cond(row), axis=1)

        def is_intersection(row: pd.Series):
            str = row['INTERSECTION']
            if str == "Y":
                return 1
            return 0
        df['IS_INTERSECTION'] = df.apply(lambda row: is_intersection(row), axis=1)

        # Trim columns again
        new_columns = ["YEAR", "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON"]
        df = df[new_columns]
        
        return df

    def convert_columns_to_proper_types(self, df:pd.DataFrame) -> pd.DataFrame:
        """ Convert columns to the proper types
        """
        # Drop all lat lon that are not numberic
        # df = df[df.f.apply(lambda x: x.isnumeric())]
        df = df[pd.to_numeric(df['LAT'], errors='coerce').notnull()]
        df = df[pd.to_numeric(df['LON'], errors='coerce').notnull()]

        df = df.astype(self.convert_column_type_dict)

        print(df.dtypes)
        return df

    def remove_invalid_lat_lon(self, df:pd.DataFrame) -> pd.DataFrame:
        """ Takes a preprocessed SDS data and remove points with invalid latitude and longitudes
        """
        # Valid lat and lon range
        lat_range = [-90, 90]
        lon_range = [-180, 180]

        print("LENGTH BEFORE DROPPING: ", df.shape[0])
        # Drop NAs
        df = df.dropna(subset=['LAT', 'LON'], how='all')
        print("LENGTH AFTER DROPPING NANS: ", df.shape[0])

        return df
    
    def create_point_column_from_lat_lon(self, df: pd.DataFrame):
        """ Generate a Point geometry column using latitude and longitude
            We want to use this because then we can use shapely to determine 
            whether each of the points 
        """

        
        gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df['LON'], df['LAT']), crs="EPSG:4269")

        # gdf['geom'] = gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=4269))
        # gdf.drop(columns='geometry', axis=1, inplace=True)
        # gdf.set_geometry('geom')

        return gdf

    def label_SDS_with_MPO_and_county_identifiers(self, state_name):
        """ Loop through all MPO shapefiles and check whether each point is inside the polygon boundary
        """
        # Get SDS data
        processed_SDS_path = 'SDS/Output/' + state_name + '.csv'
        SDS_df = helper.load_df_from_csv(processed_SDS_path)
        print("Got SDS data")
        SDS_df['MPO_ID'] = np.nan
        SDS_df['COUNTY_ID'] = np.nan

        # Create point column from lat_long
        SDS_df = self.create_point_column_from_lat_lon(SDS_df, flip_lon_sign = False)
        # Create MPO_ID and COUNTY_ID columns
        print("made point columns from lat long")
        print(SDS_df.head)

        # Convert state name to state id
        state_id = d_state_name2id[state_name]
       
        # Get all County boundaries
        print("Getting all County boundaries for state_id: ", state_id)
        sql = text(""" SELECT * FROM "boundaries_county" WHERE "STATE_ID" = {} """.format(state_id))
        county_boundaries = gpd.read_postgis(sql, con=sqlalchemy_conn)
        print("Got all County boundaries")
        print(county_boundaries.head)

        # Get all MPO boundaries
        print("Getting all MPO boundaries for state_id: ", state_id)
        sql = text(""" SELECT * FROM "boundaries_mpo" WHERE "STATE_ID" = {} """.format(state_id))
        mpo_boundaries = gpd.read_postgis(sql, con=sqlalchemy_conn)
        print("Got all MPO boundaries")
        print(mpo_boundaries.head)

        # Perform a spatial join between SDS and county boundaries
        SDS_with_county = gpd.sjoin(SDS_df,county_boundaries, predicate='intersects', how='left')
        columns = ["YEAR", 'COUNTY_ID_right', "COUNTY_NAME", "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON", "geometry"]
        SDS_with_county = SDS_with_county[columns]
        renames = {'COUNTY_ID_right' : 'COUNTY_ID'}
        SDS_with_county.rename(columns = renames,inplace = True)

        # Perform a spatial join between SDS and mpo boundaries
        SDS_with_MPOs = gpd.sjoin(SDS_with_county,mpo_boundaries, predicate='intersects', how='left')
        columns = ["YEAR", 'COUNTY_ID', "COUNTY_NAME", "MPO_ID", "MPO_NAME", "IS_FATAL", "SEVERITY", "IS_PED", "IS_CYC", "WEATHER_COND", "LIGHT_COND", "ROAD_COND", "ROAD_NAME", "IS_INTERSECTION", "LAT", "LON", "geometry"]
        SDS_with_MPOs = SDS_with_MPOs[columns]
        
        # Write updated geojson to file
        helper.write_dataframe_to_file(SDS_with_MPOs, "SDS/Output_w_MPO_County_Identifiers/"+state_name+".csv")


    def point_is_within_boundaries(self, pt: Point, poly: Polygon):
        """ Determines whether a lat lon point is within a boundary
        """

        # p1 = Point(24.952242, 60.1696017)
        # p2 = Point(24.976567, 60.1612500)

        # # Create a Polygon
        # coords = [(24.950899, 60.169158), (24.953492, 60.169158), (24.953510, 60.170104), (24.950958, 60.169990)]
        # Polygon ((-120.072484 38.509869, -120.072566 38.447081, -120.05365 38.455607, -120.019951 38.433521, -119.884749 38.356185, -119.869667 38.367597, -119.837551 38.382411, -119.814691 38.387516, -119.801737 38.401321, -119.770553 38.406663, -119.753481 38.416759, -119.705385 38.416102, -119.698671 38.409838, -119.693622 38.378899, -119.700029 38.365215, -119.669524 38.348288, -119.639205 38.32688, -119.628295 38.349733, -119.635575 38.353908, -119.607395 38.366458, -119.622093 38.393875, -119.601212 38.405354, -119.592409 38.398877, -119.561995 38.410734, -119.570009 38.43486, -119.556426 38.447465, -119.555863 38.470242, -119.542367 38.481657, -119.542862 38.499694, -119.556616 38.501702, -119.556217 38.516621, -119.568055 38.537707, -119.587367 38.558354, -119.599815 38.593348, -119.619237 38.604501, -119.614658 38.665879, -119.598647 38.670942, -119.579518 38.705609, -119.585437 38.713212, -119.587066 38.714345, -119.587679 38.714734, -119.904315 38.933324, -119.887643 38.918295, -119.879516 38.887021, -119.888444 38.879301, -119.877287 38.870193, -119.891909 38.857344, -119.906779 38.854664, -119.908493 38.834346, -119.92271 38.829955, -119.92186 38.820962, -119.942108 38.80311, -119.947927 38.781642, -119.964948 38.775986, -120.072392 38.702767, -120.072484 38.509869))
        # POINT (119.78938 34.44396)

        # poly = Polygon(coords)

        # print(pt)
        # print(poly)
        poly

        if poly.contains(pt):
            return True
        return False



if __name__=="__main__":
    preprocessor = preprocess_SDS_data()
    # preprocessor.preprocess_SDS_datasets()
    # preprocessor.label_SDS_with_MPO_and_county_identifiers("California")
    # preprocessor.label_SDS_with_MPO_and_county_identifiers("Massachusetts")
    # df = helper.load_df_from_csv('SDS/Output/California.csv')

    # df = preprocessor.preprocess_CA_SDS()
    # print("converting columns to proper types")
    # df = preprocessor.convert_columns_to_proper_types(df)
    # df = preprocessor.remove_invalid_lat_lon(df)
    # df = preprocessor.preprocess_MA_SDS()
    # print(df)

    