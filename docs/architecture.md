# Pipeline Architecture

## Scope

This document describes the data paths visible in the four Glue job scripts captured from AWS Glue Studio. It does not assume that jobs ran successfully or that all steps are orchestrated in this order.

## Regional statistics CSV path

1. The `spark` job reads CSV files matching `s3://de-youtube-raw-useast1-krishna-2026/youtube/raw_statistics/*/*.csv`.
2. It enables header parsing, schema inference, multiline records, CSV quoting/escaping, and permissive parsing.
3. It adds the input file path temporarily, extracts a region using the `region=([^/]+)` regular expression, then drops the temporary path column.
4. It writes Snappy-compressed Parquet to `s3://de-on-youtube-cleansed-useast1-s3/youtube/` in **append** mode.

**Operational note:** append mode can duplicate data when a job is rerun over the same input. Confirm whether the pipeline has a separate deduplication or cleanup strategy.

## Reference-data JSON path

1. The `de-youtube-reference-explode-job` reads multiline JSON from `s3://de-youtube-raw-useast1-krishna-2026/youtube/raw_statistics_reference_data/*.json`.
2. It explodes the top-level `items` array and selects `kind`, `etag`, `id`, `snippet.channelId`, `snippet.title`, and `snippet.assignable`.
3. It casts `id` to `bigint` and writes Snappy-compressed Parquet in **overwrite** mode to `s3://de-on-youtube-cleansed-useast1-s3/statistics_reference_data/`.

**Operational note:** overwrite mode replaces existing output at the target path on each successful write.

## Catalog-based cleansed job

The `de-youtube-raw-to-cleansed-glue-job` reads `de-youtube-raw.raw_statistics` from the Glue Data Catalog, maps 17 fields to explicit types, runs a data-quality evaluation with `ColumnCount > 0`, and writes Snappy Parquet to `s3://de-on-youtube-cleansed-useast1-s3/youtube/`.

The configured rule is a basic schema/frame check; it does not establish that values are non-null, valid, unique, or business-correct.

## Statistics reference-data job: investigate

The captured `de-youtube-statistics-reference-data-job`:
- reads `de-youtube-raw.raw_statistics_reference_data` from the Data Catalog;
- reads Parquet from `s3://de-on-youtube-cleansed-useast1-s3/statistics_reference_data/`;
- calls `gs_flatten(maxLevels=0)` on the catalog DynamicFrame; and
- commits the Glue job.

In the captured script, the Parquet DynamicFrame is not used by the flatten operation and there is no explicit output/write step. Inspect the Visual job configuration and how the `gs_flatten` module is supplied before describing its role more definitively.

## Verification checklist

- [ ] Confirm successful run status and review logs for each Glue job.
- [ ] Confirm the raw and cleansed paths exist and contain expected files.
- [ ] Validate output row counts, schemas, and representative records.
- [ ] Confirm Glue Data Catalog tables and partitions reflect actual output.
- [ ] Confirm whether the statistics reference-data job has additional visual configuration or dependencies.
- [ ] Check append-mode reruns for duplicate data.
- [ ] Execute Athena queries and preserve safe, representative results.
- [ ] Document orchestration, triggers, job dependencies, and the actual run order.

## Security

S3 paths and resource names are included because they appear in the submitted scripts. Review whether these identifiers should remain public. Never commit credentials, tokens, account secrets, or unredacted sensitive logs.
