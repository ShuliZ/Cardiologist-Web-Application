.PHONY: image image_app image_test

image:
	docker build -f dockerfiles/Dockerfile.run -t final-project .

image_app:
	docker build -f dockerfiles/Dockerfile.app -t final-project-app .

image_test:
	docker build -f dockerfiles/Dockerfile.test -t final-project-tests .

# Database
.PHONY: create_db

create_db:
	docker run -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="$(shell pwd)"/,target=/app/ final-project run.py create_db

# Pipeline
.PHONY: upload_file_to_s3 download_file_from_s3 load featurize train score evaluate feature_importance

upload_file_to_s3:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY final-project run.py upload_file_to_s3

acquire:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY final-project run.py run_model_pipeline --step acquire

data/artifacts/cleaned.csv: acquire
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py run_model_pipeline --step load --config config/config.yaml --output data/artifacts/cleaned.csv

load: data/artifacts/cleaned.csv

data/artifacts/featurized.csv: data/artifacts/cleaned.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py run_model_pipeline --step featurize --input data/artifacts/cleaned.csv --config config/config.yaml --output data/artifacts/featurized.csv

featurize: data/artifacts/featurized.csv

models/rf.sav data/artifacts/test.csv: data/artifacts/featurized.csv config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py run_model_pipeline --step train --input data/artifacts/featurized.csv --config config/config.yaml --output_model models/rf.sav --output_data data/artifacts/

train: models/rf.sav data/artifacts/test.csv

data/artifacts/scored.csv: models/rf.sav data/artifacts/test.csv config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py run_model_pipeline --step score --input models/rf.sav data/artifacts/test.csv --config config/config.yaml --output data/artifacts/scored.csv

score: data/artifacts/scored.csv

data/artifacts/evaluation_result.csv: data/artifacts/scored.csv data/artifacts/test.csv config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py run_model_pipeline --step evaluate --input data/artifacts/scored.csv data/artifacts/test.csv --config config/config.yaml --output data/artifacts/evaluation_result.csv

evaluate: data/artifacts/evaluation_result.csv

pipeline: acquire load featurize train score evaluate

# App
.PHONY: run_app
run_app:
	docker run \
	 --mount type=bind,source="$(shell pwd)",target=/app/ \
	 -e SQLALCHEMY_DATABASE_URI \
	 -p 5001:5001 final-project-app

# Test
.PHONY: test
tests:
	docker run final-project-tests
