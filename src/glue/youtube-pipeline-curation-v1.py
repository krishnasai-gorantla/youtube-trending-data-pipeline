import json
import logging
import sys
from datetime import datetime, timezone

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F

args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME", "RUN_ID", "SOURCE_DATABASE", "SOURCE_TABLE",
        "OUTPUT_BUCKET", "OUTPUT_PREFIX", "EXPECTED_REGIONS",
    ],
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("youtube-pipeline-curation")
sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

run_id = args["RUN_ID"]
source_dyf = glue_context.create_dynamic_frame.from_catalog(
    database=args["SOURCE_DATABASE"],
    table_name=args["SOURCE_TABLE"],
    push_down_predicate=f"run_id == '{run_id}'",
)
source = source_dyf.toDF()
if not source.take(1):
    raise RuntimeError(f"No staged rows found for run_id={run_id}")

business_key = ["region", "video_id", "trending_date"]
missing = sorted(set(business_key + ["run_id"]).difference(source.columns))
if missing:
    raise ValueError(f"Staging table missing required columns: {missing}")

invalid_id = (
    F.col("video_id").isNull()
    | (F.length(F.trim(F.col("video_id"))) == 0)
    | (F.upper(F.trim(F.col("video_id"))) == "#NAME?")
)
invalid_rows = source.filter(invalid_id).withColumn(
    "issue_type", F.lit("invalid_video_id")
)
valid_rows = source.filter(~invalid_id)
data_columns = [c for c in source.columns if c not in ("run_id",)]
exact_dedup = valid_rows.dropDuplicates(data_columns + ["run_id"])
conflicting_keys = (
    exact_dedup.groupBy(*business_key)
    .count()
    .filter(F.col("count") > 1)
    .select(*business_key)
)
conflicting_rows = exact_dedup.join(
    conflicting_keys, business_key, "inner"
).withColumn("issue_type", F.lit("conflicting_business_key"))
safe_rows = exact_dedup.join(conflicting_keys, business_key, "left_anti")

source_count = source.count()
invalid_count = invalid_rows.count()
exact_unique_count = exact_dedup.count()
conflict_key_count = conflicting_keys.count()
conflict_row_count = conflicting_rows.count()
safe_count = safe_rows.count()
region_count = safe_rows.select("region").distinct().count()
expected_regions = int(args["EXPECTED_REGIONS"])

if region_count != expected_regions:
    raise ValueError(
        f"Expected {expected_regions} safe regions; found {region_count}"
    )
if safe_rows.filter(invalid_id).limit(1).count():
    raise ValueError("Invalid video ID found in safe output")
if safe_rows.groupBy(*business_key).count().filter(
    F.col("count") > 1
).limit(1).count():
    raise ValueError("Duplicate business key found in safe output")

root = f"s3://{args['OUTPUT_BUCKET']}/{args['OUTPUT_PREFIX'].strip('/')}"
safe_path = f"{root}/safe"
quarantine_path = f"{root}/quarantine"
(
    safe_rows.write.mode("errorifexists")
    .format("parquet").option("compression", "snappy")
    .partitionBy("run_id", "region").save(safe_path)
)
quarantine = invalid_rows.unionByName(
    conflicting_rows, allowMissingColumns=True
)
(
    quarantine.write.mode("errorifexists")
    .format("parquet").option("compression", "snappy")
    .partitionBy("run_id", "region").save(quarantine_path)
)

metrics = {
    "job": args["JOB_NAME"],
    "run_id": run_id,
    "source_table": f"{args['SOURCE_DATABASE']}.{args['SOURCE_TABLE']}",
    "source_rows": source_count,
    "invalid_video_id_rows": invalid_count,
    "exact_unique_rows": exact_unique_count,
    "conflicting_business_key_groups": conflict_key_count,
    "conflicting_rows_quarantined": conflict_row_count,
    "safe_rows_published": safe_count,
    "safe_regions": region_count,
    "safe_output": safe_path,
    "quarantine_output": quarantine_path,
    "completed_at_utc": datetime.now(timezone.utc).isoformat(),
}
logger.info("CURATION_METRICS=%s", json.dumps(metrics, sort_keys=True))
job.commit()
