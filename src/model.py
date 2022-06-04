"""
This module contains functions that perform
model training and evaluation
"""
import logging

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from imblearn.under_sampling import RandomUnderSampler

logger = logging.getLogger(__name__)

def train(trans_df, target, sampling_strat, rand_state, test_prop, n_estimate):
    X = trans_df.drop([target], axis=1)
    y = trans_df[[target]].values.ravel()

    # train test split
    x_train, x_test, y_train, y_test = train_test_split(X,y,test_size=test_prop,random_state=rand_state)

    # define oversampling strategy
    oversample = RandomUnderSampler(sampling_strategy=sampling_strat, random_state=rand_state)

    # fit and apply the transform
    x_under, y_under = oversample.fit_resample(x_train, y_train)

    # random forest model
    rf = RandomForestClassifier(n_estimators = n_estimate, random_state=rand_state)
    rf.fit(x_under, y_under)
    return [rf, x_test, y_test]


def evaluate(rf, x_test, y_test, save_path):
    clf_y_predict = rf.predict(x_test)
    cm  = confusion_matrix(y_test, clf_y_predict)
    tn, fp, fn, tp = cm.ravel()
    fnr = fn/(fn+tp)
    acc = (tn+tp) / (tn+fp+fn+tp)
    logger.info("False Negative Rate is %s", fnr)
    logger.info("Accuracy is %s", acc)
    try:
        eval_result = pd.DataFrame({"FNR": fnr, "ACC": acc}, index=[0])
        eval_result.to_csv(save_path, index=False)
        logger.info("Evaluation results saved to location: %s", save_path)
    except ValueError:
        logger.error("Failed to save the evaluation results because "
                     "the DataFrame of evaluation results cannot be appropriately called")
