import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import input_file_name, regexp_extract

args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args['JOB_NAME'], args)


# ==============================
# READ ALL YOUTUBE CSV FILES
# ==============================

input_path = "s3://de-youtube-raw-useast1-krishna-2026/youtube/raw_statistics/*/*.csv"

df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("multiLine", "true") \
    .option("quote", '"') \
    .option("escape", '"') \
    .option("mode", "PERMISSIVE") \
    .csv(input_path)


# ==============================
# EXTRACT REGION FROM S3 PATH
# ==============================

df = df.withColumn(
    "source_file",
    input_file_name()
)

df = df.withColumn(
    "region",
    regexp_extract(
        "source_file",
        r"region=([^/]+)",
        1
    )
).drop("source_file")


# ==============================
# WRITE AS PARQUET
# ==============================

output_path = "s3://de-on-youtube-cleansed-useast1-s3/youtube/"

df.write \
    .mode("append") \
    .option("compression", "snappy") \
    .parquet(output_path)


job.commit()
