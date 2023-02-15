"""Combines all .csv datasets for each folder (intended for SDS data) into 1 `pd.DataFrame` per folder and writes to a single .csv file per folder.

Main function is combine_SDS_datasets. Helper functions take the folder path and get all .csv filenames, read a list of filenames into `pd.DataFrame` objects, and concatenate a list of `pd.DataFrame` objects into a single `pd.DataFrame`.

"""

import pandas as pd
import helper

# Dictionary of the list of columns retained for each state
SDS_columns = {
    "Massachusetts": 
                ['OBJECTID', 'CRASH_NUMB', 'CITY_TOWN_NAME', 'CRASH_DATE_TEXT', 'CRASH_DATE', 'CRASH_HOUR', 'CRASH_TIME_2', 'CRASH_STATUS', 'CRASH_SEVERITY_DESCR', 'MAX_INJR_SVRTY_CL', 'NUMB_VEHC', 'NUMB_NONFATAL_INJR', 'NUMB_FATAL_INJR', 'POLC_AGNCY_TYPE_DESCR', 'MANR_COLL_DESCR', 'VEHC_MNVR_ACTN_CL', 'VEHC_TRVL_DIRC_CL', 'VEHC_SEQ_EVENTS_CL', 'AMBNT_LIGHT_DESCR', 'WEATH_COND_DESCR', 'ROAD_SURF_COND_DESCR', 'FIRST_HRMF_EVENT_DESCR', 'MOST_HRMFL_EVT_CL', 'DRVR_CNTRB_CIRC_CL', 'VEHC_CONFIG_CL', 'STREET_NUMB', 'RDWY', 'DIST_DIRC_FROM_INT', 'NEAR_INT_RDWY', 'MM_RTE', 'DIST_DIRC_MILEMARKER', 'MILEMARKER', 'EXIT_RTE', 'DIST_DIRC_EXIT', 'EXIT_NUMB', 'DIST_DIRC_LANDMARK', 'LANDMARK', 'RDWY_JNCT_TYPE_DESCR', 'TRAF_CNTRL_DEVC_TYPE_DESCR', 'TRAFY_DESCR_DESCR', 'JURISDICTN', 'FIRST_HRMF_EVENT_LOC_DESCR', 'NON_MTRST_TYPE_CL', 'NON_MTRST_ACTN_CL', 'NON_MTRST_LOC_CL', 'IS_GEOCODED', 'GEOCODING_METHOD_NAME', 'X', 'Y', 'LAT', 'LON', 'RMV_DOC_IDS', 'CRASH_RPT_IDS', 'YEAR', 'AGE_DRVR_YNGST', 'AGE_DRVR_OLDEST', 'AGE_NONMTRST_YNGST', 'AGE_NONMTRST_OLDEST', 'DRVR_DISTRACTED_CL', 'DISTRICT_NUM', 'RPA_ABBR', 'VEHC_EMER_USE_CL', 'VEHC_TOWED_FROM_SCENE_CL', 'CNTY_NAME', 'FMCSA_RPTBL_CL', 'FMCSA_RPTBL', 'HIT_RUN_DESCR', 'LCLTY_NAME', 'ROAD_CNTRB_DESCR', 'SCHL_BUS_RELD_DESCR', 'SPEED_LIMIT', 'TRAF_CNTRL_DEVC_FUNC_DESCR', 'WORK_ZONE_RELD_DESCR', 'AADT', 'AADT_YEAR', 'PK_PCT_SUT', 'AV_PCT_SUT', 'PK_PCT_CT', 'AV_PCT_CT', 'CURB', 'TRUCK_RTE', 'LT_SIDEWLK', 'RT_SIDEWLK', 'SHLDR_LT_W', 'SHLDR_LT_T', 'SURFACE_WD', 'SURFACE_TP', 'SHLDR_RT_W', 'SHLDR_RT_T', 'NUM_LANES', 'OPP_LANES', 'MED_WIDTH', 'MED_TYPE', 'URBAN_TYPE', 'F_CLASS', 'URBAN_AREA', 'FD_AID_RTE', 'FACILITY', 'OPERATION', 'CONTROL', 'PEAK_LANE', 'SPEED_LIM', 'STREETNAME', 'FROMSTREETNAME', 'TOSTREETNAME', 'CITY', 'STRUCT_CND', 'TERRAIN', 'URBAN_LOC_TYPE', 'AADT_DERIV', 'STATN_NUM', 'OP_DIR_SL', 'SHLDR_UL_T', 'SHLDR_UL_W', 'T_EXC_TYPE', 'T_EXC_TIME', 'F_F_CLASS', 'CRASH_DATETIME', 'SHAPE', 'CRASH_TIME'],
    "California":
                ['CASE_ID', 'ACCIDENT_YEAR', 'PROC_DATE', 'JURIS', 'COLLISION_DATE', 'COLLISION_TIME', 'OFFICER_ID', 'REPORTING_DISTRICT', 'DAY_OF_WEEK', 'CHP_SHIFT', 'POPULATION', 'CNTY_CITY_LOC', 'SPECIAL_COND', 'BEAT_TYPE', 'CHP_BEAT_TYPE', 'CITY_DIVISION_LAPD', 'CHP_BEAT_CLASS', 'BEAT_NUMBER', 'PRIMARY_RD', 'SECONDARY_RD', 'DISTANCE', 'DIRECTION', 'INTERSECTION', 'WEATHER_1', 'WEATHER_2', 'STATE_HWY_IND', 'CALTRANS_COUNTY', 'CALTRANS_DISTRICT', 'STATE_ROUTE', 'ROUTE_SUFFIX', 'POSTMILE_PREFIX', 'POSTMILE', 'LOCATION_TYPE', 'RAMP_INTERSECTION', 'SIDE_OF_HWY', 'TOW_AWAY', 'COLLISION_SEVERITY', 'NUMBER_KILLED', 'NUMBER_INJURED', 'PARTY_COUNT', 'PRIMARY_COLL_FACTOR', 'PCF_CODE_OF_VIOL', 'PCF_VIOL_CATEGORY', 'PCF_VIOLATION', 'PCF_VIOL_SUBSECTION', 'HIT_AND_RUN', 'TYPE_OF_COLLISION', 'MVIW', 'PED_ACTION', 'ROAD_SURFACE', 'ROAD_COND_1', 'ROAD_COND_2', 'LIGHTING', 'CONTROL_DEVICE', 'CHP_ROAD_TYPE', 'PEDESTRIAN_ACCIDENT', 'BICYCLE_ACCIDENT', 'MOTORCYCLE_ACCIDENT', 'TRUCK_ACCIDENT', 'NOT_PRIVATE_PROPERTY', 'ALCOHOL_INVOLVED', 'STWD_VEHTYPE_AT_FAULT', 'CHP_VEHTYPE_AT_FAULT', 'COUNT_SEVERE_INJ', 'COUNT_VISIBLE_INJ', 'COUNT_COMPLAINT_PAIN', 'COUNT_PED_KILLED', 'COUNT_PED_INJURED', 'COUNT_BICYCLIST_KILLED', 'COUNT_BICYCLIST_INJURED', 'COUNT_MC_KILLED', 'COUNT_MC_INJURED', 'PRIMARY_RAMP', 'SECONDARY_RAMP', 'LATITUDE', 'LONGITUDE', 'Unnamed: 76']
    
}


