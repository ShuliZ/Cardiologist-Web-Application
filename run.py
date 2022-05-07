"""Configures the subparsers for receiving command line arguments for each
 stage in the model pipeline and orchestrates their execution."""
import argparse
import logging.config

from config.flaskconfig import SQLALCHEMY_DATABASE_URI
from src.add_patients import create_db
from src.s3 import upload_file_to_s3, download_file_from_s3

logging.config.fileConfig("config/logging/local.conf")
# logger = logging.getLogger('patient-pipeline')

if __name__ == "__main__":

    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    # parser.add_argument('--config', default='config/config.yaml',
    #                     help='Path to configuration file')

    subparsers = parser.add_subparsers(dest="subparser_name")

    # Sub-parser for creating a database
    sp_create = subparsers.add_parser("create_db",
                                      description="Create database")
    sp_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # Sub-parser for uploading data to s3
    sp_upload = subparsers.add_parser("upload_file_to_s3",
                                      description="Upload data to s3")
    sp_upload.add_argument("--s3_path",
                           default="s3://2022-msia423-zhu-shuli/data/heart_2020_cleaned.csv",
                           help="S3 path to upload files to")
    sp_upload.add_argument("--local_path",
                            default="data/sample/heart_2020_cleaned.csv",
                            help="Local path of the file to be uploaded")

    # Sub-parser for downloading data from s3
    sp_download = subparsers.add_parser("download_file_from_s3",
                                      description="Download data from s3")
    sp_download.add_argument("--s3_path",
                             default="s3://2022-msia423-zhu-shuli/data/heart_2020_cleaned.csv",
                             help="S3 path to download files from")
    sp_download.add_argument("--local_path",
                           default="data/sample/heart_2020_cleaned.csv",
                           help="Local path to download files to")

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == "create_db":
        create_db(args.engine_string)
    elif sp_used == "upload_file_to_s3":
        upload_file_to_s3(args.local_path, args.s3_path)
    elif sp_used == "download_file_from_s3":
        download_file_from_s3(args.local_path, args.s3_path)
    else:
        parser.print_help()
