"""
This module contains multiple functions that offer
user input transformation and prediction functionality
"""
import logging

import joblib
import pandas as pd
import numpy as np

from src.feature import get_binary_data, get_ordinalenc_age, get_ordinalenc_health

logger = logging.getLogger(__name__)

def input_onehot(df, onehot_col, required_col):
    onehot_df = df[onehot_col]
    non_onehot_df = df.drop(onehot_col, axis=1)
    output_df = pd.DataFrame(columns = required_col)
    for col in onehot_col:
        new_name = col + '_' + str(onehot_df[col].values[0])
        onehot_df = onehot_df.rename(columns={col: new_name})
        onehot_df[new_name] = onehot_df.shape[0] * [1]
    output_df = output_df.T.join(onehot_df.T).fillna(0).T
    result = pd.concat([non_onehot_df, output_df], axis=1)
    return result

def input_feature_engineer(ui_dict, num_col, binary_col, onehot_col, required_col, age_col, age_mapping, health_col, health_mapping):
    # transform the user input into a pandas DataFrame
    input_df = pd.DataFrame(ui_dict, index=[0])
    for num in num_col:
        input_df[num] = input_df[num].astype(float)
    trans = get_binary_data(input_df, binary_col)
    logger.debug("input_feature_engineer 2: %s", trans.values)
    trans = input_onehot(trans, onehot_col, required_col)
    logger.debug("input_feature_engineer 3: %s", trans.values)
    trans = get_ordinalenc_age(trans, age_col, age_mapping)
    logger.debug("input_feature_engineer 4: %s", trans.values)
    input_transform = get_ordinalenc_health(trans, health_col, health_mapping)
    logger.debug("input_feature_engineer 5: %s", input_transform.values)
    # input_transform = normalization(trans)
    # logger.debug("input_feature_engineer 6: %s", input_transform.values)
    logger.info("Completed input transformation") 
    return input_transform

def input_predict(df, model_path, transformed_col):
    # load pre-trained model
    try:
        loaded_rf = joblib.load(model_path)
        logger.info('Loaded model from %s', model_path)
    except OSError:
        logger.error('Model is not found from %s', model_path)

    # predict the class with the new user input
    try:
        logger.info("The column names are %s", df.columns)
        logger.info("The values are %s", df[transformed_col].values)
        prediction = loaded_rf.predict(df[transformed_col])
        pred_prob = np.round(100 * loaded_rf.predict_proba(df[transformed_col])[:, 1][0], 2)
    except KeyError as error_msg:
        logger.warning('The column names are not matched.')
        logger.error(error_msg)
    else:
        if prediction == 1:
            pred_bin = "You are LIKELY to have heart disease"
        else:
            pred_bin = "You are NOT LIKELY to have heart disease"
        return [pred_prob, pred_bin]