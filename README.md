# YouTube Trending Data Pipeline

A portfolio project exploring batch data engineering on AWS using the Kaggle YouTube Trending Videos dataset. The repository preserves the Glue scripts captured from the AWS environment and documents the verified state of the pipeline, its known defects, and the recovery plan.

> **Current state:** Historical S3 outputs and Athena tables exist, but the pipeline is not yet fully reproducible end to end. One Glue job has a confirmed CSV parsing failure, one has a prior IAM write failure, and one reference-data job needs its output behaviour clarified. See [the AWS verification record](docs/verified-aws-state.md).

## Project goals

- Land multi-region CSV and JSON source files in Amazon S3.
- Transform raw files into analytics-friendly Parquet using AWS Glue and PySpark.
- Register datasets in the AWS Glue Data Catalog.
- Query the datasets with Amazon Athena.
- Prepare reliable category and regional analysis for a BI dashboard.

## Architecture represented by the current implementation

```text
Kaggle YouTube Trending CSVs + category JSON
                    |
                    v
        Amazon S3 - raw layer
                    |
          AWS Glue Crawlers
                    |
          Glue Data Catalog
                    |
          AWS Glue / PySpark
             /          \
            v            v
    Regional CSV      Category JSON
    transformation    explode/flatten
            |            |
            v            v
        Amazon S3 - cleansed Parquet
                    |
          Glue Data Catalog
                    |
              Amazon Athena
                    |
       SQL analysis / BI-ready outputs
```

This diagram describes the intended flow from the scripts and AWS resources inspected so far. It does **not** imply that all jobs are orchestrated, that every job currently succeeds, or that a QuickSight dashboard is part of this repository.

## AWS services and tools

| Service / tool | Role in this project |
|---|---|
| Amazon S3 | Stores raw CSV/JSON and transformed Parquet |
| AWS Glue Crawlers | Discover schemas and update catalog tables |
| AWS Glue Data Catalog | Stores table metadata for ETL and Athena |
| AWS Glue / PySpark | Performs batch transformations |
| Amazon Athena | Runs SQL directly against S3-backed tables |
| GitHub | Stores scripts, SQL, documentation and validation checks |

## Repository structure

```text
.
├── .github/workflows/       # Automated repository checks
├── docs/                    # Architecture, AWS evidence and recovery plan
├── notes/                   # Project progress log
├── scripts/                 # Local repository validation
├── sql/                     # Athena validation and analysis queries
├── src/glue/                # Captured AWS Glue scripts
└── tests/                   # Lightweight repository tests
```

## Existing Glue scripts

| Script | What it currently does | Known concern |
|---|---|---|
| `src/glue/spark.py` | Reads regional CSVs, derives region from the S3 path, writes Snappy Parquet | Writes in append mode; repeated runs can duplicate data |
| `src/glue/de-youtube-reference-explode-job.py` | Explodes JSON `items`, selects category fields, writes Parquet | Uses overwrite mode; reruns replace the target prefix |
| `src/glue/de-youtube-raw-to-cleansed-glue-job.py` | Reads the raw catalog table, applies mappings and a basic data-quality ruleset, writes Parquet | Historical runs failed parsing MX/KR CSVs; output path overlaps the CSV job |
| `src/glue/de-youtube-statistics-reference-data-job.py` | Reads catalog and Parquet DynamicFrames and applies `gs_flatten` to the catalog frame | Captured code does not use the Parquet frame in the flatten operation or write a result |

The scripts are retained as evidence of the implementation that was present in AWS. They should not be treated as production-ready simply because they are in version control.

## Verification

The last recorded AWS inspection found:

- Athena successfully counted **375,942 rows** in `db_youtube_cleaned.youtube`.
- Athena successfully counted **311 rows** in `db_youtube_cleaned.statistics_reference_data`.
- The two S3 prefixes contained 10 Parquet objects under `youtube/` and 4 under `statistics_reference_data/`.
- The Glue run history included successful runs as well as the failures described in [the verification record](docs/verified-aws-state.md).

These are historical observations, not a guarantee that the resources still have the same state. Re-run the SQL in `sql/01_table_validation.sql` before relying on the counts.

## Run local checks

The Glue scripts require the AWS Glue runtime and cannot be executed as ordinary local Python programs. The repository checks validate Python syntax and project structure without connecting to AWS.

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q src/glue scripts tests
```

## Safety and reproducibility

- Do not rerun the append-mode job against the existing `youtube/` prefix until the duplicate-handling strategy is confirmed.
- Do not overwrite the current S3 datasets during recovery. Test new transformations in a separate versioned prefix first.
- Do not broaden IAM permissions just to make a job pass. Identify the exact bucket/prefix and grant only the required actions.
- Keep credentials, `.env` files, raw datasets, generated Parquet, and unredacted logs out of Git.
- The AWS resource names in the captured scripts are environment-specific. Replace them with configuration parameters before sharing a reusable deployment.
- A successful syntax check does not prove that an AWS Glue job will run successfully.

## References

- [Darshil Parmar's original YouTube Analytics project write-up](https://medium.com/@darshilp/end-to-end-data-engineering-project-youtube-analytics-1c7eebf0d31)
- [Related public project repository](https://github.com/darshilparmar/youtube-data-piepline-aws-s3-lambda-glue-athena-stepfunction)
- Dataset: [Trending YouTube Video Statistics](https://www.kaggle.com/datasets/datasnaek/youtube-new) — confirm the dataset's current licence and terms before redistributing data.

This repository is an independently maintained learning implementation. It is not affiliated with or endorsed by the tutorial author.
