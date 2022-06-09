import pytest

import pandas as pd
import numpy as np
import sklearn

from src.model import train_test_split, fit_model

TARGET_COL = 'HeartDisease'
RANDOM_STATE = 10
TEST_SIZE = 0.2

model_params = {
    'random_state': 10,
      'n_estimators': 100,
      'min_samples_split': 6,
      'min_samples_leaf': 4,
      'max_depth': 10
}
SAMPLING_STRAT = 'majority'
RAND_STATE = 10
MODEL_TYPE ='RandomForestClassifier'

def test_train_test_split_happy():
    """test whether the function train_test_split works as expected"""
    # create input dataframe
    df_in = pd.DataFrame(
        [[0, 0, 0],
       [1, 0, 0],
       [1, 0, 0]],
       index = [2, 5, 10],
       columns = ['HeartDisease','AlcoholDrinking','Stroke']
    )
    # create true outputs
    x_train_true = pd.DataFrame(
        [[0, 0],
        [0, 0]],
        index= [10, 5],
        columns = ['AlcoholDrinking', 'Stroke']
    )
    x_test_true = pd.DataFrame(
        [[0, 0]], index = [2], columns = ['AlcoholDrinking', 'Stroke']
    )
    y_train_true = np.array([1, 1])
    y_test_true = np.array([0])

    df_test = train_test_split(df_in, TARGET_COL,RANDOM_STATE,TEST_SIZE)
    # test whether the training and testing data are the same
    pd.testing.assert_frame_equal(x_train_true, df_test[0])
    pd.testing.assert_frame_equal(x_test_true, df_test[1])
    assert np.array_equal(y_train_true, df_test[2])
    assert np.array_equal(y_test_true, df_test[3])

def test_train_test_split_non_df():
    """test invalid input dataframe data type"""
    df_non = 'I am not a dataframe'
    # errors for wrong data frame type
    with pytest.raises(AttributeError):
        train_test_split(df_non,TARGET_COL,RANDOM_STATE,TEST_SIZE)


def test_fit_model_happy():
    """test whether the function fit_model works as expected"""
    # create true model
    true_model = sklearn.ensemble.RandomForestClassifier(**model_params)
    # create inputs for tests
    x_train = pd.DataFrame(
        [[26.58,1,0,0,20.0,30.0,0,9,1,1,8.0,1,0,0,0.0,0.0,0.0,0.0,1.0,0.0,1.0,0.0,1.0],
        [28.87,1,0,0,6.0,0.0,1,11,0,1,12.0,0,0,0,0.0,0.0,0.0,0.0,1.0,0.0,1.0,0.0,1.0],
        [34.30,1,0,0,30.0,0.0,1,8,0,0,15.0,1,0,0,0.0,0.0,0.0,0.0,1.0,0.0,1.0,0.0,1.0]],
         index = [2, 5, 10],
         columns = ['BMI', 'Smoking', 'AlcoholDrinking', 'Stroke',
        'PhysicalHealth', 'MentalHealth', 'DiffWalking', 'AgeCategory',
        'PhysicalActivity', 'GenHealth', 'SleepTime', 'Asthma', 'KidneyDisease',
        'SkinCancer', 'Race_Asian', 'Race_Black', 'Race_Hispanic', 'Race_Other',
        'Race_White', 'Diabetic_No, borderline diabetes', 'Diabetic_Yes',
        'Diabetic_Yes (during pregnancy)', 'Sex_Male']
    )
    y_train = np.array([0,1,1])
    test_model = fit_model(x_train,
                           y_train,
                           model_params,
                           SAMPLING_STRAT,
                           RAND_STATE,
                           MODEL_TYPE)
    # check whether the model type is correct
    assert isinstance(test_model, sklearn.ensemble.RandomForestClassifier)
    # check the parameters
    assert getattr(test_model, 'random_state') == getattr(true_model, 'random_state')
    assert getattr(test_model, 'n_estimators') == getattr(true_model, 'n_estimators')
    assert getattr(test_model, 'min_samples_split') == getattr(true_model, 'min_samples_split')
    assert getattr(test_model, 'min_samples_leaf') == getattr(true_model, 'min_samples_leaf')
    assert getattr(test_model, 'max_depth') == getattr(true_model, 'max_depth')


def test_fit_model_wrong_shape():
    """test wrong shape of the input dataframe"""
    x_train = pd.DataFrame(
        [[26.58,1,0,0,20.0,30.0,0,9,1,1,8.0,1,0,0,0.0,0.0,0.0,0.0,1.0,0.0,1.0,0.0,1.0],
        [28.87,1,0,0,6.0,0.0,1,11,0,1,12.0,0,0,0,0.0,0.0,0.0,0.0,1.0,0.0,1.0,0.0,1.0],
        [34.30,1,0,0,30.0,0.0,1,8,0,0,15.0,1,0,0,0.0,0.0,0.0,0.0,1.0,0.0,1.0,0.0,1.0]],
         index = [2, 5, 10],
         columns = ['BMI', 'Smoking', 'AlcoholDrinking', 'Stroke',
        'PhysicalHealth', 'MentalHealth', 'DiffWalking', 'AgeCategory',
        'PhysicalActivity', 'GenHealth', 'SleepTime', 'Asthma', 'KidneyDisease',
        'SkinCancer', 'Race_Asian', 'Race_Black', 'Race_Hispanic', 'Race_Other',
        'Race_White', 'Diabetic_No, borderline diabetes', 'Diabetic_Yes',
        'Diabetic_Yes (during pregnancy)', 'Sex_Male']
    )
    y_train = np.array([0,1])
    # test for unmatched shape of x_train and y_train inputs
    with pytest.raises(ValueError):
        fit_model(x_train,
                  y_train,
                  model_params,
                  SAMPLING_STRAT,
                  RAND_STATE,
                  MODEL_TYPE)