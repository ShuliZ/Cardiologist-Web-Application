import logging
import traceback
import yaml
from flask import Flask, render_template, request

import pandas as pd

from config.flaskconfig import AGE_CATEGORY, RACE, DIABETIC, GEN_HEALTH, BINARY, GENDER_CATEGORY
from src.add_patients import PatientManager
from src.feature import featurize
from src.predict import input_predict

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.config.from_pyfile("config/flaskconfig.py")

logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug('Web app log')

# Initialize the database session
patient_manager = PatientManager(app)

# load yaml configuration file
try:
    with open('config/config.yaml', "r") as file:
        conf = yaml.load(file, Loader=yaml.FullLoader)
        logger.info("Configuration file loaded")
except FileNotFoundError:
    logger.error("Configuration file is not found")


@app.route('/')
def index():
    try:
        logger.debug("Index page accessed")
        return render_template('index.html',
                                smoking = BINARY,
                                alcohol_drinking = BINARY,
                                strok_category = BINARY,
                                diff_walking = BINARY,
                                gender_category = GENDER_CATEGORY,
                                age_category = AGE_CATEGORY,
                                race_category = RACE,
                                diabetes_category = DIABETIC,
                                physical_activity = BINARY,
                                gen_health = GEN_HEALTH,
                                asthma_category = BINARY,
                                kidney_disease = BINARY,
                                skin_cancer = BINARY)
    except:
        traceback.print_exc()
        logger.warning("Not able to display the heart disease form, error page returned")
        return render_template('error.html')


@app.route("/result", methods=["GET", "POST"])
def add_entry():
    if request.method == "GET":
        return "Visit the homepage to fill out your health status and get predictions"
    elif request.method == "POST":
        try:
            logger.debug("start add new patient to rds")
            patient_manager.add_patient(
                bmi=request.form["bmi"],
                smoking = request.form["smoke"],
                alcohol_drinking = request.form["drink"],
                strok_category = request.form["stroke"],
                physical_health = request.form["physical_health"],
                mental_health = request.form["mental_health"],
                diff_walking = request.form["walk"],
                gender_category = request.form["gender"],
                age_category = request.form["age"],
                race_category = request.form["race"],
                diabetes_category = request.form["diabetes"],
                physical_activity = request.form["activity"],
                gen_health = request.form["gen"],
                sleep_time = request.form["sleep_time"],
                asthma_category = request.form["asthma"],
                kidney_disease = request.form["kidney"],
                skin_cancer = request.form["skin"]
            )
            logger.info("New patient information is added")
        
            user_input = {
                "BMI": request.form["bmi"],
                "Smoking": request.form["smoke"],
                "AlcoholDrinking": request.form["drink"],
                "Stroke": request.form["stroke"],
                "PhysicalHealth": request.form["physical_health"],
                "MentalHealth": request.form["mental_health"],
                "DiffWalking": request.form["walk"],
                "Sex": request.form["gender"],
                "AgeCategory": request.form["age"],
                "Race": request.form["race"],
                "Diabetic": request.form["diabetes"],
                "PhysicalActivity": request.form["activity"],
                "GenHealth": request.form["gen"],
                "SleepTime": request.form["sleep_time"],
                "Asthma": request.form["asthma"],
                "KidneyDisease": request.form["kidney"],
                "SkinCancer": request.form["skin"]
            }
            logger.debug("start prediction")
            input_df = pd.DataFrame(user_input, index=[0])
            user_input_fe = featurize(input_df, True, conf["feature"], **conf["feature"]["featurize"])
            user_pred_prob = input_predict(user_input_fe, **conf["predict"]["input_predict"])[0]
            user_pred_text = input_predict(user_input_fe, **conf["predict"]["input_predict"])[1]
            logger.info("Probability %s", user_pred_prob)
            logger.debug("Accessed Result page")
            return render_template('result.html', user_pred_prob=user_pred_prob, user_pred_text=user_pred_text)
        except:
            logger.warning("Not able to process your request, error page returned")
            return render_template('error.html')

@app.route('/contact', methods=['GET'])
def contact():
    """View of an 'Contact Us' page that has the contact information
    Returns:
        rendered html template located at: app/templates/contact.html
    """
    logger.debug("Contact page accessed")
    return render_template('contact.html')



if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])