import pytest

import pandas as pd
import yaml

from src.feature import get_binary_data, get_ohe_data, get_ordinalenc_age, get_ordinalenc_health, featurize

# Load configuration file for parameters and tmo path
with open('config/config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# data frame initialization
df_values = \
    [['No', 26.58, 'Yes', 'No', 'No', 20.0, 30.0, 'No', 'Male',
        '65-69', 'White', 'Yes', 'Yes', 'Fair', 8.0, 'Yes', 'No', 'No'],
       ['Yes', 28.87, 'Yes', 'No', 'No', 6.0, 0.0, 'Yes', 'Female',
        '75-79', 'Black', 'No', 'No', 'Fair', 12.0, 'No', 'No', 'No'],
       ['Yes', 34.3, 'Yes', 'No', 'No', 30.0, 0.0, 'Yes', 'Male',
        '60-64', 'White', 'Yes', 'No', 'Poor', 15.0, 'Yes', 'No', 'No']]

df_index = [2, 5, 10]

df_columns = \
    ['HeartDisease', 'BMI', 'Smoking', 'AlcoholDrinking', 'Stroke',
       'PhysicalHealth', 'MentalHealth', 'DiffWalking', 'Sex', 'AgeCategory',
       'Race', 'Diabetic', 'PhysicalActivity', 'GenHealth', 'SleepTime',
       'Asthma', 'KidneyDisease', 'SkinCancer']
# parameters initialization
binary_col = \
    ['Smoking','AlcoholDrinking',
    'Stroke','Asthma','DiffWalking','PhysicalActivity',
    'KidneyDisease','SkinCancer']

TARGET_COL = 'HeartDisease'

binary_value = ['No', 'Yes']

onehot_col = ['Race', 'Diabetic','Sex']

required_col = \
    ['Race_Asian',
    'Race_Black',
    'Race_Hispanic',
    'Race_Other',
    'Race_White',
    'Diabetic_No, borderline diabetes',
    'Diabetic_Yes',
    'Diabetic_Yes (during pregnancy)',
    'Sex_Male']

AGE_COL = 'AgeCategory'

age_mapping = {
    '18-24': 0,
    '25-29': 1,
    '30-34': 2,
    '35-39': 3,
    '40-44': 4,
    '45-49': 5,
    '50-54': 6,
    '55-59': 7,
    '60-64': 8,
    '65-69': 9,
    '70-74': 10,
    '75-79': 11,
    '80 or older': 12
}

HEALTH_COL = 'GenHealth'

health_mapping = {
    'Poor': 0,
    'Fair': 1,
    'Good': 2,
    'Very good': 3,
    'Excellent': 4
 }

num_columns = ['BMI', 'PhysicalHealth', 'MentalHealth', 'SleepTime']


def test_get_binary_data_happy():
    """test whether the get_binary_data function work as expected"""
    df_true = pd.DataFrame(
        [[0, 26.58, 1, 0, 0, 20.0, 30.0, 0, 'Male', '65-69', 'White',
        'Yes', 1, 'Fair', 8.0, 1, 0, 0],
       [1, 28.87, 1, 0, 0, 6.0, 0.0, 1, 'Female', '75-79', 'Black', 'No',
        0, 'Fair', 12.0, 0, 0, 0],
       [1, 34.3, 1, 0, 0, 30.0, 0.0, 1, 'Male', '60-64', 'White', 'Yes',
        0, 'Poor', 15.0, 1, 0, 0]],
        index = [2, 5, 10],
        columns = ['HeartDisease', 'BMI', 'Smoking', 'AlcoholDrinking', 'Stroke',
       'PhysicalHealth', 'MentalHealth', 'DiffWalking', 'Sex', 'AgeCategory',
       'Race', 'Diabetic', 'PhysicalActivity', 'GenHealth', 'SleepTime',
       'Asthma', 'KidneyDisease', 'SkinCancer']
    )
    # input dataframe
    df_in = pd.DataFrame(df_values, index = df_index, columns=df_columns)
    df_test = get_binary_data(df_in, False, binary_col, TARGET_COL, binary_value)
    # Test if the true and output dataframes are the same
    pd.testing.assert_frame_equal(df_true, df_test)

def test_get_binary_data_non_df():
    """test invalid input dataframe data type"""
    df_non = 'I am not a dataframe'
    # errors for wrong data frame type
    with pytest.raises(TypeError):
        get_binary_data(df_non, False, binary_col, TARGET_COL, binary_value)

def test_get_ohe_data_happy():
    """test whether the get_ohe_data function work as expected"""
    df_true = pd.DataFrame(
        [['No', 26.58, 'Yes', 'No', 'No', 20.0, 30.0, 'No', '65-69', 'Yes',
        'Fair', 8.0, 'Yes', 'No', 'No', 0.0, 0.0, 0.0, 0.0, 1.0, 0.0,
        1.0, 0.0, 1.0],
       ['Yes', 28.87, 'Yes', 'No', 'No', 6.0, 0.0, 'Yes', '75-79', 'No',
        'Fair', 12.0, 'No', 'No', 'No', 0.0, 0.0, 0.0, 0.0, 1.0, 0.0,
        1.0, 0.0, 1.0],
       ['Yes', 34.3, 'Yes', 'No', 'No', 30.0, 0.0, 'Yes', '60-64', 'No',
        'Poor', 15.0, 'Yes', 'No', 'No', 0.0, 0.0, 0.0, 0.0, 1.0, 0.0,
        1.0, 0.0, 1.0]],
        index = [2, 5, 10],
        columns = ['HeartDisease', 'BMI', 'Smoking', 'AlcoholDrinking', 'Stroke',
       'PhysicalHealth', 'MentalHealth', 'DiffWalking', 'AgeCategory',
       'PhysicalActivity', 'GenHealth', 'SleepTime', 'Asthma', 'KidneyDisease',
       'SkinCancer', 'Race_Asian', 'Race_Black', 'Race_Hispanic', 'Race_Other',
       'Race_White', 'Diabetic_No, borderline diabetes', 'Diabetic_Yes',
       'Diabetic_Yes (during pregnancy)', 'Sex_Male']
    )
    # input dataframe
    df_in = pd.DataFrame(df_values, index = df_index, columns=df_columns)
    df_test = get_ohe_data(df_in, onehot_col, required_col)

    # Test if the true and output dataframes are the same
    pd.testing.assert_frame_equal(df_true, df_test)


def test_get_ohe_data_non_df():
    """test invalid input dataframe data type"""
    df_non = 'I am not a dataframe'
    # errors for wrong data frame type
    with pytest.raises(TypeError):
        get_ohe_data(df_non, onehot_col, required_col)


def test_get_ordinalenc_age_happy():
    """test whether the function get_ordinalenc_age works as expected"""
    df_true = pd.DataFrame(
        [['No', 26.58, 'Yes', 'No', 'No', 20.0, 30.0, 'No', 'Male', 9,
         'White', 'Yes', 'Yes', 'Fair', 8.0, 'Yes', 'No', 'No'],
        ['Yes', 28.87, 'Yes', 'No', 'No', 6.0, 0.0, 'Yes', 'Female', 11,
         'Black', 'No', 'No', 'Fair', 12.0, 'No', 'No', 'No'],
        ['Yes', 34.3, 'Yes', 'No', 'No', 30.0, 0.0, 'Yes', 'Male', 8,
         'White', 'Yes', 'No', 'Poor', 15.0, 'Yes', 'No', 'No']],
         index = [2, 5, 10],
         columns = ['HeartDisease', 'BMI', 'Smoking', 'AlcoholDrinking', 'Stroke',
        'PhysicalHealth', 'MentalHealth', 'DiffWalking', 'Sex', 'AgeCategory',
        'Race', 'Diabetic', 'PhysicalActivity', 'GenHealth', 'SleepTime',
        'Asthma', 'KidneyDisease', 'SkinCancer']
    )
    # input dataframe
    df_in = pd.DataFrame(df_values, index = df_index, columns=df_columns)
    df_test = get_ordinalenc_age(df_in, AGE_COL, age_mapping)
    # Test if the true and output dataframes are the same
    pd.testing.assert_frame_equal(df_true, df_test)

def test_get_ordinalenc_age_non_df():
    """test invalid input dataframe data type"""
    df_non = 'I am not a dataframe'
    # errors for wrong data frame type
    with pytest.raises(ValueError):
        get_ordinalenc_age(df_non, AGE_COL, age_mapping)

def test_get_ordinalenc_health_happy():
    """test whether the function get_ordinalenc_health works as expected"""
    df_true = pd.DataFrame(
        [['No', 26.58, 'Yes', 'No', 'No', 20.0, 30.0, 'No', 'Male',
         '65-69', 'White', 'Yes', 'Yes', 1, 8.0, 'Yes', 'No', 'No'],
        ['Yes', 28.87, 'Yes', 'No', 'No', 6.0, 0.0, 'Yes', 'Female',
         '75-79', 'Black', 'No', 'No', 1, 12.0, 'No', 'No', 'No'],
        ['Yes', 34.3, 'Yes', 'No', 'No', 30.0, 0.0, 'Yes', 'Male',
         '60-64', 'White', 'Yes', 'No', 0, 15.0, 'Yes', 'No', 'No']],
         index = [2, 5, 10],
         columns = ['HeartDisease', 'BMI', 'Smoking', 'AlcoholDrinking', 'Stroke',
        'PhysicalHealth', 'MentalHealth', 'DiffWalking', 'Sex', 'AgeCategory',
        'Race', 'Diabetic', 'PhysicalActivity', 'GenHealth', 'SleepTime',
        'Asthma', 'KidneyDisease', 'SkinCancer']
    )
    # input dataframe
    df_in = pd.DataFrame(df_values, index = df_index, columns=df_columns)
    df_test = get_ordinalenc_health(df_in, HEALTH_COL, health_mapping)
    # Test if the true and output dataframes are the same
    pd.testing.assert_frame_equal(df_true, df_test)

def test_get_ordinalenc_health_non_df():
    """test invalid input dataframe data type"""
    df_non = 'I am not a dataframe'
    # errors for wrong data frame type
    with pytest.raises(ValueError):
        get_ordinalenc_health(df_non, HEALTH_COL, health_mapping)

def test_featurize_happy():
    """test whether the function featurize works as expected"""
    df_true = pd.DataFrame(
        [[0,26.58,1,0,0,20.0,30.0,0,9,1,1,8.0,1,0,0,0.0,0.0,0.0,0.0,1.0,0.0,1.0,0.0,1.0],
        [1,28.87,1,0,0,6.0,0.0,1,11,0,1,12.0,0,0,0,0.0,0.0,0.0,0.0,1.0,0.0,1.0,0.0,1.0],
        [1,34.30,1,0,0,30.0,0.0,1,8,0,0,15.0,1,0,0,0.0,0.0,0.0,0.0,1.0,0.0,1.0,0.0,1.0]],
         index = [2, 5, 10],
         columns = ['HeartDisease', 'BMI', 'Smoking', 'AlcoholDrinking', 'Stroke',
        'PhysicalHealth', 'MentalHealth', 'DiffWalking', 'AgeCategory',
        'PhysicalActivity', 'GenHealth', 'SleepTime', 'Asthma', 'KidneyDisease',
        'SkinCancer', 'Race_Asian', 'Race_Black', 'Race_Hispanic', 'Race_Other',
        'Race_White', 'Diabetic_No, borderline diabetes', 'Diabetic_Yes',
        'Diabetic_Yes (during pregnancy)', 'Sex_Male']
    )
    # input dataframe
    df_in = pd.DataFrame(df_values, index = df_index, columns=df_columns)
    df_test = featurize(df_in, False, config['feature'], num_columns)
    print(df_test)
    # Test if the true and output dataframes are the same
    pd.testing.assert_frame_equal(df_true, df_test)

def test_featurize_non_df():
    """test invalid input dataframe data type"""
    df_non = 'I am not a dataframe'
    # errors for wrong data frame type
    with pytest.raises(TypeError):
        featurize(df_non, False, config, num_columns)
