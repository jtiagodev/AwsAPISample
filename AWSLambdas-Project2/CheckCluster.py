import json
import boto3


def lambda_handler(event, context):

    # cluster_name = event['pathParameters']['clusterName']
    cluster_id = event['queryStringParameters']['clusterid']
    client = boto3.client('emr')

    # clusters = client.list_clusters()
    # your_cluster = [i for i in clusters['Clusters'] if i['Name'] == cluster_name][0]
    # response = client.describe_cluster(ClusterId=your_cluster['Id'])
    response = client.describe_cluster(ClusterId=cluster_id)

    res_payload = {}
    res_payload['status'] = {}
    res_payload['status']['state'] = response['Cluster']['Status']['State']
    # res_payload['status']['changecode'] = response['Cluster']['Status']['StateChangeReason']['Code']
    # res_payload['status']['changemessage'] = response['Cluster']['Status']['StateChangeReason']['Message']

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps(res_payload)
    }
