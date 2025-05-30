import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame

args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Load from Glue Catalog (table created by crawler)
datasource = glueContext.create_dynamic_frame.from_catalog(
    database="airlines-database",
    table_name="raw-raw_data_airlines"
)

# Convert to DataFrame for transformation
df = datasource.toDF()

# Clean 'NA' and cast to proper types
columns_to_cast = {
    'Passengers': 'int',
    'Seats': 'int',
    'Flights': 'int',
    'Distance': 'double',
    'origin_population': 'bigint',
    'destination_population': 'bigint',
    'org_airport_lat': 'double',
    'org_airport_long': 'double',
    'dest_airport_lat': 'double',
    'dest_airport_long': 'double'
}

for col_name, col_type in columns_to_cast.items():
    df = df.withColumn(col_name, df[col_name].cast(col_type))

# Convert back to DynamicFrame
cleaned_df = DynamicFrame.fromDF(df, glueContext, "cleaned_df")

# Write as Parquet
glueContext.write_dynamic_frame.from_options(
    frame=cleaned_df,
    connection_type="s3",
    connection_options={"path": "s3://processed-data-airlines/airports2_parquet/"},
    format="parquet"
)

job.commit()
