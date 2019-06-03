import json
import boto3
from datetime import datetime

# Bucket name
S3_BUCKET = 'computacao-nuvem-spark'

# Get S3 client
s3 = boto3.resource('s3')

# Get all the objects in bucket
bucket = s3.Bucket('computacao-nuvem-spark')

# Handler


def lambda_handler(event, context):

    # Set folder path
    FOLDER_PATH = 'spark-output/'

    # Get bucket files
    bucket_objects = bucket.objects.all()

    # Get most recent output folder
    most_recent_output = sorted([object for object in bucket_objects if (FOLDER_PATH in object.key) and (
        '_SUCCESS' not in object.key)], key=lambda x: x.key, reverse=True)[0]

    # print(most_recent_folder_path)

    # output = [object for object in bucket_objects if ('_SUCCESS' not in object.key) and (most_recent_folder_path][0]

    print(most_recent_output)

    return {
        'statusCode': 200,
        'body': json.loads(json.dumps(most_recent_output.get()['Body'].read().decode().replace("u'", "'").replace("\n", ",")))
    }
