import logging
import traceback
import yaml
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy as SQA

from config.flaskconfig import AGE_CATEGORY, RACE, DIABETIC, GEN_HEALTH, BINARY, GENDER_CATEGORY
from src.add_patients import PatientManager
from src.predict import input_feature_engineer, input_predict

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
        return render_template('errororg.html')


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
            user_input_fe = input_feature_engineer(user_input, **conf["predict"]["input_feature_engineer"])
            logger.debug("user_input_fe: %s", user_input_fe.values)
            user_pred_prob = input_predict(user_input_fe, **conf["predict"]["input_predict"])[0]
            user_pred_text = input_predict(user_input_fe, **conf["predict"]["input_predict"])[1]
            logger.info("Probability %s", user_pred_prob)


            logger.debug("Result page accessed")
            return render_template('result.html', user_pred_prob=user_pred_prob, user_pred_text=user_pred_text)
        except:
            logger.warning("Not able to process your request, error page returned")
            raise
            return render_template('errororg.html')



if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])