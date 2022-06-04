"""Configures the subparsers for receiving command line arguments for each
 stage in the model pipeline and orchestrates their execution."""
import os
import argparse
import logging.config

import yaml
import joblib
import pandas as pd

from config.flaskconfig import SQLALCHEMY_DATABASE_URI
from src.add_patients import create_db, PatientManager
from src.feature import get_binary_data, get_ohe_data, get_ordinalenc_age, get_ordinalenc_health
from src.model import train, evaluate
from src.s3 import upload_file_to_s3, download_file_from_s3

logging.config.fileConfig("config/logging/local.conf")
logger = logging.getLogger('patient-pipeline')

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


    # Sub-parser for ingesting new data
    sb_ingest = subparsers.add_parser("ingest", description="Add data to database")
    sb_ingest.add_argument("--id", help="patient ID")
    sb_ingest.add_argument("--bmi", help="")
    sb_ingest.add_argument("--smoking", help="")
    sb_ingest.add_argument("--alcohol_drinking", help="")
    sb_ingest.add_argument("--stroke", help="")
    sb_ingest.add_argument("--physical_health", help="")
    sb_ingest.add_argument("--mental_health", help="")
    sb_ingest.add_argument("--diff_walking", help="")
    sb_ingest.add_argument("--sex", help="")
    sb_ingest.add_argument("--age_category", help="")
    sb_ingest.add_argument("--race", help="")
    sb_ingest.add_argument("--diabetic", help="")
    sb_ingest.add_argument("--physical_activity", help="")
    sb_ingest.add_argument("--gen_health", help="")
    sb_ingest.add_argument("--sleep_time", help="")
    sb_ingest.add_argument("--asthma", help="")
    sb_ingest.add_argument("--kidney_disease", help="")
    sb_ingest.add_argument("--skin_cancer", help="")
    sb_ingest.add_argument("--engine_string", default='sqlite:///data/patient.db',
                           help="SQLAlchemy Connection URI for database")

    # Sub-parser for acquiring, cleaning, and running model pipeline
    sb_pipeline = subparsers.add_parser("run_model_pipeline",
                                        description="Acquire data, clean data, "
                                                    "featurize data, and run model-pipeline")
    sb_pipeline.add_argument("--step", help="Which step to run",
                             choices=["feature", "model", "test"])
    sb_pipeline.add_argument("--input", "-i", default=None,
                             help="Path to input data (optional, default = None)")
    sb_pipeline.add_argument("--config", default="config/config.yaml",
                             help="Path to configuration file")
    sb_pipeline.add_argument("--output", "-o", default=None,
                             help="Path to save output (optional, default = None)")


    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == "create_db":
        create_db(args.engine_string)
    elif sp_used == "upload_file_to_s3":
        upload_file_to_s3(args.local_path, args.s3_path)
    elif sp_used == "download_file_from_s3":
        download_file_from_s3(args.local_path, args.s3_path)
    elif sp_used == 'ingest':
        patient_manager = PatientManager(engine_string=args.engine_string)
        patient_manager.add_patient(
            args.id,
            args.bmi,
            args.smoking,
            args.alcohol_drinking,
            args.stroke,
            args.physical_health,
            args.mental_health,
            args.diff_walking,
            args.sex,
            args.age_category,
            args.race,
            args.diabetic,
            args.physical_activity,
            args.gen_health,
            args.sleep_time,
            args.asthma,
            args.kidney_disease,
            args.skin_cancer
        )
        patient_manager.close()
    elif sp_used == 'run_model_pipeline':
        # load yaml configuration file
        try:
            with open(args.config, "r") as f:
                conf = yaml.load(f, Loader=yaml.FullLoader)
                logger.info("Configuration file loaded from %s" % args.config)
        except FileNotFoundError:
            logger.error("Configuration file from %s is not found" % args.config)

        
        if args.input is not None:
            input = pd.read_csv(args.input)
            logger.info("Input data loaded from %s", args.input)
        if args.step == "feature":
            trans = get_binary_data(input, **conf["feature"]["get_binary_data"])
            trans = get_ohe_data(trans, **conf["feature"]["get_ohe_data"])
            trans = get_ordinalenc_age(trans, **conf["feature"]["get_ordinalenc_age"])
            output = get_ordinalenc_health(trans, **conf["feature"]["get_ordinalenc_health"])
            # output = normalization(trans)
            logger.info('Feature engineering completed')
        elif args.step == "model":
            fitted = train(input,**conf['model']["train"])
            output, x_test, y_test = fitted[0], fitted[1], fitted[2]
            # evaluate the model result
            evaluate(output, x_test, y_test, **conf['model']['evaluate'])
        elif args.step == 'test':
            os.system('pytest')

        if args.output is not None:
            if args.step != "model":
                # save intermediate artifacts in the model pipeline
                output.to_csv(args.output, index=False)
                logger.info("Output saved to %s", args.output)
            else:
                # save the trained model
                joblib.dump(output, args.output)
                logger.info("Trained model object saved to %s", args.output)
    else:
        parser.print_help()

