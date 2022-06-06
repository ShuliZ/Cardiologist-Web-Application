.PHONY: image image_app image_test

image:
	docker build -f dockerfiles/Dockerfile -t final-project .

image_app:
	docker build -f dockerfiles/Dockerfile.app -t final-project-app .

image_test:
	docker build -f dockerfiles/Dockerfile.test -t final-project-tests .

# Database
.PHONY: create_db

create_db:
	docker run -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="$(shell pwd)"/,target=/app/ final-project run.py create_db

# Pipeline
.PHONY: upload_file_to_s3 download_file_from_s3 acquire featurize train score evaluate feature_importance

upload_file_to_s3:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY final-project run.py upload_file_to_s3

download_file_from_s3:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY final-project run.py download_file_from_s3

data/artifacts/cleaned.csv: download_file_from_s3
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py run_model_pipeline --step acquire --config config/config.yaml --output data/artifacts/cleaned.csv

acquire: data/artifacts/cleaned.csv

data/artifacts/featurized.csv: data/artifacts/cleaned.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py run_model_pipeline --step featurize --input data/artifacts/cleaned.csv --config config/config.yaml --output data/artifacts/featurized.csv

featurize: data/artifacts/featurized.csv

models/rf.sav data/artifacts/x_test.csv data/artifacts/y_test.csv: data/artifacts/featurized.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py run_model_pipeline --step train --input data/artifacts/featurized.csv --config config/config.yaml --output models/rf.sav data/artifacts/x_test.csv data/artifacts/y_test.csv

train: models/rf.sav data/artifacts/x_test.csv data/artifacts/y_test.csv
	
data/artifacts/scored.csv: models/rf.sav data/artifacts/x_test.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py run_model_pipeline --step score --input models/rf.sav data/artifacts/x_test.csv --config config/config.yaml --output data/artifacts/scored.csv

score: data/artifacts/scored.csv
	
data/artifacts/evaluation_result.csv: data/artifacts/scored.csv data/artifacts/y_test.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py run_model_pipeline --step evaluate --input data/artifacts/scored.csv data/artifacts/y_test.csv --config config/config.yaml --output data/artifacts/evaluation_result.csv

evaluate: data/artifacts/evaluation_result.csv

feature_importance: models/rf.sav
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py plot_feature_importance --input models/rf.sav --config config/config.yaml

pipeline: acquire featurize train score evaluate

# App
.PHONY: run_app

run_app:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ \
      -e SQLALCHEMY_DATABASE_URI \
      -p 5001:5001 final-project-app

# Test
test:
	docker run final-project-tests