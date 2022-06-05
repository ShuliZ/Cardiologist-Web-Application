"""Configures the subparsers for receiving command line arguments for each
 stage in the model pipeline and orchestrates their execution."""
import os
import sys
import pickle
import argparse
import logging.config

import yaml
import pandas as pd

from config.flaskconfig import SQLALCHEMY_DATABASE_URI
from src.add_patients import create_db, PatientManager
from src.acquire import import_data
from src.feature import featurize
from src.model import train, score, evaluate, plot_feature_importance
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


    # Sub-parser for acquiring, cleaning, and running model pipeline
    sb_pipeline = subparsers.add_parser("run_model_pipeline",
                                        description="Acquire data, clean data, "
                                                    "featurize data, and run model-pipeline")
    sb_pipeline.add_argument("--step", help="Which step to run",
                             choices=["acquire", "featurize", "train", "score", "evaluate"])
    sb_pipeline.add_argument("--input", "-i", default=None, nargs="*",
                             help="Path to input data (optional, default = None)")
    sb_pipeline.add_argument("--config", default="config/config.yaml",
                             help="Path to configuration file")
    sb_pipeline.add_argument("--output", "-o", default=None, nargs="*",
                             help="Path to save output (optional, default = None)")
    
    # Sub-parser for plot feature importance
    sb_plot = subparsers.add_parser("plot_feature_importance",
                                        description="Generate bar plot for feature importance")

    sb_plot.add_argument("--input", "-i", default=None,
                             help="Path to input data (optional, default = None)")
    sb_plot.add_argument("--config", default="config/config.yaml",
                             help="Path to configuration file")

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == "create_db":
        create_db(args.engine_string)
    elif sp_used == "upload_file_to_s3":
        upload_file_to_s3(args.local_path, args.s3_path)
    elif sp_used == "download_file_from_s3":
        download_file_from_s3(args.local_path, args.s3_path)
    elif sp_used == 'run_model_pipeline':
        # load yaml configuration file
        try:
            # Load configuration file for parameters and tmo path
            with open(args.config, 'r') as f:
                conf = yaml.load(f, Loader=yaml.FullLoader)
        # error when unable to find the config file
        except FileNotFoundError:
            logger.error('Configuration file from %s is not found', args.config)
        else:
            logger.info('Configuration file loaded from %s', args.config)

        # read input file to dataframe
        if args.input is not None:
            if len(args.input) == 1:
                if args.input[0].endswith('csv'):
                    try:
                        input = pd.read_csv(args.input[0])
                    # error when unable to find the input file
                    except FileNotFoundError:
                        logger.error('No such file or directory, please check the input file.')
                        sys.exit(1)
                    except pd.errors.ParserError:
                        logger.error('The input file has incorrect format')
                        sys.exit(1)
                    except pd.errors.EmptyDataError:
                        logger.error('The data frame is empty')
                        sys.exit(1)
                    else:
                        logger.info('Input data loaded from %s', args.input[0])
            else:
                input = []
                for i in range(len(args.input)):
                    # read csv
                    if args.input[i].endswith('csv'):
                        try:
                            input.append(pd.read_csv(args.input[i]))
                        # error when unable to find the input file
                        except FileNotFoundError:
                            logger.error('No such file or directory, please check the input file.')
                            sys.exit(1)
                        except pd.errors.ParserError:
                            logger.error('The input file has incorrect format')
                            sys.exit(1)
                        except pd.errors.EmptyDataError:
                            logger.error('The data frame is empty')
                            sys.exit(1)
                        else:
                            logger.info('Input data loaded from %s', args.input[i])
                    # load model
                    elif args.input[i].endswith('sav'):
                        try:
                            with open(args.input[i], 'rb') as f:
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
        # model pipeline
        if args.step == "acquire":
            output = import_data(**conf["acquire"]["import_data"])
        elif args.step == "featurize":
            output = featurize(input, False, conf["feature"], **conf["feature"]["featurize"])
            logger.info('Feature engineering completed')
        elif args.step == "train":
            output = train(input,**conf['model']["train"])
        elif args.step == "score":
            output = score(input[0], input[1], **conf["model"]["score"])
        elif args.step == "evaluate":
            output = evaluate(input[0], input[1])
        elif args.step == "feature_importance":
            plot_feature_importance

        if args.output is not None:
            if args.step == 'train':
                # save the trained model
                try:
                    with open(args.output[0] ,'wb') as f:
                        pickle.dump(output[0], f)
                except pickle.PicklingError as error_msg:
                    logger.error(error_msg)
                    sys.exit(1)
                else:
                    logger.info('Trained model object saved to %s', args.output[0])
                
                try:
                    # save intermediate artifacts in the model pipeline

                    output[1].to_csv(args.output[1], index=False)
                    y_test = pd.DataFrame({"HeartDisease":output[2]})
                    y_test.to_csv(args.output[2], index=False)
                # error for incorrect output
                except AttributeError as error_msg:
                    logger.error(error_msg)
                    sys.exit(1)
                except TypeError as error_msg:
                    logger.error(error_msg)
                    sys.exit(1)
                else:
                    logger.info('Output saved to %s', args.output[1])
                    logger.info('Output saved to %s', args.output[2])
            elif args.step == 'evaluate':
                try:
                    # write all metrics to a file
                    with open(args.output[0], 'w') as out_file:
                        out_file.write(output[0])
                        out_file.write(output[1])
                        out_file.write(output[2])
                        out_file.close()
                # handle errors when unable to write file
                except FileNotFoundError as error_msg:
                    logger.error(error_msg)
                    sys.exit(1)
                else:
                    logger.info('The evaluation results are recorded in %s', args.output[0])
            else:
                try:
                    # save intermediate artifacts in the model pipeline
                    output.to_csv(args.output[0], index=False)
                # error for incorrect output
                except AttributeError as error_msg:
                    logger.error(error_msg)
                    sys.exit(1)
                except TypeError as error_msg:
                    logger.error(error_msg)
                    sys.exit(1)
                else:
                    logger.info('Output saved to %s', args.output[0])
    elif sp_used == "plot_feature_importance":
        # load yaml configuration file
        try:
            # Load configuration file for parameters and tmo path
            with open(args.config, 'r') as f:
                conf = yaml.load(f, Loader=yaml.FullLoader)
        # error when unable to find the config file
        except FileNotFoundError:
            logger.error('Configuration file from %s is not found', args.config)
        else:
            logger.info('Configuration file loaded from %s', args.config)

        # read input file to dataframe
        if args.input is not None:
            try:
                with open(args.input, 'rb') as f:
                    input = pickle.load(f)
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
                logger.info("The model is loaded from %s", args.input)
        plot_feature_importance(input, **conf["model"]["plot_feature_importance"])
    else:
        parser.print_help()

