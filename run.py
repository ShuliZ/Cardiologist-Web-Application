"""Configures the subparsers for receiving command line arguments for each
 stage in the model pipeline and orchestrates their execution."""
import sys
import pickle
import argparse
import logging.config

import yaml
import pandas as pd

from config.flaskconfig import SQLALCHEMY_DATABASE_URI
from src.add_patients import create_db
from src.s3 import upload_file_to_s3, download_file_from_s3
from src.load import import_data
from src.feature import featurize
from src.model import train_model
from src.score import score, evaluate

logging.config.fileConfig("config/logging/local.conf")
logger = logging.getLogger("patient-pipeline")
# pylint: disable=W0622,C0200,W0703

if __name__ == "__main__":

    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(description="Create and/or add data to database")

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


    # Sub-parser for acquiring, cleaning, and running model pipeline
    sb_pipeline = subparsers.add_parser("run_model_pipeline",
                                        description="Acquire data, load data, "
                                                    "featurize data, and run model-pipeline")
    sb_pipeline.add_argument("--step", help="Which step to run",
                             choices=["acquire","load", "featurize", "train", "score", "evaluate"])
    sb_pipeline.add_argument("--input", "-i", default=None, nargs="*",
                             help="Path to input data (optional, default = None)")
    sb_pipeline.add_argument("--config", default="config/config.yaml",
                             help="Path to configuration file")
    sb_pipeline.add_argument("--output", "-o", default=None,
                             help="Path to save output (optional, default = None)")
    sb_pipeline.add_argument("--output_model", default=None,
                             help="Path to where to load/save the trained model object from/to (optional)")
    sb_pipeline.add_argument("--output_data", default=None,
                             help="Prefix of path for saving training and test features and targets (train step only)")

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == "create_db":
        create_db(args.engine_string)
    elif sp_used == "upload_file_to_s3":
        upload_file_to_s3(args.local_path, args.s3_path)
    elif sp_used == "run_model_pipeline":
        # load yaml configuration file
        try:
            with open(args.config, "r") as f:
                conf = yaml.load(f, Loader=yaml.FullLoader)
        # error when unable to find the config file
        except FileNotFoundError:
            logger.error("Configuration file from %s is not found", args.config)
            sys.exit(1)
        else:
            logger.info("Configuration file loaded from %s", args.config)

        # read input file to dataframe
        if args.input is not None:
            if len(args.input) == 1:
                if args.input[0].endswith("csv"):
                    try:
                        input = pd.read_csv(args.input[0])
                    # error when unable to find the input file
                    except FileNotFoundError:
                        logger.error("No such file or directory, please check the input file.")
                        sys.exit(1)
                    except pd.errors.ParserError:
                        logger.error("The input file has incorrect format")
                        sys.exit(1)
                    except pd.errors.EmptyDataError:
                        logger.error("The data frame is empty")
                        sys.exit(1)
                    else:
                        logger.info("Input data loaded from %s", args.input[0])
            else:
                input = []
                for i in range(len(args.input)):
                    # read csv
                    if args.input[i].endswith("csv"):
                        try:
                            input.append(pd.read_csv(args.input[i]))
                        # error when unable to find the input file
                        except FileNotFoundError:
                            logger.error("No such file or directory, please check the input file.")
                            sys.exit(1)
                        except pd.errors.ParserError:
                            logger.error("The input file has incorrect format")
                            sys.exit(1)
                        except pd.errors.EmptyDataError:
                            logger.error("The data frame is empty")
                            sys.exit(1)
                        else:
                            logger.info("Input data loaded from %s", args.input[i])
                    # load model
                    elif args.input[i].endswith("sav"):
                        try:
                            with open(args.input[i], "rb") as f:
                                model = pickle.load(f)
                        # common error
                        except pickle.UnpicklingError as error_msg:
                            logger.error(error_msg)
                            sys.exit(1)
                        # secondary errors
                        except (AttributeError,  EOFError, ImportError, IndexError) as error_msg:
                            logger.error(error_msg)
                            sys.exit(1)
                        # other errors
                        except Exception as error_msg:
                            logger.error(error_msg)
                            sys.exit(1)
                        else:
                            input.append(model)
                            logger.info("Model loaded from %s", args.input[i])
        # model pipeline
        if args.step == "acquire":
            download_file_from_s3(**conf["s3"]["download_file_from_s3"])
        elif args.step == "load":
            output = import_data(**conf["load"]["import_data"])
        elif args.step == "featurize":
            output = featurize(input, False, conf["feature"], **conf["feature"]["featurize"])
            logger.info("Feature engineering completed")
        elif args.step == "train":
            train_model(input, conf["model"], args.output_model, args.output_data)
        elif args.step == "score":
            output = score(input[0], input[1], **conf["score"]["score"])
        elif args.step == "evaluate":
            output = evaluate(input[0], input[1], **conf["score"]["evaluate"])

        if args.output is not None:
            if args.step == "evaluate":
                try:
                    # write all metrics to a file
                    with open(args.output, "w") as out_file:
                        out_file.write(output[0])
                        out_file.write(output[1])
                        out_file.write(output[2])
                        out_file.close()
                # handle errors when unable to write file
                except FileNotFoundError as error_msg:
                    logger.error(error_msg)
                    sys.exit(1)
                else:
                    logger.info("The evaluation results are recorded in %s", args.output)
            else:
                try:
                    # save intermediate artifacts in the model pipeline
                    output.to_csv(args.output, index=False)
                # error for incorrect output
                except AttributeError as error_msg:
                    logger.error(error_msg)
                    sys.exit(1)
                except TypeError as error_msg:
                    logger.error(error_msg)
                    sys.exit(1)
                else:
                    logger.info("Output saved to %s", args.output)
    else:
        parser.print_help()
