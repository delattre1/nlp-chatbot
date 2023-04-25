import os
from dotenv import load_dotenv, find_dotenv
from classes.s3_handler import S3Handler


def create_s3_connection():
    load_dotenv(find_dotenv())
    S3_ACCESS_KEY = os.environ['S3_ACCESS_KEY']
    S3_SECRET_KEY = os.environ['S3_SECRET_KEY']
    S3_ENDPOINT   = os.environ['S3_ENDPOINT']
    S3_SECURE     = os.environ['S3_SECURE']
    S3_BUCKET     = os.environ['S3_BUCKET']

    if not S3_ACCESS_KEY:
        raise ValueError('S3_ACCESS_KEY is not defined')

    if not S3_SECRET_KEY:
        raise ValueError('S3_SECRET_KEY is not defined')

    if not S3_ENDPOINT:
        raise ValueError('S3_ENDPOINT is not defined')
    if not S3_BUCKET:
        raise ValueError('S3_BUCKET is not defined')

    if not S3_SECURE:
        raise ValueError('S3_SECURE is not defined')
    S3_SECURE = True if (S3_SECURE == 'true') else False

    s3 = S3Handler(access_key=S3_ACCESS_KEY, secret_key=S3_SECRET_KEY, endpoint=S3_ENDPOINT, bucket=S3_BUCKET, secure=S3_SECURE)
    return s3
