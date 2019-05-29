import json
import boto3
import time
# import threading


def getFileFromS3():
        
    time.sleep(100)
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('computacao-nuvem-spark')
    # Iterates through all the objects, doing the pagination for you. Each obj
    # is an ObjectSummary, so it doesn't contain the body. You'll need to call
    # get to get the whole body.
    
    for obj in bucket.objects.all():
        key = obj.key
        # body = obj.get()['Body'].read()
        # JA: gets the correct file
        # if "Output" in key:
        return key      
        # return {
        #     'statusCode': 200,
        #     'body': "Found file with name %s"%(key)
        # }
    
        #checkEMRClusterStatus(cluster_id):
        # if cluster_id["Status"]["State"] == 'TERMINATED'
        
def lambda_handler(event, context):
    
    #Get EMR client
    conn = boto3.client("emr")
    
    #Get the entire list of clusters
    clusters = conn.list_clusters()
    # choose the correct cluster
    clusters = [c["Id"] for c in clusters["Clusters"] 
                if c["Status"]["State"] in ["RUNNING", "WAITING"]]
                
                
    # code location on your emr master node
    # CODE_PATH = "/emr/instance-controller/lib/bootstrap-actions/1/sample-spark.jar"
    CODE_PATH = "s3n://computacao-nuvem-spark/spark-input/sparky.py"
    
    # spark configuration example
    step_args = [
        "/usr/bin/spark-submit", CODE_PATH
    ]

    step = {
        'Name': 'ExecuteSparkSQLStatement',
        'ActionOnFailure': 'CANCEL_AND_WAIT',
        'HadoopJarStep': {
                'Jar': 's3n://elasticmapreduce/libs/script-runner/script-runner.jar',
                'Args': step_args
            }
        }
        
    if not clusters:
        # sys.stderr.write("No valid clusters\n")
        # sys.stderr.exit()
        
        
       
            
        # Defining a new Cluster with a JOB 
        cluster_id = conn.run_job_flow(
        Name='ComputacaoNuvem2019',
        ServiceRole='EMR_DefaultRole',
        JobFlowRole='EMR_EC2_DefaultRole',
        VisibleToAllUsers=True,
        LogUri='s3n://aws-logs-781762939116-eu-west-1/',
        ReleaseLabel='emr-5.8.0',
        Instances={
            'InstanceGroups': [
                {
                    'Name': 'Master nodes',
                    'Market': 'ON_DEMAND',
                    'InstanceRole': 'MASTER',
                    'InstanceType': 'm3.xlarge',
                    'InstanceCount': 1,
                }
                
                # ,
                # {
                #    'Name': 'Slave nodes',
                #    'Market': 'ON_DEMAND',
                #    'InstanceRole': 'CORE',
                #    'InstanceType': 'm3.xlarge',
                #    'InstanceCount': 0,
                # }
            ],
            'Ec2KeyName': 'cn_projeto2',
            'KeepJobFlowAliveWhenNoSteps': False,
            'TerminationProtected': False
        },
        Applications=[{
            'Name': 'Spark'
        }],
        Configurations=[{
            "Classification":"spark-env",
            "Properties":{},
            "Configurations":[{
                "Classification":"export",
                "Properties":{
                    "PYSPARK_PYTHON":"python35",
                    "PYSPARK_DRIVER_PYTHON":"python35"
                }
            }]
        }],
        BootstrapActions=[{
            'Name': 'Install',
            'ScriptBootstrapAction': {
                'Path': 's3://computacao-nuvem-spark/bootstrap/initialize.sh'
            }
        }],
        Steps=[step],
        )
        
        # threading.Timer(5.0, getFileFromS3()).start()

        key = getFileFromS3()
        return {
            'statusCode': 200,
            'body': "Returned %s"%(key)
        }
         
        # return {
        #         'statusCode': 200,
        #         'body': "Created Cluster and added step: %s"%(cluster_id)
        #        }
            
    else: 
        
        # take the first relevant cluster
        cluster_id = clusters[0]
        
        action = conn.add_job_flow_steps(JobFlowId=cluster_id, Steps=[step])
    
        key = getFileFromS3()
        return {
            'statusCode': 200,
            'body': "Returned %s"%(key)
         }
        # return {
        #    'statusCode': 200,
        #    'body': "Added step: %s"%(action)
        # }
