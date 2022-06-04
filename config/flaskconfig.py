import os
DEBUG = True
LOGGING_CONFIG = "config/logging/local.conf"
PORT = 5001
APP_NAME = "heart-disease"
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100


SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
if SQLALCHEMY_DATABASE_URI is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/patient.db'

# Connection string
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
DB_HOST = os.environ.get('MYSQL_HOST')
DB_PORT = os.environ.get('MYSQL_PORT')
DB_USER = os.environ.get('MYSQL_USER')
DB_PW = os.environ.get('MYSQL_PASSWORD')
DATABASE = os.environ.get('DATABASE_NAME')
DB_DIALECT = 'mysql+pymysql'

if SQLALCHEMY_DATABASE_URI is not None:
    pass
elif DB_HOST is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/patient.db'
else:
    SQLALCHEMY_DATABASE_URI = '{dialect}://{user}:{pw}@{host}:{port}/{db}'.format(dialect=DB_DIALECT, user=DB_USER,
                                                                                  pw=DB_PW, host=DB_HOST, port=DB_PORT,
                                                                                  db=DATABASE)
GENDER_CATEGORY = ['Male', 'Female']
AGE_CATEGORY = ['18-24', '25-29', '30-34', '35-39', '40-44', '45-49', 
                '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80 or older']
RACE = ['American Indian/Alaskan Native','Asian', 'Black', 'Hispanic', 'White', 
        'Other']
DIABETIC = ['Yes', 'Yes (during pregnancy)', 'No', 'No, borderline diabetes']
GEN_HEALTH = ['Excellent', 'Very good', 'Good', 'Fair', 'Poor']
BINARY = ['Yes', 'No']