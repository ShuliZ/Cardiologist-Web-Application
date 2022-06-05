"""
This module contains multiple functions that offer
user input transformation and prediction functionality
"""
import logging
import pickle

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def input_predict(df, model_path, transformed_col):
    # load pre-trained model
    try:
        with open(model_path, 'rb') as f:
            loaded_rf = pickle.load(f)
    # common error
    except pickle.UnpicklingError as error_msg:
        logger.error(error_msg)
    # secondary errors
    except (AttributeError,  EOFError, ImportError, IndexError) as error_msg:
        logger.error(error_msg)
    # other errors
    except Exception as error_msg:
        logger.error(error_msg)
    else:
        logger.info('Loaded model from %s', model_path)

    # predict the class with the new user input
    try:
        prediction = loaded_rf.predict(df[transformed_col])
        pred_prob = round(100 * loaded_rf.predict_proba(df[transformed_col])[:, 1][0])
        logger.debug("Pred prob is %s", pred_prob)
    except KeyError as error_msg:
        logger.warning('The column names are not matched.')
        logger.error(error_msg)
        return
    else:
        if prediction == 1:
            pred_bin = "You are LIKELY to have heart disease"
        else:
            pred_bin = "You are NOT LIKELY to have heart disease"
        return [pred_prob, pred_bin]