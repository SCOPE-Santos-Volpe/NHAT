"""This file generates (or regenerates) all of the structured data from the raw data, and uploads all of the data to the RDS.

Booleans do_uploading and do_generating select whether to upload and/or generate data.
"""
import AWS.upload_data_to_RDS
import census_tracts_split
import preprocess_FARS_data
import preprocess_Justice40_data
import preprocess_SDS_data

# Whether to upload to the real tables
AWS.upload_data_to_RDS.testing = False

do_uploading = True

do_generating = True


if __name__ == "__main__":
    # NOTE: We have not fully tested deleting everything from the database and re-uploading everything, because that would take a while and we have stuff to do.

    if (do_uploading):
        AWS.upload_data_to_RDS.upload_state_boundaries_to_RDS()
        AWS.upload_data_to_RDS.upload_mpo_boundaries_to_RDS()
        AWS.upload_data_to_RDS.upload_county_boundaries_to_RDS()

    if (do_generating):
        preprocess_FARS_data.combine_FARS_datasets()
        preprocess_SDS_data.preprocess_SDS_datasets()
        preprocess_Justice40_data.preprocess_justice40_data()
        census_tracts_split.split_census_tracts()

    if (do_uploading):
        AWS.upload_data_to_RDS.upload_FARS_data_to_RDS()
        AWS.upload_data_to_RDS.upload_SDS_data_to_RDS()
        AWS.upload_data_to_RDS.upload_Justice40_data_to_RDS()
        AWS.upload_data_to_RDS.upload_census_tract_boundaries_to_RDS()
