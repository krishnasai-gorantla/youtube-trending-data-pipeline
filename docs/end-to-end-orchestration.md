# AWS pipeline orchestration

## What the workflow does

The Step Functions state machine `youtube-trending-end-to-end` coordinates these stages:

1. Creates a unique run ID.
2. Reads the 10 regional raw CSV files from S3.
3. Writes staging data as Snappy Parquet, partitioned by run and region.
4. Runs the staging Glue crawler.
5. Runs the curation Glue job. It rejects invalid IDs, removes exact duplicate rows and quarantines conflicting business-key records.
6. Writes safe and quarantine outputs to separate run-specific S3 prefixes.
7. Runs crawlers to register the safe and quarantine outputs in the Glue Data Catalog.

The workflow completed successful test executions on 13 November 2026. One earlier attempt exposed an output-path collision. The jobs were changed to use empty run-specific output prefixes, and the retry succeeded.

## AWS resources

- Step Functions: `youtube-trending-end-to-end`
- Glue jobs: `youtube-pipeline-staging-v1`, `youtube-pipeline-curation-v1`
- Glue tables: `youtube_pipeline_staging`, `youtube_pipeline_safe`, `youtube_pipeline_quarantine`
- Glue crawlers: `youtube-pipeline-staging-crawler`, `youtube-pipeline-safe-crawler`, `youtube-pipeline-quarantine-crawler`
- Staging S3 root: `s3://de-on-youtube-cleansed-useast1-s3/staging/youtube_pipeline/`
- Safe output: `s3://de-on-youtube-cleansed-useast1-s3/curated/youtube_pipeline/safe/`
- Quarantine output: `s3://de-on-youtube-cleansed-useast1-s3/curated/youtube_pipeline/quarantine/`

## Data-quality rules

The business key is `(region, video_id, trending_date)`.

- Blank, null and literal `#NAME?` video IDs are rejected.
- Exact duplicate rows are removed.
- If different rows share a business key, all variants for that key are quarantined.
- The safe output is checked for duplicate business keys and expected regional coverage.

The latest verified run produced 359,936 safe rows across 10 regions. The quarantine output contained 2,312 invalid-ID rows and 1,298 conflicting rows. Athena checks found zero duplicate business-key groups in the safe output.

## Current operating status

The pipeline has been tested, but automatic execution is paused to avoid ongoing AWS costs.

- EventBridge rule `youtube-pipeline-batch-ready`: disabled.
- Raw bucket EventBridge notification configuration: empty.
- Dashboard scheduled refresh workflow: not active; the previous workflow is archived under `docs/disabled-workflows/`.
- JSON-reference Lambda reserved concurrency: 0.
- Step Functions state machine: retained and available for deliberate manual execution.
- No running executions were present at the latest check.

Do not expect a `.ready` marker upload to start a pipeline run while the trigger is disabled. Manual Step Functions, Glue and Athena activity can incur usage-based charges.

## Dashboard

The dashboard reads `docs/dashboard/data.json`, a committed snapshot of Athena query results. It does not query AWS in the browser. GitHub Pages is enabled and the publish workflow has completed successfully. Publishing the static page does not run the AWS pipeline.

## Evidence

See [verified-aws-state.md](verified-aws-state.md) for execution details, validation query IDs and the recorded AWS checks.
