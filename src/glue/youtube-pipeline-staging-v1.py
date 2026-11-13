import json
import sys
import boto3
from datetime import datetime, timezone

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, BooleanType
)

args = getResolvedOptions(
    sys.argv,
    ["JOB_NAME", "RUN_ID", "RAW_PATH", "OUTPUT_BUCKET", "OUTPUT_PREFIX"],
)
sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

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
    .load(args["RAW_PATH"])
    .withColumn("region", F.regexp_extract(F.input_file_name(), r"region=([^/]+)", 1))
    .withColumn("run_id", F.lit(args["RUN_ID"]))
    .cache()
)

total_rows = df.count()
region_rows = df.groupBy("region").count().orderBy("region").collect()
regions = [r["region"] for r in region_rows if r["region"]]
malformed_rows = df.filter(F.col("_corrupt_record").isNotNull()).count()
if total_rows < 300000 or len(regions) != 10:
    raise RuntimeError(
        f"Raw input validation failed: rows={total_rows}, regions={regions}"
    )
if malformed_rows:
    raise RuntimeError(f"Malformed CSV rows detected: {malformed_rows}")

output = df.drop("_corrupt_record")
output_prefix = args["OUTPUT_PREFIX"].strip("/")
output_path = f"s3://{args['OUTPUT_BUCKET']}/{output_prefix}"
run_prefix = f"{output_prefix}/run_id={args['RUN_ID']}/"
s3 = boto3.client("s3")
existing = s3.list_objects_v2(
    Bucket=args["OUTPUT_BUCKET"], Prefix=run_prefix, MaxKeys=1
)
if existing.get("KeyCount", 0):
    raise RuntimeError(f"Refusing to reuse non-empty staging run prefix: {run_prefix}")
(
    output.write.mode("append")
    .format("parquet")
    .option("compression", "snappy")
    .partitionBy("run_id", "region")
    .save(output_path)
)

metrics = {
    "job": args["JOB_NAME"],
    "run_id": args["RUN_ID"],
    "source_rows": total_rows,
    "regions": [{"region": r["region"], "rows": r["count"]} for r in region_rows],
    "malformed_rows": malformed_rows,
    "output_path": output_path,
    "completed_at_utc": datetime.now(timezone.utc).isoformat(),
}
print("STAGING_METRICS=" + json.dumps(metrics, sort_keys=True))
df.unpersist()
job.commit()
