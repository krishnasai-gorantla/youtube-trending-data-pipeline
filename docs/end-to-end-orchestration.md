# Automated AWS pipeline

## Implemented workflow

The Step Functions state machine `youtube-trending-end-to-end` coordinates:

1. Generation of a unique run ID.
2. Reading the 10 regional raw CSV files from S3.
3. Writing run-partitioned staging data as Snappy Parquet.
4. Running the staging Glue crawler.
5. Applying validation and curation: invalid IDs are quarantined, exact duplicates are removed, and conflicting business-key variants are quarantined.
6. Writing safe and quarantine Parquet outputs to separate run-partitioned S3 prefixes.
7. Running separate Glue crawlers to register safe and quarantine partitions.

Two executions completed successfully on 13 November 2026. A first attempt failed due to a Spark output-path collision; the jobs were corrected to write to empty run-specific prefixes, and a retry succeeded. See [verified-aws-state.md](verified-aws-state.md) for execution IDs and validation evidence.

## AWS resources

- Step Functions: `youtube-trending-end-to-end`
- Glue jobs: `youtube-pipeline-staging-v1`, `youtube-pipeline-curation-v1`
- Glue tables: `youtube_pipeline_staging`, `youtube_pipeline_safe`, `youtube_pipeline_quarantine`
- Glue crawlers: `youtube-pipeline-staging-crawler`, `youtube-pipeline-safe-crawler`, `youtube-pipeline-quarantine-crawler`
- Staging S3 root: `s3://de-on-youtube-cleansed-useast1-s3/staging/youtube_pipeline/`
- Curated S3 roots: `s3://de-on-youtube-cleansed-useast1-s3/curated/youtube_pipeline/safe/` and `.../quarantine/`

## Data-quality rules

The business key is `(region, video_id, trending_date)`. The curation process:
- rejects blank, null or literal `#NAME?` video IDs;
- removes exact duplicate rows;
- quarantines every row for a business key when non-identical variants conflict;
- validates the expected regional coverage before publishing the safe dataset.

The latest verified run produced 359,936 safe rows across 10 regions, with zero invalid IDs and zero duplicate business-key groups in the safe output. The corresponding quarantine snapshot contains 2,312 invalid-ID rows and 1,298 conflicting rows.

## Current operating status — cost controls

The state machine remains defined and available for deliberate manual execution, but **automatic triggering is paused**:

- EventBridge rule `youtube-pipeline-batch-ready`: **DISABLED**.
- Raw S3 bucket EventBridge notification configuration: empty.
- No running Step Functions executions were present in the latest check.
- Dashboard scheduled refresh workflow: removed from active workflows and retained only as a disabled archive.
- JSON-reference Lambda reserved concurrency: **0**.

Do not upload a `.ready` marker expecting it to trigger a run. The trigger must be intentionally reconfigured before any future automated batch. Manual Step Functions/Glue/Athena execution can incur usage-based AWS charges.

## Dashboard

The static dashboard reads `docs/dashboard/data.json`. It can be viewed locally without AWS. The latest committed JSON snapshot is from 13 November 2026. GitHub Pages publishing is separate and requires Pages to be enabled in repository Settings → Pages → Build and deployment → Source: GitHub Actions, followed by a manual run of the Publish dashboard workflow.

## Cost and limitations

Each full pipeline execution starts two Glue jobs and crawlers, and Athena queries are usage-based. AWS credits do not guarantee that usage is free or prevent charges after credits are exhausted. QuickSight is not subscribed or used by this project.
