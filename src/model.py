import logging
import typing
import pickle

import pandas as pd
import sklearn
from imblearn.under_sampling import RandomUnderSampler

logger = logging.getLogger(__name__)


def train_test_split(df: pd.DataFrame,
                     target: str,
                     random_state: int,
                     test_size: float = 0.2) -> typing.Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """ Splits dataframe into train and test feature sets and targets.
    Args:
        df (`pd.DataFrame`): Data containing features and target
        target_col (`str`): Column containing target values/labels
        random_state (`int`): Random state to make split reproducible
        test_size (`float`): Fraction of set to randomly sample to create test data
    Returns:
        x_train (`pd.DataFrame`): Features for training dataset
        x_test (`pd.DataFrame`): Features for testing dataset
        y_train (`pd.Series`): True target values for training dataset
        y_test (`pd.Series`): True target values for testing dataset
    """
    # split features and target
    features = df.drop([target], axis=1)
    target = df[[target]].values.ravel()
    # train test split
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
        features, target, test_size=test_size, random_state=random_state)

    return x_train, x_test, y_train, y_test



def fit_model(x_train: pd.DataFrame,
              y_train: pd.Series,
              model_params: dict,
              sampling_strat: str,
              rand_state: int,
              model_type: str = 'RandomForestClassifier') -> sklearn.base.BaseEstimator:
    """Fits a random forest classification model
    Args:
        x_train (`pd.DataFrame`): Features for training dataset
        y_train (`pd.Series`): True target values for training dataset
        model_params (`dict`): Dictionary containing keyword arguments for model instantiation.
        sampling_strat (`str`): undersampling strategy
        rand_state (`int`): seed for the undersampling model
        model_type (`str`): Type of model to train. Default: 'RandomForestClassifier' Currently, this function is only
            set up to train a `sklearn` random forest classifier but could easily be extended in future such that
            multiple different model types could be trained with only a change in configuration.
    Returns:
        model (`sklearn.base.BaseEstimator`): Trained model object
    """

    # define undersampling strategy
    undersample = RandomUnderSampler(
        sampling_strategy=sampling_strat,random_state=rand_state)

    # fit and apply the transform
    x_under, y_under = undersample.fit_resample(x_train, y_train)

    # fit random forest classifier
    if model_type == 'RandomForestClassifier':
        model = sklearn.ensemble.RandomForestClassifier(**model_params)
    else:
        logger.error('`fit_model` not configured for %s model type. Currently only '
                     'configured for sklearn.ensemble.RandomForestClassifier', model_type)
        raise ValueError(f'`fit_model` not configured for {model_type} model type. Currently only '
                         'configured for sklearn.ensemble.RandomForestClassifier')

    model.fit(x_under, y_under)

    logger.info('Trained model object created:\n%s', str(model))

    return model


def train_model(data: pd.DataFrame, config: dict, out_model: str, out_data: str) -> None:
    """Orchestrate model training by creating train test split, training model,
    and writing out trained model object
    Args:
        data (`pd.DataFrame`): feature engineered data frame for modeling
        config (`dict`): configuration for splitting and training
        out_model (`str`): output model path
        out_data (`str`): output data path
    Returns:
        None
    """
    # train test split
    x_train, x_test, y_train, y_test = train_test_split(data, **config['train_test_split'])
    # model fitting
    model = fit_model(x_train, y_train, **config['fit_model'])
    # write model
    with open(out_model, 'wb') as file:
        try:
            pickle.dump(model, file)
        except pickle.PickleError:
            logger.error('Error while writing trained model object to %s', out_model)
        else:
            logger.info('Trained model object saved to %s', out_model)
    # wirte training and tetsting data frame
    target_col = config['train_test_split']['target']
    x_train[target_col] = y_train
    x_test[target_col] = y_test
    x_train.to_csv(f'{out_data}train.csv', index=False)
    logger.info('Training dataset saved to %s', f'{out_data}train.csv')

    x_test.to_csv(f'{out_data}test.csv', index=False)
    logger.info('Testing dataset saved to %s', f'{out_data}test.csv')
