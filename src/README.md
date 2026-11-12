# Source Code

## AWS Glue jobs

| File | Role | Observed status / notes |
|---|---|---|
| `glue/spark.py` | Reads regional CSVs and appends Parquet to the main cleansed prefix | One successful run observed; a prior run failed on missing S3 `PutObject` permission |
| `glue/de-youtube-reference-explode-job.py` | Explodes category JSON reference data to Parquet | Successful run observed |
| `glue/de-youtube-raw-to-cleansed-glue-job.py` | Reads raw CSV catalog table, applies mappings and writes Parquet | Historical runs failed parsing MX/KR CSV files; writes to same prefix as `spark.py` |
| `glue/de-youtube-statistics-reference-data-job.py` | Applies Glue Studio `gs_flatten` transform to catalog DynamicFrame | A successful run observed after supplying `gs_flatten.py`; captured script has no output/write step |
| `glue/youtube-tutorial-staging-validation.py` | Reads CSVs with explicit schema and ISO-8859-1 encoding; validates minimum row count and 10 regions; writes partitioned staging Parquet | Successful run observed on 17 October 2026; Athena subsequently confirmed 375,942 rows across 10 regions |

The staging-validation script is copied from the successful AWS Glue job. It is retained as an observed implementation, not yet a complete data-quality solution: it counts malformed rows and missing IDs but does not fail/quarantine those records, and it drops the corrupt-record column before writing.

## Lambda

The AWS environment also contains one active Lambda function, `de-youtube-raw-useast1-lambda-json-sheet`. Its deployment package has not yet been captured in this repository. See [lambda/README.md](lambda/README.md).

## Runtime requirements

These are AWS Glue scripts, not standalone local Python programs. They require the AWS Glue runtime, configured IAM roles, catalog resources and S3 paths. The reference-data job additionally requires the Glue Studio `gs_flatten` dependency supplied through `--extra-py-files`.

Do not rerun append-mode jobs against existing prefixes or overwrite existing datasets during recovery. Use a new test prefix and compare results first.
