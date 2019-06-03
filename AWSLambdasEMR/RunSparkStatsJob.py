import json
import boto3    

client = boto3.client('emr')
    
S3_BUCKET = 'computacao-nuvem-spark'
S3_FILE = 'sparky.py'
S3_KEY = 'spark-input/{file}'.format(file=S3_FILE)
S3_URI = 's3://{bucket}/{key}'.format(bucket=S3_BUCKET, key=S3_KEY)

def lambda_handler(event, context):
    
    response = client.run_job_flow(
        Name="count-forces-job",
        LogUri='s3://aws-logs-781762939116-eu-west-1/elasticmapreduce/',
        ReleaseLabel='emr-5.23.0',
        Instances={
            'MasterInstanceType': 'm3.xlarge',
            'SlaveInstanceType': 'm3.xlarge',
            'InstanceCount': 1,
            'KeepJobFlowAliveWhenNoSteps': False,
            'TerminationProtected': False,
        },
        Applications=[
            {
                'Name': 'Spark'
            }
        ],
        BootstrapActions=[
            {
                'Name': 'Maximize Spark Default Config',
                'ScriptBootstrapAction': {
                    'Path': 's3://support.elasticmapreduce/spark/maximize-spark-default-config'
                }
            },
        ],
        Steps=[
        {
            'Name': 'run-spark-app',
            'ActionOnFailure': 'TERMINATE_CLUSTER',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': ['spark-submit', '--deploy-mode', 'cluster', S3_URI]
            }
        }
        ],
        VisibleToAllUsers=True,
        JobFlowRole='EMR_EC2_DefaultRole',
        ServiceRole='EMR_DefaultRole'
    )

    # TODO implement
    return {
        'statusCode': 200,
        'body': response['JobFlowId']
    }
