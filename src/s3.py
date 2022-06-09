import logging
import re
import typing

import boto3
import botocore


logger = logging.getLogger(__name__)

def parse_s3(path: str) -> typing.Tuple[str, str]:
    """Parse the S3 path to return bucket name and the S3 path
    Args:
        path (`str`): input S3 path
    Returns:
        s3bucket (`str`): S3 bucket name
        path (`str`): S3 path
    """
    # match the input path to the desired patterns
    regex = r's3://([\w._-]+)/([\w./_-]+)'
    matched = re.match(regex, path)
    # get bucke and path names
    s3bucket = matched.group(1)
    s3path = matched.group(2)

    return s3bucket, s3path


def upload_file_to_s3(local_path: str, s3_path: str) -> None:
    """Upload the file from local path to s3
    Args:
        local_path (`str`): local path of the file
        s3_path (`str`): s3 path the files to be uploaded to
    Returns:
        None
    """
    # get bucke and path names
    s3bucket, s3path = parse_s3(s3_path)

    # find bucket to upload files
    resc = boto3.resource('s3')
    bucket = resc.Bucket(s3bucket)
    try:
        bucket.upload_file(local_path, s3path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID '
                     'and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info('Data uploaded from %s to %s', local_path, s3_path)


def download_file_from_s3(local_path: str, s3_path: str) -> None:
    """Download the file from s3 to the local path
    Args:
        local_path (`str`): local path the files to be doanloaded to
        s3_path (`str`): s3 path the files to be downloaded from
    Returns:
        None
    """
    # get bucke and path names
    s3bucket, s3path = parse_s3(s3_path)

    # find bucket to download files
    resc = boto3.resource('s3')
    bucket = resc.Bucket(s3bucket)
    try:
        bucket.download_file(s3path, local_path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID '
                     'and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info('Data downloaded from %s to %s', s3_path, local_path)
