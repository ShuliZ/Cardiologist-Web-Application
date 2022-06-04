.PHONY: image

image:
	docker build -f dockerfiles/Dockerfile -t final-project .

.PHONY: upload_file_to_s3 download_file_from_s3

upload_file_to_s3:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY final-project run.py upload_file_to_s3

download_file_from_s3:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY final-project run.py download_file_from_s3

.PHONY: create_db_local create_db_rds connect_db

create_db_local:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py create_db

create_db_rds:
	docker run -it -e MYSQL_HOST -e MYSQL_PORT -e MYSQL_USER -e MYSQL_PASSWORD -e DATABASE_NAME final-project run.py create_db

connect_db:
	docker run --platform linux/x86_64 -it --rm mysql:5.7.33 mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD}

feature_engineer:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py run_model_pipeline --step feature --input=data/sample/heart_2020_cleaned.csv --config=config/config.yaml --output=data/model/featurized.csv

model:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py run_model_pipeline --step model --input=data/model/featurized.csv --config=config/config.yaml --output=models/rf.joblib

image_app:
	docker build -f dockerfiles/Dockerfile.app -t final-project-app .

run_app:
	docker run -e SQLALCHEMY_DATABASE_URI -p 127.0.0.1:5001:5001 heart_disease_app
