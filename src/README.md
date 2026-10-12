# Glue Source Code

This directory contains the four AWS Glue job scripts copied from the AWS Console for documentation and version control.

| File | Purpose visible in the script |
|---|---|
| `spark.py` | Reads regional YouTube CSVs from S3, derives a `region` column from the source path, writes Snappy Parquet in append mode. |
| `de-youtube-reference-explode-job.py` | Reads multiline JSON reference data, explodes `items`, selects six fields, and writes Snappy Parquet in overwrite mode. |
| `de-youtube-raw-to-cleansed-glue-job.py` | Reads the `raw_statistics` Glue Catalog table, maps field types, evaluates `ColumnCount > 0`, and writes Snappy Parquet. |
| `de-youtube-statistics-reference-data-job.py` | Reads a reference-data catalog table and Parquet path, applies `gs_flatten` to the catalog frame, then commits. Its output behavior and dependency should be investigated. |

## Running the jobs

These are AWS Glue scripts, not standalone local Python programs. They depend on the AWS Glue runtime, IAM permissions, catalog resources, S3 paths, and (for the statistics reference-data job) the `gs_flatten` module. Do not run them locally as ordinary Python scripts and do not execute them in production without reviewing the job configuration and write modes.

## Before calling the pipeline verified

- Confirm each job's successful run in AWS Glue.
- Confirm output S3 objects, schema, row counts, and sample records.
- Review append/overwrite behavior and rerun safety.
- Verify any custom module and job dependencies.
- Record tested Athena queries and results.
