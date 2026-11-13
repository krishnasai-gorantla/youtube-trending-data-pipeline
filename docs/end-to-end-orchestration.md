# Automated AWS pipeline

## What is automated

The Step Functions workflow `youtube-trending-end-to-end` orchestrates the project in this order. It can be started manually, or automatically by the S3/EventBridge batch-ready trigger described below:

1. Generates a unique run ID for each execution.
2. Reads the 10 raw regional CSV files from the existing S3 raw layer.
3. Writes a new run-partitioned staging dataset as Snappy Parquet.
4. Runs the staging Glue crawler to register the new run and region partitions.
5. Curates the run: invalid video IDs are quarantined, exact duplicate rows are removed, and every conflicting business-key variant is quarantined rather than arbitrarily selected.
6. Writes safe and quarantine outputs to separate run-partitioned S3 prefixes.
7. Runs separate crawlers to register safe and quarantine partitions in Glue Data Catalog.

The original raw, tutorial staging, and v2 curated outputs are preserved. The automated jobs use unique `run_id` partitions and append only after checking that the run-specific output prefix is empty. Reusing a run ID is rejected, and previous runs are never overwritten.

## AWS resources

- Step Functions: `youtube-trending-end-to-end`
- Glue jobs: `youtube-pipeline-staging-v1`, `youtube-pipeline-curation-v1`
- Glue tables: `youtube_pipeline_staging`, `youtube_pipeline_safe`, `youtube_pipeline_quarantine`
- Glue crawlers: `youtube-pipeline-staging-crawler`, `youtube-pipeline-safe-crawler`, `youtube-pipeline-quarantine-crawler`
- Staging S3 root: `s3://de-on-youtube-cleansed-useast1-s3/staging/youtube_pipeline/`
- Curated S3 roots: `s3://de-on-youtube-cleansed-useast1-s3/curated/youtube_pipeline/safe/` and `.../quarantine/`

## Query a completed run

After the execution succeeds, copy the `run_id` from the execution's `AssignRunId` state output. Use it in the automated-pipeline SQL files:

- `sql/09_pipeline_region_kpis.sql`
- `sql/10_pipeline_category_performance.sql`
- `sql/11_pipeline_top_videos.sql`

Replace the `<RUN_ID>` placeholder with the exact run ID. The earlier `sql/06` through `sql/08` files remain tied to the independently verified v2 snapshot.

## Automatic start from S3

The raw bucket has EventBridge notifications enabled. The enabled EventBridge rule `youtube-pipeline-batch-ready` matches S3 `Object Created` events for keys matching `pipeline_triggers/*.ready` and starts the state machine using a dedicated least-privilege role. The event pattern was tested successfully with `TestEventPattern`.

After uploading all 10 regional CSVs for a new batch, upload a small marker object to the raw bucket at `pipeline_triggers/<unique-batch-id>.ready`. The marker content is not read; its unique key is the batch-complete signal. Do not upload the marker until all 10 files are complete. Use a new marker key for every batch and avoid overwriting/re-uploading a marker, because S3/EventBridge delivery is at-least-once and duplicate notifications can start duplicate executions.

## Manual start / recovery

For a manual run, start a Step Functions execution with an empty JSON object. The state machine generates its own run ID:

```json
{}
```

A successful execution means both Glue jobs completed and all three crawlers returned to READY. The curation job performs hard validation before publishing: it requires 10 regions, no invalid IDs in the safe set, and no duplicate business keys. Review the Glue run logs for row counts and quarantine metrics.

## Query the latest or a specific run

The Glue tables are partitioned by `run_id` and `region`. Filter by run ID for reproducible comparisons:

```sql
SELECT region, count(*) AS safe_rows
FROM db_youtube_cleaned.youtube_pipeline_safe
WHERE run_id = '<execution-run-id>'
GROUP BY region
ORDER BY region;
```

## Cost and limitations

The workflow is event-driven by an explicit batch-ready marker rather than by each CSV object, so a partial 10-file upload does not start ETL. Each execution starts two Glue jobs, so it incurs Glue DPU charges. No QuickSight subscription or other paid dashboard service is enabled by this implementation.
