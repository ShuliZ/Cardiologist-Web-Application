import pytest
import pickle

import pandas as pd

from src.score import score, evaluate

transformed_col = ['BMI','Smoking','AlcoholDrinking','Stroke','PhysicalHealth',
                   'MentalHealth','DiffWalking','AgeCategory','PhysicalActivity',
                   'GenHealth','SleepTime','Asthma','KidneyDisease','SkinCancer',
                   'Race_Asian','Race_Black','Race_Hispanic','Race_Other','Race_White',
                   'Diabetic_No, borderline diabetes','Diabetic_Yes',
                   'Diabetic_Yes (during pregnancy)','Sex_Male']

test = pd.DataFrame(
        [[0, 26.58,1,0,0,20.0,30.0,0,9,1,1,8.0,1,0,0,0.0,0.0,0.0,0.0,1.0,0.0,1.0,0.0,1.0],
        [1, 28.87,1,0,0,6.0,0.0,1,11,0,1,12.0,0,0,0,0.0,0.0,0.0,0.0,1.0,0.0,1.0,0.0,1.0],
        [1, 34.30,1,0,0,30.0,0.0,1,8,0,0,15.0,1,0,0,0.0,0.0,0.0,0.0,1.0,0.0,1.0,0.0,1.0]],
         columns = ['HeartDisease','BMI', 'Smoking', 'AlcoholDrinking', 'Stroke',
        'PhysicalHealth', 'MentalHealth', 'DiffWalking', 'AgeCategory',
        'PhysicalActivity', 'GenHealth', 'SleepTime', 'Asthma', 'KidneyDisease',
        'SkinCancer', 'Race_Asian', 'Race_Black', 'Race_Hispanic', 'Race_Other',
        'Race_White', 'Diabetic_No, borderline diabetes', 'Diabetic_Yes',
        'Diabetic_Yes (during pregnancy)', 'Sex_Male']
    )

target = 'HeartDisease'

def test_score_happy():
    df_true = pd.DataFrame(
        [[0.73455538, 1],
        [0.81894559, 1],
        [0.79067556, 1]],
        columns = ['ypred_proba_test','ypred_bin_test']
    )
    with open('models/rf.sav', 'rb') as f:
        loaded_rf = pickle.load(f)
    df_test = score(loaded_rf, test, transformed_col)
     # Test that the true and test are the same
    pd.testing.assert_frame_equal(df_true, df_test)


def test_score_non_model():
    """test invalid data type"""
    loaded_rf = 'I am not a model'

    expected = pd.DataFrame()
    df_test = score(loaded_rf, test, transformed_col)
    pd.testing.assert_frame_equal(expected, df_test)


def test_evaluate_happy():
    score_df = pd.DataFrame(
        [[0.73455538, 1],
        [0.81894559, 1],
        [0.79067556, 1]],
        columns = ['ypred_proba_test','ypred_bin_test']
    )
    true_acc = 'Accuracy on test: 0.667 \n'
    true_fnr = 'False Negative Rate on test: 0.000 \n'
    true_cm = '                 Predicted negative  Predicted '+\
    'positive\nActual negative                   0'+\
    '                   1\nActual positive'+\
    '                   0                   2'
    test_result = evaluate(score_df, test, target)
    test_acc = test_result[0]
    test_fnr = test_result[1]
    test_cm = test_result[2]

    assert true_acc == test_acc
    assert true_fnr == test_fnr
    assert true_cm == test_cm


def test_evaluate_wrong_score():
    """test invalid data type"""
    scored_df = 'Wrong data type'
    with pytest.raises(TypeError):
        evaluate(scored_df, test, target)
