#!/usr/bin/env bash

python3 run.py run_model_pipeline --step acquire --config config/config.yaml --output data/artifacts/cleaned.csv

python3 run.py run_model_pipeline --step featurize --input data/artifacts/cleaned.csv --config config/config.yaml --output data/artifacts/featurized.csv

python3 run.py run_model_pipeline --step train --input data/artifacts/featurized.csv --config config/config.yaml --output models/rf.sav data/artifacts/x_test.csv data/artifacts/y_test.csv

python3 run.py run_model_pipeline --step score --input models/rf.sav data/artifacts/x_test.csv --config config/config.yaml --output data/artifacts/scored.csv

python3 app.py