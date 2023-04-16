import census_tracts_split
import preprocess_FARS_data
import preprocess_Justice40_data
import preprocess_SDS_data
import AWS.upload_data_to_RDS

if __name__ == "__main__":
    AWS.upload_data_to_RDS.upload_state_boundaries_to_RDS()
    AWS.upload_data_to_RDS.upload_mpo_boundaries_to_RDS()
    AWS.upload_data_to_RDS.upload_county_boundaries_to_RDS()

    preprocess_FARS_data.combine_FARS_datasets()
    preprocess_SDS_data.preprocess_SDS_datasets()
    preprocess_Justice40_data.preprocess_justice40_data()
    census_tracts_split.split_census_tracts()

    AWS.upload_data_to_RDS.upload_FARS_data_to_RDS()
    AWS.upload_data_to_RDS.upload_SDS_data_to_RDS
    AWS.upload_data_to_RDS.upload_Justice40_data_to_RDS()
    AWS.upload_data_to_RDS.upload_census_tract_boundaries_to_RDS()