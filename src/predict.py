import logging
import pickle
import typing

import pandas as pd
import sklearn

logger = logging.getLogger(__name__)
# pylint: disable=W0703

def input_predict(df: pd.DataFrame,
                  rf_model: sklearn.base.BaseEstimator,
                  transformed_col: typing.List[str]) -> typing.List[str]:
    """return a list containing prediction labels and probabilities
    based on user input variables

    Args:
        df (`pd.DataFrame`): data frame representation of the user input
        rf_model (`sklearn.base.BaseEstimator`): the trained model used for prediction
        transformed_col (`list` of `str`): column names used as features for prediction

    Returns:
        predict_result (`list` of `str`): a list of prediction result
    """
    predict_result = []
    # predict the class with the new user input
    try:
        prediction = rf_model.predict(df[transformed_col])
        pred_prob = round(100 * rf_model.predict_proba(df[transformed_col])[:, 1][0])
    except KeyError as error_msg:
        logger.warning('The column names are not matched.')
        logger.error(error_msg)
        return predict_result
    except UnboundLocalError as error_msg:
        logger.error(error_msg)
        return predict_result
    # get the prediction class and probabilities
    else:
        if prediction == 1:
            pred_bin = 'You are LIKELY to have heart disease'
        else:
            pred_bin = 'You are NOT LIKELY to have heart disease'
        predict_result = [pred_prob, pred_bin]
        return predict_result

def predict(df: pd.DataFrame,
            config: typing.Dict,
            model_path: str) -> typing.List[str]:
    """perform prediction by loading the model from a specific path

    Args:
        df (`pd.DataFrame`): data frame representation of the user input variable
        config (`dict`): configuration used for input_predict
        model_path (`str`): the path to the trained model

    Returns:
        predict_result (`list` of `str`): a list of prediction result
    """
    # load pre-trained model
    try:
        with open(model_path, 'rb') as model_file:
            logger.info('Started import models.')
            loaded_rf = pickle.load(model_file)
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
    predict_result = input_predict(df, loaded_rf, **config['input_predict'])
    return predict_result
