import pytest

import pandas as pd
import numpy as np
import sklearn

from src.model import train_test_split, fit_model

target_col = 'HeartDisease'
random_state = 10
test_size = 0.2

model_params = {
    'random_state': 10,
      'n_estimators': 100,
      'min_samples_split': 6,
      'min_samples_leaf': 4,
      'max_depth': 10
}
sampling_strat = 'majority'
rand_state = 10
model_type ='RandomForestClassifier'

def test_train_test_split_happy():
    df_in = pd.DataFrame(
        [[0, 0, 0],
       [1, 0, 0],
       [1, 0, 0]],
       index = [2, 5, 10],
       columns = ['HeartDisease','AlcoholDrinking','Stroke']
    )
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

    df_test = train_test_split(df_in, target_col,random_state,test_size)
    pd.testing.assert_frame_equal(x_train_true, df_test[0])
    pd.testing.assert_frame_equal(x_test_true, df_test[1])
    assert np.array_equal(y_train_true, df_test[2])
    assert np.array_equal(y_test_true, df_test[3])

def test_train_test_split_non_df():
   """test invalid input dataframe data type"""
   df_non = 'I am not a dataframe'
   # errors for wrong data frame type
   with pytest.raises(AttributeError):
       train_test_split(df_non,target_col,random_state,test_size)


def test_fit_model_happy():
    true_model = sklearn.ensemble._forest.RandomForestClassifier(**model_params)
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
                           sampling_strat,
                           rand_state,
                           model_type)

    assert isinstance(test_model, sklearn.ensemble._forest.RandomForestClassifier)
    assert getattr(test_model, 'random_state') == getattr(true_model, 'random_state')
    assert getattr(test_model, 'n_estimators') == getattr(true_model, 'n_estimators')
    assert getattr(test_model, 'min_samples_split') == getattr(true_model, 'min_samples_split')
    assert getattr(test_model, 'min_samples_leaf') == getattr(true_model, 'min_samples_leaf')
    assert getattr(test_model, 'max_depth') == getattr(true_model, 'max_depth')


def test_fit_model_wrong_shape():
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
    with pytest.raises(ValueError):
        fit_model(x_train,
                  y_train,
                  model_params,
                  sampling_strat,
                  rand_state,
                  model_type)