def combine_SDS_datasets(path: str = '', output_path: str = 'SDS/Output/') -> pd.DataFrame:
    """Combines folders of SDS datasets in folder `path` into a single CSV file for each folder in `output_path`.

    Calls a series of helper functions, see their docstrings for specifics.
    
    Args: 
        path: A string specifying the folders where the CSVs will be loaded from. Defaults to 'FARS CSVs/'
        output_path: A string specifying the path to the directory where the combined CSV for each source folder will be saved. Defaults to 'SDS/Output/'

    Returns:
        A dictionary where the keys are the subdirectories of `path` and the values are the `pd.DataFrame` of all the CSV files contained within that folder.
    """

    all_dirs = helper.get_all_subdirectories(path = path)
    print("Full list of states: " + str(all_dirs))
    output = {}
    for state_dir in all_dirs:
        # print("Processing: "+state_dir)
        all_filenames = helper.get_all_filenames(path+state_dir,"*.csv")
        #get_all_dfs_from_csv(filenames: list[str], required_columns: list[str] = [], **kwargs)
        all_dfs_state = helper.get_all_dfs_from_csv(filenames=all_filenames, required_columns=SDS_columns[state_dir], encoding_errors='ignore', low_memory=False)
        combined_df = helper.concat_pandas_dfs(all_dfs_state)
        helper.write_dataframe_to_file(combined_df, output_path+state_dir+".csv")
        output[state_dir] = combined_df
    return combined_df

if __name__=="__main__":
    combine_SDS_datasets(path = 'SDS/Data/', output_path='SDS/Output/')