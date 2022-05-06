"""Creates database of patient health status, 
and adds new data to the database"""
import logging.config
import sqlite3
import typing

import flask
import sqlalchemy
from sqlalchemy import Column, Integer, String, Float
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()

class Patient(Base):
    """Creates a data model for the database to be set up for patient health records.
    """

    __tablename__ = 'patient'

    id = Column(Integer, primary_key=True, autoincrement=True)
    BMI = Column(Float, unique=False, nullable=False)
    Smoking = Column(String(100), unique=False, nullable=False)
    AlcoholDrinking = Column(String(100), unique=False, nullable=False)
    Stroke = Column(String(100), unique=False, nullable=False)
    PhysicalHealth = Column(String(100), unique=False, nullable=False)
    MentalHealth = Column(Float, unique=False, nullable=False)
    DiffWalking = Column(String(100), unique=False, nullable=False)
    Sex = Column(String(100), unique=False, nullable=False)
    AgeCategory = Column(String(100), unique=False, nullable=False)
    Race = Column(String(100), unique=False, nullable=False)
    Diabetic = Column(String(100), unique=False, nullable=False)
    PhysicalActivity = Column(String(100), unique=False, nullable=False)
    GenHealth = Column(String(100), unique=False, nullable=False)
    SleepTime = Column(Float, unique=False, nullable=False)
    Asthma = Column(String(100), unique=False, nullable=False)
    KidneyDisease = Column(String(100), unique=False, nullable=False)
    SkinCancer = Column(String(100), unique=False, nullable=False)

    logger.info("Created data model patient.")
    # what is the return type??????????????????????????????????????????????????????
    def __repr__(self):
        return f'<Patient {self.title}>'

def create_db(engine_string: str) -> None:
    """Create database with Patient() data model from provided engine string.

    Args:
        engine_string (str): SQLAlchemy engine string specifying which database
            to write to

    Returns: None

    """
    try:
        engine = sqlalchemy.create_engine(engine_string)
        Base.metadata.create_all(engine)
    except sqlalchemy.exc.ArgumentError:
        logger.error("%s is an invalid engine string.")
    except sqlalchemy.exc.OperationalError:
        logger.error("Fail to connect to server.")
    else:
        logger.info("Database created.")

class PatientManager:
    """Creates a SQLAlchemy connection to the patient table.

    Args:
        app (:obj:`flask.app.Flask`): Flask app object for when connecting from
            within a Flask app. Optional.
        engine_string (str): SQLAlchemy engine string specifying which database
            to write to. Follows the format
    """
    def __init__(self, app: typing.Optional[flask.app.Flask] = None,
                 engine_string: typing.Optional[str] = None) -> None:
        if app:
            self.database = SQLAlchemy(app)
            self.session = self.database.session
        elif engine_string:
            engine = sqlalchemy.create_engine(engine_string)
            session_maker = sqlalchemy.orm.sessionmaker(bind=engine)
            self.session = session_maker()
        else:
            raise ValueError(
                "Need either an engine string or a Flask app to initialize")

    def close(self) -> None:
        """Closes SQLAlchemy session

        Returns: None

        """
        self.session.close()

    def add_patient(self, bmi: float, smoking: str, alcohol_drinking: str,
                    stroke: str, physical_health: float, mental_health: float, 
                    diff_walking: str, sex: str, age_category: str, race: str,
                    diabetic: str, physical_activity: str, gen_health: str,
                    sleep_time: float, asthma: str, kidney_disease: str,
                    skin_cancer: str) -> None:
        """Seeds an existing database with additional patient cases.

        Args:


        Returns:
            None
        """
        try:
            session = self.session
            patient = Patient(BMI = bmi,
                              Smoking = smoking,
                              AlcoholDrinking = alcohol_drinking,
                              Stroke = stroke,
                              PhysicalHealth = physical_health,
                              MentalHealth = mental_health,
                              DiffWalking = diff_walking,
                              Sex = sex,
                              AgeCategory = age_category,
                              Race = race,
                              Diabetic = diabetic,
                              PhysicalActivity = physical_activity,
                              GenHealth = gen_health,
                              SleepTime = sleep_time,
                              Asthma = asthma,
                              KidneyDisease = kidney_disease,
                              SkinCancer = skin_cancer)
            session.add(patient)
            session.commit()
            logger.info("A new patient case is added to database.")
        except sqlalchemy.exc.OperationalError:
            logger.error("Fail to connect to server. Please check \
                            if you are connected to Northwestern VPN.")

