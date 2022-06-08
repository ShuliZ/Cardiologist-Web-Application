import logging
import typing

import pandas as pd
import category_encoders as ce

logger = logging.getLogger(__name__)

def get_binary_data(
    df: pd.DataFrame,
    is_user_input: bool,
    binary_col: typing.List[str],
    binary_value: typing.List[str],
    target_col: str='HeartDisease') -> pd.DataFrame:
    """Change the columns of text values Yes and No to numeric.

    Args:
        df (`pd.DataFrame`): input dataframe for transformation
        is_user_input (bool): whether it is user inputs from the web or raw data
        binary_col (`list` of `str`): the list of columns that need transformation
        target_col (str): name of the target variable. Defaults to "HeartDisease"
        binary_value (`list` of `str`): the list of text values to be transformed

    Returns:
        df (`pd.DataFrame`): data frame with binary columns get transformed
    """
    if not is_user_input:
        binary_col += [target_col]
    for col in binary_col:
        df[col] = df[col].replace(binary_value,[0,1])
    return df

def get_ohe_data(
    df: pd.DataFrame,
    onehot_col: typing.List[str],
    required_col: typing.List[str]) -> pd.DataFrame:
    """Change the columns of text values to multiple columns of 0's and 1's

    Args:
        df (`pd.DataFrame`): input dataframe for transformation
        onehot_col (`list` of `str`): the list of columns that need transformation
        required_col (`list` of `str`): the required column names that should be included in the dataframe

    Returns:
        result (`pd.DataFrame`): data frame with one hot columns get transformed
    """
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


def get_ordinalenc_age(
    df: pd.DataFrame,
    age_col: str,
    age_mapping: typing.Dict) -> pd.DataFrame:
    """Change the column of age category into ordered numeric values

    Args:
        df (`pd.DataFrame`): input dataframe for transformation
        age_col (`str`): the age column name that needs transformation
        age_mapping (`dict`): mapping with keys of text and values of ordered numeric

    Returns:
        t_df (:obj:`DataFrame <pandas.DataFrame>`): data frame with age column get transformed
    """
    age_encoder= ce.OrdinalEncoder(cols=[age_col],
                                   return_df=True,
                                   mapping=[{'col': age_col,
                                                 'mapping': age_mapping}])
    t_df = age_encoder.fit_transform(df)

    return t_df

def get_ordinalenc_health(
    df: pd.DataFrame,
    health_col: str,
    health_mapping: typing.Dict) -> pd.DataFrame:
    """Change the column of general health into ordered numeric values

    Args:
        df (`pd.DataFrame`): input dataframe for transformation
        health_col (`str`): the general health column name that needs transformation
        health_mapping (`dict`): mapping with keys of text and values of ordered numeric

    Returns:
        t_df (`pd.DataFrame`): data frame with general health column get transformed
    """
    health_encoder = ce.OrdinalEncoder(cols=[health_col],
                                       return_df=True,
                                       mapping=[{'col': health_col,
                                                 'mapping': health_mapping}])
    t_df = health_encoder.fit_transform(df)
    return t_df

def featurize(
    input_df: pd.DataFrame,
    is_user_input: bool,
    config: typing.Dict,
    num_columns: typing.List[str]) -> pd.DataFrame:
    """Perform all of the feature engineering steps in combination

    Args:
        input_df (`pd.DataFrame`): input dataframe for feature engineering
        is_user_input (bool): whether the data is from user input or raw data
        config (`dict`): configurations for the feature engineering functions
        num_columns (`list` of `str`): columns that should have numerical values

    Returns:
        input_transform (`pd.DataFrame`): data frame after all feature engineering steps
    """
    # transform the user input into a pandas DataFrame
    for num in num_columns:
        input_df[num] = input_df[num].astype(float)
    trans = get_binary_data(input_df, is_user_input, **config['get_binary_data'])
    trans = get_ohe_data(trans,  **config['get_ohe_data'])
    trans = get_ordinalenc_age(trans, **config['get_ordinalenc_age'])
    input_transform = get_ordinalenc_health(trans, **config['get_ordinalenc_health'])
    logger.info('Completed input transformation')
    return input_transform
