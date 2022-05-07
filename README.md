# MSiA423 Template Repository

# Table of Contents
* [Project Charter](#Project-Charter)
* [Directory structure ](#Directory-structure)
* [Running the app ](#Running-the-app)
	* [1. Initialize the database ](#1.-Initialize-the-database)
	* [2. Configure Flask app ](#2.-Configure-Flask-app)
	* [3. Run the Flask app ](#3.-Run-the-Flask-app)
* [Testing](#Testing)
* [Mypy](#Mypy)
* [Pylint](#Pylint)


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
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project.
|
├── dockerfiles/                      <- Directory for all project-related Dockerfiles 
│   ├── Dockerfile.app                <- Dockerfile for building image to run web app
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
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project. No executable Python files should live in this folder.  
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the web app 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
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
make download_file_from_s3
```


### 1. Initialize the database 
#### Create the database locally
To create the database locally, please run the following command:

```bash
make create_db_local
```

By default, `run.py create_db` creates a local SQLite database at `sqlite:///data/patient.db`. You could also input a specific engine string by running:

```bash
docker run --mount type=bind,source="$(shell pwd)",target=/app/ heart_disease run.py create_db --engine_string=<YOUR_ENGINE_STRING>
```


#### Create the database on RDS
To create the databse on RDS, please first set the environment variables for database connection details:

```bash
export MYSQL_HOST="YOUR_HOST_URL"
export MYSQL_USER="YOUR_USERNAME"
export MYSQL_PASSWORD="YOUR_PASSWORD"
export MYSQL_PORT="YOUR_PORT"
export DATABASE_NAME="YOUR_DATABASE"
```

* Set `MYSQL_HOST` to be the RDS instance endpoint from the console.
* Set `MYSQL_USER` to the "master username" that you used to create the database server.
* Set `MYSQL_PASSWORD` to the "master password" that you used to create the database server.

If you wish, you can store your database connection details in a local file that is ignored from git. You can name this .mysqlconfig to write the above commands into .mysqlconfig:

```bash
vi .mysqlconfig
```

Remember, in `vim`, you press `i` to activate insert mode, and then `esc` to return to normal mode. From normal mode, `:wq` (command: write quit) will save your changes and close `vim`.

Please run the following command to update the .mysqlconfig file: 

```bash
source .mysqlconfig
```

To Using your database with SQLAlchemy:

```bash
make create_db_rds
```


Start a MySQL client and connect to your database:

```bash
make connect_db
```


#### Adding songs 
To add songs to the database:

```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/app/data/ pennylanedb ingest --engine_string=sqlite:///data/tracks.db --artist=Emancipator --title="Minor Cause" --album="Dusk to Dawn"
```

#### Defining your engine string 
A SQLAlchemy database connection is defined by a string with the following format:

`dialect+driver://username:password@host:port/database`

The `+dialect` is optional and if not provided, a default is used. For a more detailed description of what `dialect` and `driver` are and how a connection is made, you can see the documentation [here](https://docs.sqlalchemy.org/en/13/core/engines.html). We will cover SQLAlchemy and connection strings in the SQLAlchemy lab session on 
##### Local SQLite database 

A local SQLite database can be created for development and local testing. It does not require a username or password and replaces the host and port with the path to the database file: 

```python
engine_string='sqlite:///data/tracks.db'

```

The three `///` denote that it is a relative path to where the code is being run (which is from the root of this directory).

You can also define the absolute path with four `////`, for example:

```python
engine_string = 'sqlite://///Users/cmawer/Repos/2022-msia423-template-repository/data/tracks.db'
```


### 2. Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
DEBUG = True  # Keep True for debugging, change to False when moving to production 
LOGGING_CONFIG = "config/logging/local.conf"  # Path to file that configures Python logger
HOST = "0.0.0.0" # the host that is running the app. 0.0.0.0 when running locally 
PORT = 5000  # What port to expose app on. Must be the same as the port exposed in dockerfiles/Dockerfile.app 
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/tracks.db'  # URI (engine string) for database that contains tracks
APP_NAME = "penny-lane"
SQLALCHEMY_TRACK_MODIFICATIONS = True 
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100 # Limits the number of rows returned from the database 
```

### 3. Run the Flask app 

#### Build the image 

To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f dockerfiles/Dockerfile.app -t pennylaneapp .
```

This command builds the Docker image, with the tag `pennylaneapp`, based on the instructions in `dockerfiles/Dockerfile.app` and the files existing in this directory.

#### Running the app

To run the Flask app, run: 

```bash
 docker run --name test-app --mount type=bind,source="$(pwd)"/data,target=/app/data/ -p 5000:5000 pennylaneapp
```
You should be able to access the app at http://127.0.0.1:5000/ in your browser (Mac/Linux should also be able to access the app at http://127.0.0.1:5000/ or localhost:5000/) .

The arguments in the above command do the following: 

* The `--name test-app` argument names the container "test". This name can be used to kill the container once finished with it.
* The `--mount` argument allows the app to access your local `data/` folder so it can read from the SQLlite database created in the prior section. 
* The `-p 5000:5000` argument maps your computer's local port 5000 to the Docker container's port 5000 so that you can view the app in your browser. If your port 5000 is already being used for someone, you can use `-p 5001:5000` (or another value in place of 5001) which maps the Docker container's port 5000 to your local port 5001.

Note: If `PORT` in `config/flaskconfig.py` is changed, this port should be changed accordingly (as should the `EXPOSE 5000` line in `dockerfiles/Dockerfile.app`)


#### Kill the container 

Once finished with the app, you will need to kill the container. If you named the container, you can execute the following: 

```bash
docker kill test-app 
```
where `test-app` is the name given in the `docker run` command.

If you did not name the container, you can look up its name by running the following:

```bash 
docker container ls
```

The name will be provided in the right most column. 

## Testing

Run the following:

```bash
 docker build -f dockerfiles/Dockerfile.test -t pennylanetest .
```

To run the tests, run: 

```bash
 docker run pennylanetest
```

The following command will be executed within the container to run the provided unit tests under `test/`:  

```bash
python -m pytest
``` 

## Mypy

Run the following:

```bash
 docker build -f dockerfiles/Dockerfile.mypy -t pennymypy .
```

To run mypy over all files in the repo, run: 

```bash
 docker run pennymypy .
```
To allow for quick iteration, mount your entire repo so changes in Python files are detected:


```bash
 docker run --mount type=bind,source="$(pwd)"/,target=/app/ pennymypy .
```

To run mypy for a single file, run: 

```bash
 docker run pennymypy run.py
```

## Pylint

Run the following:

```bash
 docker build -f dockerfiles/Dockerfile.pylint -t pennylint .
```

To run pylint for a file, run:

```bash
 docker run pennylint run.py 
```

(or any other file name, with its path relative to where you are executing the command from)

To allow for quick iteration, mount your entire repo so changes in Python files are detected:


```bash
 docker run --mount type=bind,source="$(pwd)"/,target=/app/ pennylint run.py
```
