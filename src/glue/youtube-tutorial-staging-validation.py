import sys

from pyspark.context import SparkContext
from pyspark.sql.functions import input_file_name, regexp_extract, col
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    LongType,
    BooleanType,
)

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

raw_path = "s3://de-youtube-raw-useast1-krishna-2026/youtube/raw_statistics/region=*/*.csv"
output_path = "s3://de-on-youtube-cleansed-useast1-s3/staging/tutorial_compat/youtube/"

schema = StructType([
    StructField("video_id", StringType(), True),
    StructField("trending_date", StringType(), True),
    StructField("title", StringType(), True),
    StructField("channel_title", StringType(), True),
    StructField("category_id", LongType(), True),
    StructField("publish_time", StringType(), True),
    StructField("tags", StringType(), True),
    StructField("views", LongType(), True),
    StructField("likes", LongType(), True),
    StructField("dislikes", LongType(), True),
    StructField("comment_count", LongType(), True),
    StructField("thumbnail_link", StringType(), True),
    StructField("comments_disabled", BooleanType(), True),
    StructField("ratings_disabled", BooleanType(), True),
    StructField("video_error_or_removed", BooleanType(), True),
    StructField("description", StringType(), True),
    StructField("_corrupt_record", StringType(), True),
])

df = (
    spark.read.format("csv")
    .option("header", "true")
    .option("inferSchema", "false")
    .option("multiLine", "true")
    .option("quote", '"')
    .option("escape", '"')
    .option("encoding", "ISO-8859-1")
    .option("mode", "PERMISSIVE")
    .option("columnNameOfCorruptRecord", "_corrupt_record")
    .schema(schema)
    .load(raw_path)
    .withColumn("region", regexp_extract(input_file_name(), r"region=([^/]+)", 1))
)

df = df.cache()
total = df.count()
region_counts = [
    (r["region"], r["count"])
    for r in df.groupBy("region").count().orderBy("region").collect()
]
malformed = df.filter(col("_corrupt_record").isNotNull()).count()
missing_id = df.filter(col("video_id").isNull() | (col("video_id") == "")).count()
regions = [r[0] for r in region_counts if r[0]]

if total < 300000 or len(regions) != 10:
    raise RuntimeError(
        "Staging validation failed: expected >300000 rows across 10 regions; "
        "got rows=%s regions=%s" % (total, regions)
    )

output = df.drop("_corrupt_record")
(
    output.write
    .mode("errorifexists")
    .format("parquet")
    .option("compression", "snappy")
    .partitionBy("region")
    .save(output_path)
)

print(
    "STAGING_VALIDATION_JSON={\"total_rows\":%s,\"regions\":%s,"
    "\"malformed_rows\":%s,\"missing_video_id_rows\":%s,"
    "\"output_path\":\"%s\"}"
    % (total, region_counts, malformed, missing_id, output_path)
)
df.unpersist()
job.commit()
