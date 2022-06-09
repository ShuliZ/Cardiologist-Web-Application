import logging
import typing

import pandas as pd
import sklearn

logger = logging.getLogger(__name__)

def score(rf_model: sklearn.ensemble.RandomForestClassifier,
          test: pd.DataFrame,
          transformed_features: typing.List[str]) -> pd.DataFrame:
    """a function used for model prediction and returns predicted scores
        Args:
            rf_model (:obj:`sklearn.ensemble.RandomForestClassifier`)
            test (:obj:`pandas.DataFrame`): a full series of features for testing
            transformed_features (:obj:`list` of `str`): variables after feature engineering process
        Return:
            scored_df (:obj:`pandas.DataFrame`): a data frame that record the predicted results
    """
    # predict probability and class for each sample in the test set
    scored_df = pd.DataFrame()
    try:
        ypred_proba_test = rf_model.predict_proba(test[transformed_features])[:,1]
        ypred_bin_test = rf_model.predict(test[transformed_features])
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
             test: pd.DataFrame,
             target: str) -> typing.List[str]:
    """ a function used to calculate evaluation metrics and prepare for writing to files
        Args:
            scored_df (:obj:`pandas.DataFrame`): a data frame that record the predicted results
            test (:obj:`pandas.DataFrame`): test data frame from train test split
            target (`str`): name of target variable
        Return:
            output (`list` of `str`): a list of string representation of model performance metrics
    """
    y_test = test[target]
    # predict probability and class for each sample in the test set
    ypred_bin_test = scored_df['ypred_bin_test']
    # evaluation metrics
    confusion = sklearn.metrics.confusion_matrix(y_test, ypred_bin_test)
    accuracy = sklearn.metrics.accuracy_score(y_test, ypred_bin_test)
    false_neg = confusion.ravel()[2]
    true_pos = confusion.ravel()[3]
    fnr = false_neg/(false_neg+true_pos)
    logger.info('Completed evaluation of the Random Forest Classifier')

    # convert confusion matrix value to dataframe
    confusion_matrix = pd.DataFrame(confusion,
                       index=['Actual negative', 'Actual positive'],
                       columns=['Predicted negative', 'Predicted positive'])
    # convert dataframe to string for writting to output files
    df_string = confusion_matrix.to_string(header=True, index=True)
    wtrite_acc = 'Accuracy on test: ' + str(accuracy) + ' \n'
    write_fnr = 'False Negative Rate on test: ' + str(fnr) + ' \n'
    output = [wtrite_acc, write_fnr, df_string]
    return output
