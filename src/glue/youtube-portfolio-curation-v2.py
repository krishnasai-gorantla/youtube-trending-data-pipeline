import sys
import json
import logging
from datetime import datetime, timezone

from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F

args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "SOURCE_DATABASE",
        "SOURCE_TABLE",
        "OUTPUT_BUCKET",
        "OUTPUT_PREFIX",
        "EXPECTED_SAFE_ROWS",
        "EXPECTED_REGIONS",
    ],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("youtube-portfolio-curation-v2")

sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

source_name = f'{args["SOURCE_DATABASE"]}.{args["SOURCE_TABLE"]}'
source = glue_context.create_dynamic_frame.from_catalog(\n    database=args["SOURCE_DATABASE"],\n    table_name=args["SOURCE_TABLE"],\n).toDF()

business_key = ["region", "video_id", "trending_date"]
all_columns = source.columns

required = set(business_key)
missing = sorted(required.difference(all_columns))
if missing:
    raise ValueError(f"Source table is missing required columns: {missing}")

# Reject null/blank IDs and Excel formula-error literals. Keep these rows
# in quarantine rather than silently treating them as valid video IDs.
invalid_id = (
    F.col("video_id").isNull()
    | (F.length(F.trim(F.col("video_id"))) == 0)
    | (F.upper(F.trim(F.col("video_id"))) == "#NAME?")
)
invalid_rows = (
    source.filter(invalid_id)
    .withColumn("issue_type", F.lit("invalid_video_id"))
)

valid_rows = source.filter(~invalid_id)

# Remove only exact full-row duplicates. Never arbitrarily pick one version
# when records share a business key but disagree on one or more attributes.
exact_dedup = valid_rows.dropDuplicates(all_columns)

conflicting_keys = (
    exact_dedup.groupBy(*business_key)
    .count()
    .filter(F.col("count") > 1)
    .select(*business_key)
)

conflicting_rows = (
    exact_dedup.join(conflicting_keys, business_key, "inner")
    .withColumn("issue_type", F.lit("conflicting_business_key"))
)

safe_rows = exact_dedup.join(conflicting_keys, business_key, "left_anti")

source_count = source.count()
invalid_count = invalid_rows.count()
valid_count = valid_rows.count()
exact_unique_count = exact_dedup.count()
conflict_key_count = conflicting_keys.count()
conflict_row_count = conflicting_rows.count()
safe_count = safe_rows.count()
region_count = safe_rows.select("region").distinct().count()

expected_safe = int(args["EXPECTED_SAFE_ROWS"])
expected_regions = int(args["EXPECTED_REGIONS"])

if safe_count != expected_safe:
    raise ValueError(
        f"Safe row count mismatch: expected {expected_safe}, found {safe_count}. "
        "Review the source changes before publishing."
    )
if region_count != expected_regions:
    raise ValueError(
        f"Region count mismatch: expected {expected_regions}, found {region_count}."
    )

# Final safety assertions before any write.
if safe_rows.filter(invalid_id).limit(1).count():
    raise ValueError("Invalid video ID found in safe output.")
if safe_rows.groupBy(*business_key).count().filter(F.col("count") > 1).limit(1).count():
    raise ValueError("Duplicate business key found in safe output.")

root = f's3://{args["OUTPUT_BUCKET"]}/{args["OUTPUT_PREFIX"].strip("/")}'
safe_path = f"{root}/safe"
quarantine_path = f"{root}/quarantine"

# errorifexists prevents an accidental rerun from overwriting an earlier run.
safe_rows.write.mode("errorifexists").format("parquet").option(
    "compression", "snappy"
).partitionBy("region").save(safe_path)

quarantine = invalid_rows.unionByName(conflicting_rows, allowMissingColumns=True)
quarantine.write.mode("errorifexists").format("parquet").option(
    "compression", "snappy"
).partitionBy("region").save(quarantine_path)

metrics = {
    "job": "youtube-portfolio-curation-v2",
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "source_table": source_name,
    "source_rows": source_count,
    "invalid_video_id_rows": invalid_count,
    "valid_rows_before_dedup": valid_count,
    "exact_unique_rows": exact_unique_count,
    "conflicting_business_key_groups": conflict_key_count,
    "conflicting_rows_quarantined": conflict_row_count,
    "safe_rows_published": safe_count,
    "safe_regions": region_count,
    "safe_output": safe_path,
    "quarantine_output": quarantine_path,
}
logger.info("CURATION_METRICS=%s", json.dumps(metrics, sort_keys=True))
job.commit()
