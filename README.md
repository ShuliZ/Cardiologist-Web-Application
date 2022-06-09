# MSiA423 Template Repository

# Table of Contents
* [Project Charter](#Project-Charter)
* [Directory structure ](#Directory-structure)
* [Running the app ](#Running-the-app)
	* [0. Setup ](#0-Setup)
	* [1. Initialize the database ](#1-Initialize-the-database)
	* [2. Model Pipeline](#2-Model-Pipeline)
	* [3. Configure Flask app ](#3-Configure-Flask-app)
	* [4. Run the Flask app ](#4-Run-the-Flask-app)
* [Testing](#Testing)


## Project Charter

### Vision

According to [CDC](https://www.cdc.gov/heartdisease/facts.htm), heart disease is the leading cause of death for men, women, and people of most racial and ethnic groups in the United States. About 659,000 people in the United States die from heart disease each year—that’s 1 in every 4 deaths. This product is an online heart disease diagnosis system. It could systematically process patient symptoms, generate health reports, and help identify heart diseases. This product saves patients time and cost for general doctor consultation, and improves health outcomes and medical resources allocations.

### Mission

This product aims to make online heart disease diagnoses by predicting the presence of the heart disease based on patients’ answer to a series of questions about their heath status. It would also generate a summary report about their health conditions for the reference of the patients and doctors. The dataset used for this project was obtained from [Personal Key Indicators of Heart Disease](https://www.kaggle.com/datasets/kamilpytlak/personal-key-indicators-of-heart-disease).

### Success criteria

Model Performance Metrics
* This product is based on a machine learning classifier. The Machine Learning metric for the model evaluation is False Negative rate, because it is important to minimize the probability that a person with heart diseases is diagnosed incorrectly. A 10% False Negative rate denotes success.

Business Metrics
* Number of health reports generated per day: it measures the number of patients for online consultation.
* Abandon rate: it measures the number of users who do not complete the entire health check surveys.



## Directory structure 

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs│    
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── config.yaml					  <- Configuration for model pipeline
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── artifacts/					  <- Intermediate artifacts from model pipeline
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Raw data used for code development and testing
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project.
|
├── dockerfiles/                      <- Directory for all project-related Dockerfiles 
│   ├── Dockerfile.app                <- Dockerfile for building image to run web app
│   ├── Dockerfile.pylint		      <- Dockerfile for checking code style
│   ├── Dockerfile.run                <- Dockerfile for building image to execute run.py  
│   ├── Dockerfile.test               <- Dockerfile for building image to run unit tests
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project
│	├── add_patients.py				  <- Python script that defines the data model
│	├── feature.py			  		  <- Python script that generates new features
│	├── load.py						  <- Python script that loads raw data and saves cleaned data
│	├── model.py					  <- Python script that generates the trained model and train/test split data
│	├── predict.py					  <- Python script that makes prediction based on user inputs
│	├── s3.py						  <- Python script that upload or download raw data to or from s3 bucket
│	├── score.py					  <- Python script that scores the model
│
├── test/                             <- Files necessary for running model tests
│	├── test_feature.py				  <- Python script that tests function feature.py
│	├── test_model.py				  <- Python script that tests function model.py
│	├── test_predict.py				  <- Python script that tests function predict.py
│	├── test_score.py				  <- Python script that tests function score.py
│
├── app.py                            <- Flask wrapper for running the web app 
├── Makefile						  <- Makefile that contains shortcuts to terminal commands
├── requirements.txt                  <- Python package dependencies 
├── run.py                            <- Simplifies the execution of one or more of the src scripts
```

## Running the app 

### 0. Setup
#### Data Source

The dataset used in the project is from [Personal Key Indicators of Heart Disease](https://www.kaggle.com/datasets/kamilpytlak/personal-key-indicators-of-heart-disease). Since the size of the dataset is small, it is already downloaded and stored in the following path: data/sample/heart_2020_cleaned.csv.


#### Build Docker Image

In order to perform data acquisition, processing, or modeling, please run the following commands to build the docker image:

```bash
make image
```


#### AWS Credentials Configuration
To access AWS S3, AWS CLI will look for environment variables named AWS_ACCESS_KEY_ID  and AWS_SECRET_ACCESS_KEY to acquire your credentials. Please  configure your AWS credentials as follows:

```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY"
```


#### Upload data to S3
Please run the following command to upload the data from local to S3:

```bash
make upload_file_to_s3
```


#### Download data from S3
The dataset is already in the data/sample folder. If you want to acquire the dataset from S3, please run the following command:
```bash
make acquire
```


### 1. Initialize the database 

#### SQLAlchemy Database URL Configuration
SQLALCHEMY_DATABASE_URI is used for creating a database connection for both the relational data ingestion and web app components of the project. Please provide a SQLALCHEMY_DATABASE_URI  of either of the following formats: "{dialect}://{user}:{pasword}>@{host}:{port}/{database}" or "sqlite:///data/{databasename}.db"

#### Create the database
To create the database locally or on RDS, please run the following command:

```bash
docker run -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="$(pwd)"/,target=/app/ final-project run.py create_db
```

### 2. Model Pipeline

#### Running Entire Model Pipeline
To execute the entire model pipeline, please run

```bash
make pipeline
```

You can also execute each step of the model pipeline by following the instructions below.

#### Acquire and Process Data
To load the raw data from S3 bucket, clean and/or process it, and then save it to the appropriate directory, please run

```bash
make load
```

#### Feature Generation
To generate the features and save them to the appropriate directory, please run

```bash
docker run --mount type=bind,source="$(pwd)",target=/app/ final-project run.py run_model_pipeline --step featurize --input data/artifacts/cleaned.csv --config config/config.yaml --output data/artifacts/featurized.csv
```

#### Training
To generate the trained model object and train/test split data and save them to the appropriate directories, please run

```bash
docker run --mount type=bind,source="$(pwd)",target=/app/ final-project run.py run_model_pipeline --step train --input data/artifacts/featurized.csv --config config/config.yaml --output_model models/rf.sav --output_data data/artifacts/
```

#### Scoring
To produce predictions/labels and save them to the appropriate directory, please run

```bash
docker run --mount type=bind,source="$(pwd)",target=/app/ final-project run.py run_model_pipeline --step score --input models/rf.sav data/artifacts/test.csv --config config/config.yaml --output data/artifacts/scored.csv
```

#### Evaluation
To compute the performance metrics and save them to the appropriate directory, please run

```bash
docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py run_model_pipeline --step evaluate --input data/artifacts/scored.csv data/artifacts/test.csv --config config/config.yaml --output data/artifacts/evaluation_result.csv
```

### 3. Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
# Keep True for debugging, change to False when moving to production
DEBUG = True 
# Path to file that configures Python logger
LOGGING_CONFIG = "config/logging/local.conf"
# What port to expose app on. Must be the same as the port exposed in dockerfiles/Dockerfile.app
PORT = 5001
APP_NAME = "heart-disease"
SQLALCHEMY_TRACK_MODIFICATIONS = True
# the host that is running the app.
HOST = "0.0.0.0"
# If true, SQL for queries made will be printed
SQLALCHEMY_ECHO = False  
# Limits the number of rows returned from the database
MAX_ROWS_SHOW = 100
# URI for database that contains patient input records
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
if SQLALCHEMY_DATABASE_URI is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/patient.db'
# input values for form
GENDER_CATEGORY = ['Male', 'Female']
AGE_CATEGORY = ['18-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80 or older']
RACE = ['American Indian/Alaskan Native','Asian', 'Black', 'Hispanic', 'White', 'Other']
DIABETIC = ['Yes', 'Yes (during pregnancy)', 'No', 'No, borderline diabetes']
GEN_HEALTH = ['Excellent', 'Very good', 'Good', 'Fair', 'Poor']
BINARY = ['Yes', 'No']
```



### 4. Run the Flask app 

#### Build the image 

To build the image, run from this directory (the root of the repo): 

```bash
make image_app
```
or
```bash
docker build -f dockerfiles/Dockerfile.app -t final-project-app .
```

This command builds the Docker image, with the tag `final-project-app`, based on the instructions in `dockerfiles/Dockerfile.app` and the files existing in this directory.


#### Running the app

To run the Flask app, run: 

```bash
 docker run --mount type=bind,source="$(pwd)",target=/app/ -e SQLALCHEMY_DATABASE_URI -p 5001:5001 final-project-app
```

You should be able to access the app at http://127.0.0.1:5001/ in your browser.

The arguments in the above command do the following: 


* The `--mount` argument allows the app to access your local `data/` folder
* The `-e SQLALCHEMY_DATABASE_URI` specifies the database used to store user inputs
* The `-p 5001:5001` argument maps your computer's local port 5001 to the Docker container's port 5001 so that you can view the app in your browser.


## Testing
If you want to run the unit tests, please be sure that you have built the image by running ```make image```.

Then, run the following:

```bash
make image_test
```
or 
```bash
docker build -f dockerfiles/Dockerfile.test -t final-project-tests .
```

To run the tests, run: 

```bash
make tests
```
or
```bash
docker run final-project-tests
```
