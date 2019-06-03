import json
import boto3

#Bucket name
S3_BUCKET = 'computacao-nuvem-spark'

#Get S3 client
s3 = boto3.resource('s3')

#Get all the objects in bucket
bucket = s3.Bucket('computacao-nuvem-spark')
    
#Handler
def lambda_handler(event, context):
    
    #Get spark id from request
    #spark_result_id = event['body']['spark_result_id']
    
    #Set folder path
    FOLDER_PATH = 'spark-output/' + 'get-forces/'#spark_result_id
    
    #Get output for folder
    folder_objects = [object for object in bucket.objects.all() if FOLDER_PATH in object.key]
    output = [object for object in folder_objects if '_SUCCESS' not in object.key][0].get()['Body'].read()
    
    return {
        'statusCode': 200,
        'body': json.loads(output)
    }
