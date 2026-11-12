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

## 3. Successful staging-validation path

A fifth Glue job, `youtube-tutorial-staging-validation`, was present in AWS but missing from the original GitHub repository. Its script is now preserved at `src/glue/youtube-tutorial-staging-validation.py`.

The job:

1. Reads all regional CSVs using an explicit schema and `ISO-8859-1` encoding.
2. Uses permissive CSV parsing and captures malformed records in `_corrupt_record`.
3. Extracts the region from the source S3 path.
4. Requires at least 300,000 rows and exactly 10 non-empty region values.
5. Writes Snappy Parquet partitioned by region to `s3://de-on-youtube-cleansed-useast1-s3/staging/tutorial_compat/youtube/` using `errorifexists`.

This job succeeded on 17 October 2026. Athena later confirmed 375,942 rows across 10 regions in `db_youtube_cleaned.tutorial_staging_youtube`.

**Important limitation:** the script counts malformed rows and blank video IDs, but does not enforce a threshold for either; it drops `_corrupt_record` before writing. Its CloudWatch output reported zero malformed rows and zero blank IDs, but Athena found 2,312 literal `#NAME?` video IDs, which are non-blank and therefore passed that check. The staging job is the best current baseline, but it still needs a quarantine/rejection policy.

## 4. Category reference JSON transformation

The captured `de-youtube-reference-explode-job.py` script:

1. Reads multiline JSON.
2. Explodes the top-level `items` array.
3. Selects `kind`, `etag`, `id`, `snippet.channelId`, `snippet.title`, and `snippet.assignable`.
4. Casts `id` to `bigint`.
5. Writes Snappy Parquet in **overwrite** mode to `s3://de-on-youtube-cleansed-useast1-s3/statistics_reference_data/`.

The reference table contains 311 rows but only 32 distinct category IDs. Each category ID is repeated across regional source files. Joining it directly on `category_id = id` multiplies statistics rows. Deduplicate the reference table by `id` before joining, or retain region in the reference data if localized labels are required.

## 5. Catalog-based raw-to-cleansed job

The captured `de-youtube-raw-to-cleansed-glue-job.py` reads `de-youtube-raw.raw_statistics`, applies explicit mappings to 17 fields, evaluates the rule `ColumnCount > 0`, and writes Parquet to the same `youtube/` prefix used by `spark.py`.

The rule `ColumnCount > 0` checks the presence of columns; it does not validate row-level nulls, duplicate keys, numeric ranges, timestamps, or business rules. The recorded job failures identify CSV parsing problems in `MXvideos.csv` and `KRvideos.csv`.

## 6. Statistics reference-data job

The captured `de-youtube-statistics-reference-data-job.py`:

- reads `de-youtube-raw.raw_statistics_reference_data` from the Data Catalog;
- reads Parquet from the cleansed `statistics_reference_data/` prefix;
- applies `gs_flatten(maxLevels=0)` to the catalog DynamicFrame; and
- commits the job.

In the captured script, the Parquet DynamicFrame is not passed to the flatten transform and no explicit output/write operation appears. The AWS job configuration supplies `gs_flatten.py` through `--extra-py-files`. The job's intended role must be confirmed from the Glue Studio visual graph before it is redesigned.

## 7. Analytics and observed data quality

The cleaned database `db_youtube_cleaned` includes `youtube`, `tutorial_staging_youtube`, and `statistics_reference_data`. Athena checks on the staging table found:

- 375,942 rows across 10 regions.
- Zero blank video IDs, zero blank regions and zero negative values in views, likes, dislikes or comment counts.
- 2,312 rows where `video_id = '#NAME?'`.
- 12,703 duplicate business-key groups (`region, video_id, trending_date`) with 13,045 extra rows among otherwise valid IDs. A full-column `SELECT DISTINCT` audit found 12,396 exact duplicate extra rows and 649 conflicting variants across 649 keys. After exact deduplication and excluding conflicting keys, 359,936 rows remain as a conservative analytics subset.
- 311 reference rows but only 32 distinct category IDs. A direct join on category ID inflated the row count from 375,942 to 3,734,265. A deduplicated category lookup restores a one-row-per-video-observation join.

These results show why row counts and non-null checks alone are insufficient. See [verified-aws-state.md](verified-aws-state.md) and the Athena SQL files for query IDs and reproducible checks.

## 8. Recovery design

1. Preserve the current raw and cleansed S3 data and all captured job scripts.
2. Use the successful staging output as the baseline for comparisons, not as a fully clean final dataset.
3. Reject or quarantine formula-error IDs and malformed CSV records with source-file lineage.
4. Deduplicate exact duplicate rows and explicitly reconcile conflicting business keys.
5. Give each transformation a distinct output prefix; do not have two jobs write to `youtube/`.
6. Make reruns deterministic and validate output counts before promotion.
7. Deduplicate reference data by ID or preserve region for localized category names.
8. Confirm Glue Catalog locations and schemas against the actual S3 output.
9. Add orchestration and BI only after each stage has repeatable evidence.

No AWS resources should be deleted or overwritten as part of this documentation recovery.
