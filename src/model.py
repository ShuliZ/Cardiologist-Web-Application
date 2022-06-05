"""
This module contains functions that perform
model training and evaluation
"""
import logging
import typing

import pandas as pd
import numpy as np
import sklearn
import matplotlib.pyplot as plt
import seaborn as sns
from imblearn.under_sampling import RandomUnderSampler

logger = logging.getLogger(__name__)

def train(trans_df, target, sampling_strat, rand_state, test_prop, n_estimate):
    X = trans_df.drop([target], axis=1)
    y = trans_df[[target]].values.ravel()

    # train test split
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(X,y,test_size=test_prop,random_state=rand_state)

    # define oversampling strategy
    undersample = RandomUnderSampler(sampling_strategy=sampling_strat, random_state=rand_state)

    # fit and apply the transform
    x_under, y_under = undersample.fit_resample(x_train, y_train)

    # random forest model
    rf = sklearn.ensemble.RandomForestClassifier(n_estimators = n_estimate, random_state=rand_state)
    rf.fit(x_under, y_under)
    return [rf, x_test, y_test]

def score(rf_model: sklearn.ensemble.RandomForestClassifier,
          x_test: pd.DataFrame,
          transformed_features: typing.List[str]) -> pd.DataFrame:
    """a function used for model prediction and returns predicted scores and labels
        Args:
            rf_model (:obj:`sklearn.ensemble.RandomForestClassifier`)
            x_test (:obj:`pandas.DataFrame`): a full series of features for testing
            transformed_features (:obj:`list` of `str`): variables after feature engineering process
        Return:
            scored_df (:obj:`pandas.DataFrame`): a data frame that record the predicted results
    """
    # predict probability and class for each sample in the test set
    scored_df = pd.DataFrame()
    try:
        ypred_proba_test = rf_model.predict_proba(x_test[transformed_features])[:,1]
        ypred_bin_test = rf_model.predict(x_test[transformed_features])
    # ValueError for incorrect initial_features
    except ValueError as error_msg:
        logger.error(error_msg)
        return scored_df
    # AttributeError for incorrect model input
    except AttributeError as error_msg:
        logger.error(error_msg)
        return scored_df

    scored_df['ypred_proba_test'] = ypred_proba_test
    scored_df['ypred_bin_test'] = ypred_bin_test
    logger.info('Completed prediction')
    return scored_df


def evaluate(scored_df: pd.DataFrame,
             y_test: pd.Series) -> None:
    """ a function used to save all evaluation metrics
        Args:
            scored_df (:obj:`pandas.DataFrame`): a data frame that record the predicted results
            y_test (:obj:`pandas.Series`): a series of target variable for testing
            save_path (str): path to save the model
        Return:
            None
    """
    # predict probability and class for each sample in the test set
    ypred_proba_test = scored_df['ypred_proba_test']
    ypred_bin_test = scored_df['ypred_bin_test']
    # evaluation metrics
    auc = sklearn.metrics.roc_auc_score(y_test, ypred_proba_test)
    confusion = sklearn.metrics.confusion_matrix(y_test, ypred_bin_test)
    accuracy = sklearn.metrics.accuracy_score(y_test, ypred_bin_test)
    tn, fp, fn, tp = confusion.ravel()
    fnr = fn/(fn+tp)
    logger.info('Completed evaluation of the Random Forest Classifier')

    # convert confusion matrix value to dataframe
    confusion_matrix = pd.DataFrame(confusion,
                       index=['Actual negative', 'Actual positive'],
                       columns=['Predicted negative', 'Predicted positive'])
    # convert dataframe to string for writting to output files
    df_string = confusion_matrix.to_string(header=True, index=True)
    wtrite_acc = 'Accuracy on test: {:0.3f} \n'.format(accuracy)
    write_fnr = 'False Negative Rate on test: {:0.3f} \n'.format(fnr)
    return [wtrite_acc, write_fnr, df_string]

def plot_feature_importance(rf_model, columns, save_path, top_n=15):

    #Create arrays from feature importance and feature names
    importance = rf_model.feature_importances_
    feature_importance = np.array(importance)
    feature_names = np.array(columns)

    #Create a DataFrame using a Dictionary
    data={'feature_names':feature_names,'feature_importance':feature_importance}
    fi_df = pd.DataFrame(data)

    #Sort the DataFrame in order decreasing feature importance
    fi_df.sort_values(by=['feature_importance'], ascending=False,inplace=True)
    fi_df = fi_df.iloc[:top_n,:]

    #Plot Searborn bar chart
    plt.figure(figsize=(10,8))
    sns.barplot(x=fi_df['feature_importance'], y=fi_df['feature_names'])
    plt.savefig(save_path)
    logger.info("Completed generating the plot for feature importance.")
