# Pipeline Architecture and Implementation Notes

## Scope

This document separates the intended data flow from what is visible in the captured scripts and the AWS resources inspected. It avoids assuming that the jobs run in a particular order or that a successful run of one job proves the whole pipeline works.

## 1. Raw ingestion

Regional YouTube trending CSVs and category reference JSON files were uploaded to Amazon S3. The raw bucket paths used by the captured scripts are:

- CSV: `s3://de-youtube-raw-useast1-krishna-2026/youtube/raw_statistics/*/*.csv`
- JSON: `s3://de-youtube-raw-useast1-krishna-2026/youtube/raw_statistics_reference_data/*.json`

The raw Glue database inspected was `de-youtube-raw`, with tables `raw_statistics` and `raw_statistics_reference_data`.

## 2. Regional CSV transformation

The captured `spark.py` script:

1. Reads CSV files with header parsing, schema inference, multiline records, quote/escape handling and permissive mode.
2. Adds the input file path and extracts `region` from a `region=...` path segment.
3. Writes Snappy-compressed Parquet to `s3://de-on-youtube-cleansed-useast1-s3/youtube/`.
4. Uses **append** mode.

### Risks to resolve

- Reprocessing the same source files can append duplicate records.
- CSV parsing must be tested against all regional files and the actual encoding.
- The job's S3 write permissions must be scoped to the target prefix.
- The current output prefix is also used by the catalog-based raw-to-cleansed job.

## 3. Category reference JSON transformation

The captured `de-youtube-reference-explode-job.py` script:

1. Reads multiline JSON.
2. Explodes the top-level `items` array.
3. Selects `kind`, `etag`, `id`, `snippet.channelId`, `snippet.title`, and `snippet.assignable`.
4. Casts `id` to `bigint`.
5. Writes Snappy Parquet in **overwrite** mode to `s3://de-on-youtube-cleansed-useast1-s3/statistics_reference_data/`.

Overwrite mode replaces the contents at the target prefix on a successful write. Confirm that this is intentional before rerunning it.

## 4. Catalog-based raw-to-cleansed job

The captured `de-youtube-raw-to-cleansed-glue-job.py` reads `de-youtube-raw.raw_statistics`, applies explicit mappings to 17 fields, evaluates the rule `ColumnCount > 0`, and writes Parquet to the same `youtube/` prefix used by `spark.py`.

The rule `ColumnCount > 0` checks the presence of columns; it does not validate row-level nulls, duplicate keys, numeric ranges, timestamps, or business rules. The recorded job failures identify CSV parsing problems in `MXvideos.csv` and `KRvideos.csv`.

## 5. Statistics reference-data job

The captured `de-youtube-statistics-reference-data-job.py`:

- reads `de-youtube-raw.raw_statistics_reference_data` from the Data Catalog;
- reads Parquet from the cleansed `statistics_reference_data/` prefix;
- applies `gs_flatten(maxLevels=0)` to the catalog DynamicFrame; and
- commits the job.

In the captured script, the Parquet DynamicFrame is not passed to the flatten transform and no explicit output/write operation appears. The AWS job configuration supplies `gs_flatten.py` through `--extra-py-files`. The job's intended role must be confirmed from the Glue Studio visual graph before it is redesigned.

## 6. Analytics layer

The inspected cleaned catalog database was `db_youtube_cleaned`. It included `youtube`, `statistics_reference_data`, and several staging/curated tables. The `youtube` table exposes a `region` column and fields including `video_id`, `category_id`, `views`, `likes`, and `comment_count`. The reference table exposes `id` and `snippet_title`, which can be joined to map category IDs to names.

Athena is enabled and was used to count rows in the two main tables. See [verified-aws-state.md](verified-aws-state.md) and the SQL files for the recorded evidence.

## 7. Recovery design

1. Preserve the current S3 data and the four captured Glue scripts.
2. Fix the CSV reader and validate every source file in an isolated test output prefix.
3. Give each transformation a distinct output prefix; do not have two jobs write to `youtube/`.
4. Add row-level quality checks: required columns, null key fields, duplicate business keys, valid region, parseable dates, and non-negative metrics.
5. Make reruns deterministic. Use a clean versioned output prefix or partition overwrite strategy with explicit run controls.
6. Build curated category/region aggregates only after the cleansed dataset passes checks.
7. Validate Glue Catalog locations and schemas against the actual S3 output.
8. Add orchestration and BI only after each individual stage has repeatable evidence.

No AWS resources should be deleted or overwritten as part of this documentation recovery.
