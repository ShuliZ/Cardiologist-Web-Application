import pytest
import pickle

import pandas as pd
import numpy as np

from src.predict import input_predict


df_in = pd.DataFrame(
        [[26.58,1,0,0,20.0,30.0,0,9,1,1,8.0,1,0,0,0.0,0.0,0.0,0.0,1.0,0.0,1.0,0.0,1.0]],
         index = [2],
         columns = ['BMI', 'Smoking', 'AlcoholDrinking', 'Stroke',
        'PhysicalHealth', 'MentalHealth', 'DiffWalking', 'AgeCategory',
        'PhysicalActivity', 'GenHealth', 'SleepTime', 'Asthma', 'KidneyDisease',
        'SkinCancer', 'Race_Asian', 'Race_Black', 'Race_Hispanic', 'Race_Other',
        'Race_White', 'Diabetic_No, borderline diabetes', 'Diabetic_Yes',
        'Diabetic_Yes (during pregnancy)', 'Sex_Male'])

transformed_col = ['BMI','Smoking','AlcoholDrinking','Stroke','PhysicalHealth',
                   'MentalHealth','DiffWalking','AgeCategory','PhysicalActivity',
                   'GenHealth','SleepTime','Asthma','KidneyDisease','SkinCancer',
                   'Race_Asian','Race_Black','Race_Hispanic','Race_Other','Race_White',
                   'Diabetic_No, borderline diabetes','Diabetic_Yes',
                   'Diabetic_Yes (during pregnancy)','Sex_Male']

def test_input_predict_happy():
    with open('models/rf.sav', 'rb') as f:
        loaded_rf = pickle.load(f)
    true_result = np.array([73, 'You are LIKELY to have heart disease'])

    
    
    test_result = np.array(input_predict(df_in, loaded_rf, transformed_col))

    assert np.array_equal(true_result, test_result)


def test_input_predict_non_model():
    """ Test invalid model type"""
    rf_model = 'I am not a model'
    with pytest.raises(AttributeError):
        input_predict(df_in, rf_model, transformed_col)
