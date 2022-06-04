"""
This module contains functions that performs feature
engineering
"""
import logging

import pandas as pd
import category_encoders as ce

logger = logging.getLogger(__name__)

def get_binary_data(df, binary_col):
    for col in binary_col:
        df[col] = df[col].replace(['No','Yes'],[0,1])
    return df


def get_ohe_data(df, onehot_col):
    """One Hot Encode variables in a DataFrame to prepare for modeling
    Args:

    Returns:
    """
    dummy_df = pd.get_dummies(df[onehot_col], drop_first=True)
    t_df = pd.concat([df.drop(onehot_col, axis=1), dummy_df], axis=1)
    return t_df


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

# def normalization(df):
#     scaler = MinMaxScaler()
#     names = df.columns
#     t_df = scaler.fit_transform(df)
#     scaled_df = pd.DataFrame(t_df, columns=names)
#     return scaled_df
