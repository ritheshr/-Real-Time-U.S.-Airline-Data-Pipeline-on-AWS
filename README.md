#  Real-Time U.S. Airline Data Pipeline on AWS

This project implements a fully automated, production-grade ETL pipeline for ingesting, transforming, and visualizing U.S. airline data using AWS services including S3, Glue, Lambda, Athena, and QuickSight.

---

##  Project Structure

```
├── glue/
│   └── etl_airlines_job.py         # Glue PySpark script
├── lambda/
│   └── trigger_etl_job.py          # Lambda function to trigger Glue job
├── queries/
│   └── athena_visual_queries.sql   # Ready-to-use Athena queries
├── docs/
│   └── A_detailed_architectural_diagram_in_the_image_illu.png
└── README.md
```

---

## Architecture Overview

1. **Data Ingestion**: CSVs uploaded to S3 (`raw-data-airlines`)
2. **Crawling**: Glue Crawler populates the Data Catalog
3. **Processing**: ETL job transforms & fills missing data → writes Parquet to `processed-data-airlines`
4. **Triggering**: Lambda auto-triggers on S3 upload using S3 → Lambda → Glue
5. **Querying**: Athena queries over transformed data
6. **Visualization**: QuickSight dashboards powered by Athena datasets

---

## IAM & Role Configuration

### IAM Policy for Glue Crawler & ETL

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::raw-data-airlines",
        "arn:aws:s3:::raw-data-airlines/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["glue:*"] ,
      "Resource": "*"
    }
  ]
}
```

Attach this inline policy to:

* Glue Service Role
* Lambda Execution Role

---

## Lambda Trigger Setup

### Lambda Function Code: `trigger-etl-airports2-job.py`

```python
import boto3

glue = boto3.client('glue')

def lambda_handler(event, context):
    response = glue.start_job_run(JobName='etl_airports2_job')
    return {
        'statusCode': 200,
        'body': str(response)
    }
```

###  S3 Bucket Trigger Permissions

```json
{
  "Effect": "Allow",
  "Principal": { "Service": "s3.amazonaws.com" },
  "Action": "lambda:InvokeFunction",
  "Resource": "arn:aws:lambda:us-east-1:ACCOUNT_ID:function:trigger-etl-airports2-job",
  "Condition": {
    "ArnLike": {
      "AWS:SourceArn": "arn:aws:s3:::raw-data-airlines"
    }
  }
}
```

---

## Glue ETL Job: `etl_airports2_job.py`

```python
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from awsglue.dynamicframe import DynamicFrame

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

df = glueContext.create_dynamic_frame.from_catalog(
    database="airlines-database", table_name="raw-raw_data_airlines"
).toDF()

# Fill nulls
df = df.fillna({'passengers': 150, 'seats': 180})

# Write
cleaned_df = DynamicFrame.fromDF(df, glueContext, "cleaned_df")
glueContext.write_dynamic_frame.from_options(
    frame=cleaned_df,
    connection_type="s3",
    connection_options={"path": "s3://processed-data-airlines/airports2_parquet/"},
    format="parquet"
)
```

---

## Athena Queries for Visualization

```SAMPLE Sql QUERIES
-- Longest Routes
SELECT origin_airport, destination_airport, ROUND(MAX(distance), 2) AS max_distance
FROM "airlines-database"."raw-raw_data_airlines"
GROUP BY origin_airport, destination_airport
ORDER BY max_distance DESC
LIMIT 10;

-- City-to-City Frequency
SELECT origin_city, destination_city, COUNT(*) AS connection_count
FROM "airlines-database"."raw-raw_data_airlines"
GROUP BY origin_city, destination_city
ORDER BY connection_count DESC
LIMIT 10;
```

---

## QuickSight Dashboard Structure

### Visuals

1. **Top 10 Longest Routes** – Horizontal bar, grouped by route
2. **Most Frequent City Pairs** – Vertical bar, sorted by count
3. **Origin Airport Map** – Point map
4. **Destination Airport Map** – Bubble map by population
5. **Flights per Route** – Heatmap

### Filters

* Origin city
* Destination city
* Flight range

---

##  Deployment Checklist

Create S3 buckets: `raw-data-airlines`, `processed-data-airlines`
Create Glue Crawler + ETL Job
Assign IAM roles and inline policies
Create Lambda trigger from S3 PUT events
Validate with Athena queries
Build and publish QuickSight dashboard

---

##  Author

**Rithesh Raja** – Cloud Data Engineer
🔗LinkedIn: https://www.linkedin.com/in/rithesh-raja-14a65a167/| 📧 ritheshraj321@gmail.com

---

> Fully serverless, highly visualized, and production-ready airline analytics pipeline built with AWS Glue, Lambda, Athena & QuickSight.
