.PHONY: image

image:
	docker build -f Dockerfile -t heart_disease .

.PHONY: upload_file_to_s3 download_file_from_s3

upload_file_to_s3:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY heart_disease run.py upload_file_to_s3

download_file_from_s3:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY heart_disease run.py download_file_from_s3

.PHONY: create_db_local create_db_rds connect_db

create_db_local:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ heart_disease run.py create_db

create_db_rds:
	docker run -it -e MYSQL_HOST -e MYSQL_PORT -e MYSQL_USER -e MYSQL_PASSWORD -e DATABASE_NAME heart_disease run.py create_db

connect_db:
	docker run --platform linux/x86_64 -it --rm mysql:5.7.33 mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD}