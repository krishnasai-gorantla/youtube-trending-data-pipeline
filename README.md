# YouTube Trending Data Pipeline

A hands-on data engineering portfolio project using Amazon S3, AWS Glue, PySpark, Parquet, and the YouTube Trending Videos dataset. The project explores ingesting regional source files, extracting reference data from JSON, applying schema mappings and data-quality checks, and writing analytics-friendly data to S3.

> **Status:** The four AWS Glue job scripts have been captured from the AWS Console and added to this repository. Runtime success, output contents, and end-to-end orchestration still need to be documented with verified evidence.

## Technology stack

- **Amazon S3** — raw and cleansed data storage
- **AWS Glue / Glue Data Catalog** — ETL jobs, catalog-based input, and data-quality evaluation
- **PySpark** — CSV/JSON processing, flattening arrays, column selection, and type casting
- **Parquet + Snappy** — columnar output format and compression
- **Git / GitHub** — version control and project documentation
- **Amazon Athena / SQL** — include verified queries here when available

## Data flow represented by the captured scripts

```text
Regional YouTube CSV files
  s3://de-youtube-raw-useast1-krishna-2026/youtube/raw_statistics/*/*.csv
                 |
                 v
        Glue job: spark
        - read CSV with header/schema inference
        - extract region from source file path
        - append Snappy Parquet
                 |
                 v
  s3://de-on-youtube-cleansed-useast1-s3/youtube/

Reference JSON files
  s3://de-youtube-raw-useast1-krishna-2026/youtube/raw_statistics_reference_data/*.json
                 |
                 v
 Glue job: de-youtube-reference-explode-job
 - explode items array
 - select and rename reference fields
 - cast id to bigint
                 |
                 v
  s3://de-on-youtube-cleansed-useast1-s3/statistics_reference_data/
                 |
                 v
 Glue job: de-youtube-raw-to-cleansed-glue-job
 - read raw_statistics from Glue Data Catalog
 - map 17 columns to explicit types
 - evaluate ColumnCount > 0
 - write Snappy Parquet to cleansed S3 path
```

The diagram summarizes code paths, not a verified execution order or proof that every job succeeded. The statistics reference-data job also reads catalog data and the cleansed Parquet path, then calls a flatten transform; its captured script does not currently write an output. Review its visual-job configuration and dependency before treating it as a completed pipeline stage.

## Captured Glue jobs

| Script | Purpose visible in code | Important implementation detail |
|---|---|---|
| [`spark.py`](src/glue/spark.py) | Reads regional CSVs, extracts `region` from the source path, writes Parquet | Uses append mode; reruns may append duplicate records unless controlled |
| [`de-youtube-reference-explode-job.py`](src/glue/de-youtube-reference-explode-job.py) | Explodes JSON `items`, selects reference fields, writes Parquet | Uses overwrite mode at the reference-data output path |
| [`de-youtube-raw-to-cleansed-glue-job.py`](src/glue/de-youtube-raw-to-cleansed-glue-job.py) | Reads catalog table `de-youtube-raw.raw_statistics`, maps 17 fields, evaluates a basic data-quality rule, writes Parquet | Rule `ColumnCount > 0` checks that the frame has columns; it does not validate every row or field |
| [`de-youtube-statistics-reference-data-job.py`](src/glue/de-youtube-statistics-reference-data-job.py) | Reads reference data from the catalog and a Parquet path; applies `gs_flatten(maxLevels=0)` to the catalog DynamicFrame | Captured code does not use the Parquet frame in the flatten call or write an output; investigate configuration and dependency |

## Repository structure

```text
.
├── docs/
│   └── architecture.md
├── notes/
│   └── progress-log.md
├── sql/
│   └── README.md
├── src/
│   ├── glue/
│   │   ├── spark.py
│   │   ├── de-youtube-reference-explode-job.py
│   │   ├── de-youtube-raw-to-cleansed-glue-job.py
│   │   └── de-youtube-statistics-reference-data-job.py
│   └── README.md
├── .gitignore
└── README.md
```

## Verification checklist

- [x] Regional CSVs uploaded to the raw S3 bucket (reported during project work).
- [x] Four Glue job scripts captured from the AWS Console and committed here.
- [ ] Verify the Glue job run status and review logs for each job.
- [ ] Verify expected Parquet objects and schemas in the cleansed S3 paths.
- [ ] Confirm Glue Catalog tables and partitions match the actual files.
- [ ] Inspect the reference-data visual job and the `gs_flatten` dependency.
- [ ] Check whether rerunning append-mode CSV processing duplicates records.
- [ ] Add tested Athena SQL and record sample results/row counts.
- [ ] Add a final end-to-end run record and cite the original tutorial and dataset source.

Do not mark a checkbox complete until you have verified it in your AWS environment.

## Security and data handling

- Never commit AWS access keys, secret keys, passwords, session tokens, or `.env` files.
- The scripts contain S3 bucket names and paths. These are not credentials, but review whether you want to expose resource naming in a public portfolio.
- Keep raw CSV/JSON datasets and generated Parquet files out of Git unless there is a clear, safe reason to include a small sample.
- Do not commit private account details, personal data, or unredacted logs/screenshots.
- Prefer IAM roles and least-privilege permissions.

## Learning outcomes demonstrated by the code

- Reading CSV and multiline JSON from S3 with Spark
- Extracting metadata from input file paths
- Exploding nested arrays and selecting nested JSON fields
- Applying explicit Glue schema mappings
- Writing Parquet with Snappy compression
- Using Glue Data Catalog inputs and a data-quality evaluation rule
- Understanding idempotency implications of append versus overwrite modes

## Acknowledgements

Add the exact tutorial title/link and dataset source/licence here before presenting this as a finished public portfolio project.
