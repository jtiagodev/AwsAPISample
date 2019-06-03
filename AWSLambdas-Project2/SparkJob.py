from pyspark import SQLContext
from pyspark.sql import SparkSession
import json
from datetime import datetime

# '/Users/Francisco/Desktop/cn/data/*.csv'
INPUT_FOLDER_PATH = 's3://computacao-nuvem-spark/spark-input/input-data/*.csv'
OUTPUT_PATH = 's3://computacao-nuvem-spark/spark-output/' + \
    datetime.now().strftime("%Y-%m")


def toJSONFormat(row):
    rowJSON = {}
    forceContent = {}
    typeContent = {}
    forceContent['total_starts_and_stops'] = row['total_starts_and_stops']
    forceContent['total_outcomes'] = row['total_outcomes']
    typeContent['person_search'] = row['person_search_percentage']
    typeContent['vehicle_search'] = row['vehicle_search_percentage']
    typeContent['person_vehicle_search'] = row['person_vehicle_search_percentage']
    forceContent['type_percentages'] = typeContent
    rowJSON[row['force_id']] = forceContent
    return rowJSON


if __name__ == '__main__':

    spark = SparkSession \
        .builder \
        .appName("Python Spark SQL basic example") \
        .getOrCreate()

    # spark is an existing SparkSession

    #df = spark.read.format("com.databricks.spark.csv").option("header", "true").load(INPUT_FOLDER_PATH)

    df = spark.read.format("com.databricks.spark.csv").option(
        "header", "true").load(INPUT_FOLDER_PATH)
    # Register the DataFrame as a SQL temporary view
    df.createOrReplaceTempView("raw_data")

    # Total Start and Stops
    startAndStops = spark.sql(
        "SELECT force_id, COUNT(*) as total_starts_and_stops FROM raw_data GROUP BY 1")
    startAndStops.createOrReplaceTempView("startAndStops")

    # Total Outcomes
    totalOutcomes = spark.sql(
        "SELECT force_id, SUM(CASE WHEN outcome_class = 'Outcome' THEN 1 ELSE 0 END) as total_outcomes FROM raw_data GROUP BY 1")
    totalOutcomes.createOrReplaceTempView("totalOutcomes")

    # Types of Start and Stops
    types = spark.sql("""
    SELECT 
        force_id, 
        AVG(CASE WHEN type = 'Person search' THEN 1 ELSE 0 END)*100 as person_search_percentage,
        AVG(CASE WHEN type = 'Vehicle search' THEN 1 ELSE 0 END)*100 as vehicle_search_percentage,
        AVG(CASE WHEN type = 'Person and Vehicle search' THEN 1 ELSE 0 END)*100 as person_vehicle_search_percentage
    FROM raw_data
    GROUP BY 1
    """)
    types.createOrReplaceTempView("types")
    # types.show()

    outputData = spark.sql("""
    SELECT
        startAndStops.force_id,
        total_starts_and_stops,
        total_outcomes,
        person_search_percentage,
        vehicle_search_percentage,
        person_vehicle_search_percentage
    FROM startAndStops
    LEFT JOIN totalOutcomes ON totalOutcomes.force_id = startAndStops.force_id
    LEFT JOIN types ON types.force_id = startAndStops.force_id
    """)
    # outputData.show()
    finalOutput = outputData.rdd.coalesce(1).map(lambda x: toJSONFormat(x))

    finalOutput.saveAsTextFile(OUTPUT_PATH)
