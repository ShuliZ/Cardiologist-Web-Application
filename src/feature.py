"""
This module contains functions that performs feature
engineering
"""
import logging

import pandas as pd
import category_encoders as ce

logger = logging.getLogger(__name__)

def get_binary_data(df, is_user_input, binary_col, target_col="HeartDisease"):
    if not is_user_input:
        binary_col += [target_col]
    for col in binary_col:
        df[col] = df[col].replace(['No','Yes'],[0,1])
    return df

def get_ohe_data(df, onehot_col, required_col):
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


def get_ordinalenc_age(df, age_col, age_mapping):
    age_encoder= ce.OrdinalEncoder(cols=[age_col],
                                   return_df=True,
                                   mapping=[{'col': age_col,
                                                 'mapping': age_mapping}])
    t_df = age_encoder.fit_transform(df)
    
    return t_df

def get_ordinalenc_health(df, health_col, health_mapping):
    health_encoder = ce.OrdinalEncoder(cols=[health_col], 
                                       return_df=True,
                                       mapping=[{'col': health_col,
                                                 'mapping': health_mapping}])
    t_df = health_encoder.fit_transform(df)
    return t_df

def featurize(input_df, is_user_input, config, num_columns):
    # transform the user input into a pandas DataFrame
    for num in num_columns:
        input_df[num] = input_df[num].astype(float)
    trans = get_binary_data(input_df, is_user_input, **config['get_binary_data'])
    trans = get_ohe_data(trans,  **config['get_ohe_data'])
    trans = get_ordinalenc_age(trans, **config['get_ordinalenc_age'])
    input_transform = get_ordinalenc_health(trans, **config['get_ordinalenc_health'])
    logger.info("Completed input transformation") 
    return input_transform