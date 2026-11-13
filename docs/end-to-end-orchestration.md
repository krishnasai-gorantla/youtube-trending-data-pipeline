# Automated AWS pipeline

## What is automated

The Step Functions workflow `youtube-trending-end-to-end` orchestrates the project in this order:

1. Generates a unique run ID for each execution.
2. Reads the 10 raw regional CSV files from the existing S3 raw layer.
3. Writes a new run-partitioned staging dataset as Snappy Parquet.
4. Runs the staging Glue crawler to register the new run and region partitions.
5. Curates the run: invalid video IDs are quarantined, exact duplicate rows are removed, and every conflicting business-key variant is quarantined rather than arbitrarily selected.
6. Writes safe and quarantine outputs to separate run-partitioned S3 prefixes.
7. Runs separate crawlers to register safe and quarantine partitions in Glue Data Catalog.

The original raw, tutorial staging, and v2 curated outputs are preserved. The automated jobs use new S3 prefixes and unique `run_id` partitions. They do not use append mode or overwrite existing runs.

## AWS resources

- Step Functions: `youtube-trending-end-to-end`
- Glue jobs: `youtube-pipeline-staging-v1`, `youtube-pipeline-curation-v1`
- Glue tables: `youtube_pipeline_staging`, `youtube_pipeline_safe`, `youtube_pipeline_quarantine`
- Glue crawlers: `youtube-pipeline-staging-crawler`, `youtube-pipeline-safe-crawler`, `youtube-pipeline-quarantine-crawler`
- Staging S3 root: `s3://de-on-youtube-cleansed-useast1-s3/staging/youtube_pipeline/`
- Curated S3 roots: `s3://de-on-youtube-cleansed-useast1-s3/curated/youtube_pipeline/safe/` and `.../quarantine/`

## Run it

Start a Step Functions execution with an empty JSON object. The state machine generates its own run ID:

```json
{}
```

A successful execution means the two Glue jobs completed and all three crawlers returned to READY. The curation job performs hard validation before publishing: it requires 10 regions, no invalid IDs in the safe set, and no duplicate business keys. Review the Glue run logs for row counts and quarantine metrics.

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

The workflow is manually started; it does not run a schedule or react to each S3 object event. This avoids triggering multiple overlapping full-data runs for the 10-file batch. Each execution starts two Glue jobs, so it incurs Glue DPU charges. No QuickSight subscription or other paid dashboard service is enabled by this implementation.
