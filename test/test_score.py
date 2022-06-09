import pickle
import pytest

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

TARGET = 'HeartDisease'

def test_score_happy():
    """ test whether the function score works as expected"""
    df_true = pd.DataFrame(
        [[0.73455538, 1],
        [0.81894559, 1],
        [0.79067556, 1]],
        columns = ['ypred_proba_test','ypred_bin_test']
    )
    # load model
    with open('models/rf.sav', 'rb') as model_file:
        loaded_rf = pickle.load(model_file)
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
    """ test whether evaluate function works as expected"""
    score_df = pd.DataFrame(
        [[0.73455538, 1],
        [0.81894559, 1],
        [0.79067556, 1]],
        columns = ['ypred_proba_test','ypred_bin_test']
    )
    # true metrics output
    true_acc = 'Accuracy on test: 0.667 \n'
    true_fnr = 'False Negative Rate on test: 0.000 \n'
    true_cm = '                 Predicted negative  Predicted '+\
    'positive\nActual negative                   0'+\
    '                   1\nActual positive'+\
    '                   0                   2'
    # test metrics output
    test_result = evaluate(score_df, test, TARGET)
    test_acc = test_result[0]
    test_fnr = test_result[1]
    test_cm = test_result[2]
    # check whether the true and test output are the same
    assert true_acc == test_acc
    assert true_fnr == test_fnr
    assert true_cm == test_cm


def test_evaluate_wrong_score():
    """test invalid data type"""
    scored_df = 'Wrong data type'
    # raise errors when the score has wrong input type
    with pytest.raises(TypeError):
        evaluate(scored_df, test, TARGET)
