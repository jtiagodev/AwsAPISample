import s3fs
import boto3
import io
from botocore.vendored import requests
import pandas as pd
from pandas.io.json import json_normalize
from datetime import datetime
pd.options.mode.chained_assignment = None

s3 = boto3.resource('s3')
#s3_forces_file = s3.Object('computacao-nuvem-spark', 'get-data/force_ids.csv').get()['Body']

def last_month():
    date = datetime.now()
    m, y = (date.now().month+-2) % 12, date.year + ((date.now().month)+-2-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.now().replace(day=d,month=m, year=y).strftime("%Y-%m")

def get_current_month_data(force_id, month=None):
    
    if not month: month = last_month()
    
    try:
        data = json_normalize(requests.get("https://data.police.uk/api/stops-force?force="+force_id+"&date="+month).json())
        
        if len(data) == 0:
            return []
        
        data["force_id"] = force_id
        data["month"] = month
        data["outcome_class"] = data.outcome.apply(lambda x: "Outcome" if x != "" else "No outcome")
        data["officer_defined_ethnicity"] = data.officer_defined_ethnicity.apply(lambda x: "Uknown" if x == None else x)
        data["age_range"] = data.age_range.apply(lambda x: "Uknown" if x == None else x)
        return data[["force_id", "month","type", "officer_defined_ethnicity", "age_range", "outcome_class"]]

    except:
        return []


#Handler
def lambda_handler(event, context):
    
    month_data = []
    forces = pd.read_csv("s3://computacao-nuvem-spark/get-data/force_ids.csv")
    print(forces)
        
    for force_id in forces.id:
    
        if len(month_data) == 0:
            month_data = get_current_month_data(force_id)

        else:
            force_data = get_current_month_data(force_id)

            if len(force_data) == 0:
                continue

            month_data = pd.concat([month_data,force_data]) 

    if len(month_data) > 0:
        #csv_buffer = StringIO()
        month_data.to_csv("s3://computacao-nuvem-spark/spark-input/input-data/"+last_month()+".csv", index=False)

    return {
        'statusCode': 200,
        'body': 'Data updated.'
    }