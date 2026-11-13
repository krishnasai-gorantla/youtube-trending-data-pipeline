# Current status correction — 13 November 2026

This section supersedes older status statements later in this file where they describe automatic triggers or scheduled refreshes as active.

At the latest check:
- The EventBridge rule `youtube-pipeline-batch-ready` is **DISABLED**.
- The raw S3 bucket EventBridge notification configuration is empty.
- The scheduled dashboard refresh workflow is not active; its file is retained only under `docs/disabled-workflows/`.
- The JSON-reference Lambda reserved concurrency is **0**.
- The Step Functions state machine and its successful execution history are retained. No execution was running at the latest check.
- GitHub Pages is enabled. The dashboard publish workflow completed successfully for commit `ddf4301414a35216aa8f0951ddf3648aebc605c8`.

The successful pipeline runs and query results recorded below remain historical evidence. They do not mean that automatic execution is currently enabled. Do not upload a marker expecting a run, and do not describe the dashboard as automatically refreshing.

---

# AWS Verification Record

This file records evidence gathered from the connected AWS environment. Treat it as a snapshot, not a live status page. Re-run checks before deployment or a CV claim.

## Current automated pipeline verification — 13 November 2026

A new Step Functions state machine was created and its first full execution completed successfully in `us-east-1`.

- State machine: `youtube-trending-end-to-end`
- ARN: `arn:aws:states:us-east-1:303102153405:stateMachine:youtube-trending-end-to-end`
- Execution ARN: `arn:aws:states:us-east-1:303102153405:execution:youtube-trending-end-to-end:3596e98a-451f-4438-9381-824f56e2b755`
- Execution: **SUCCEEDED**, 13 Nov 2026 12:23:53–12:37:01 UTC
- Generated run ID: `e8ac90d7-a4fb-4e95-a0c1-1320038d943f`

| Stage | Resource | Result |
|---|---|---|
| Raw CSV staging | `youtube-pipeline-staging-v1` | SUCCEEDED; 136 seconds; 272 DPU-seconds; 375,942 rows across 10 regions |
| Staging catalog | `youtube-pipeline-staging-crawler` | SUCCEEDED; `youtube_pipeline` table and run/region partitions registered |
| Curation and quarantine | `youtube-pipeline-curation-v1` | SUCCEEDED; 209 seconds; 419 DPU-seconds |
| Safe catalog | `youtube-pipeline-safe-crawler` | SUCCEEDED; `youtube_pipeline_safe` table and partitions registered |
| Quarantine catalog | `youtube-pipeline-quarantine-crawler` | SUCCEEDED; `youtube_pipeline_quarantine` table and partitions registered |

All three crawlers finished in READY state with `LastCrawl.Status=SUCCEEDED`. Total Glue compute recorded for the two jobs was 691 DPU-seconds. Each execution writes to a new `run_id` partition using append mode after checking that the run-specific output prefix is empty; reusing a run ID is rejected. The original raw, tutorial staging, and v2 curated outputs remain untouched.

**Athena checks for this run:**

| Validation | Result | Query execution ID |
|---|---:|---|
| Staging rows / regions | 375,942 / 10 | `e5241872-ce40-4b64-a746-9a244988e437` |
| Safe rows / regions / invalid IDs | 359,936 / 10 / 0 | `2e66d066-dd9c-4725-8bcd-8297848f0f5a` |
| Duplicate business-key groups in safe output | 0 | `a5761efc-9afe-4f01-a487-5e5f8702ee98` |
| Quarantine by issue type | 2,312 invalid IDs; 1,298 conflicting rows | `c69c6f83-ea60-41dc-bf3e-2b617724fe7a` |
| Regional dashboard metrics | 10 regional rows | `2651f081-35fc-4b33-a517-88f4e62c6bd4` |
| Top videos | 10 rows | `ae720345-cd6a-455b-b639-32de7e34a7d0` |

The safe output is in `s3://de-on-youtube-cleansed-useast1-s3/curated/youtube_pipeline/safe/`; quarantine is in `s3://de-on-youtube-cleansed-useast1-s3/curated/youtube_pipeline/quarantine/`. Glue Catalog tables are `db_youtube_cleaned.youtube_pipeline_safe` and `db_youtube_cleaned.youtube_pipeline_quarantine`. The run-scoped Athena templates are `sql/09` through `sql/11`.

**Trigger and dashboard status:** S3 EventBridge notifications are enabled on the raw bucket. The enabled rule `youtube-pipeline-batch-ready` matches `pipeline_triggers/*.ready` object-created events and targets the Step Functions state machine through a dedicated role with `states:StartExecution` only. The event pattern passed `TestEventPattern`; the trigger has now been fired with a controlled test marker and the retry completed successfully (see the latest rerun evidence above). To start a future batch automatically, upload all 10 regional CSVs first, then upload a unique marker object such as `pipeline_triggers/batch-2026-11-14.ready`. Use a new key per batch; S3/EventBridge delivery is at-least-once, so duplicate marker notifications can create duplicate executions. Manual execution with `{}` remains available for recovery.

Dashboard data is now refreshed automatically by GitHub Actions at minute 17 of every hour (and on manual dispatch). The workflow uses GitHub OIDC to assume `arn:aws:iam::303102153405:role/youtube-dashboard-refresh-github-actions`; its trust is restricted to this repository's immutable owner/repository IDs and `main` branch. Its permissions are limited to reading Step Functions execution metadata, the curated Glue Catalog tables and S3 Parquet, running Athena queries, and writing Athena results to a dedicated temporary prefix. It cannot start Glue jobs or modify source/curated data. The first authenticated refresh succeeded (workflow run `43432957979`); a follow-up run confirmed unchanged data does not create another commit (`43433160585`). The JSON output is `docs/dashboard/data.json`; `index.html` loads it with an embedded fallback snapshot.

GitHub Pages is not enabled yet. The publish workflow now detects that state and skips deployment cleanly instead of failing. Enable **Settings → Pages → Build and deployment → Source: GitHub Actions**, then run **Actions → Publish dashboard → Run workflow** once. After that, new dashboard data commits will be deployed automatically. Athena charges apply to scheduled refresh queries; QuickSight remains unsubscribed and no QuickSight subscription has been enabled.


## Latest end-to-end rerun — 13 November 2026

The S3/EventBridge trigger was exercised with a test batch-ready marker. The first trigger attempt exposed a Spark output-path collision: Spark rejected the existing dataset root even though the new run ID was unique. The Glue jobs were corrected to append only into a previously empty run-specific partition and to reject reuse of a populated run ID. The retry then completed successfully end to end.

- Marker: `s3://de-youtube-raw-useast1-krishna-2026/pipeline_triggers/verification-2026-11-13-retry.ready`
- EventBridge rule: `youtube-pipeline-batch-ready`
- Step Functions execution: `arn:aws:states:us-east-1:303102153405:execution:youtube-trending-end-to-end:8ddefb0c-332e-f8bc-fc31-f048315eafd6_19f8e221-332a-cc52-7905-5b1977ca6d14`
- Execution: **SUCCEEDED**, 13 Nov 2026 12:51:53–13:06:47 UTC
- Run ID: `72af6f39-6a91-4c80-954e-1d9a1830a588`

| Stage | Resource | Result |
|---|---|---|
| Raw CSV staging | `youtube-pipeline-staging-v1` | SUCCEEDED; 97 seconds; 194 DPU-seconds |
| Staging catalog | `youtube-pipeline-staging-crawler` | SUCCEEDED; crawler returned to READY |
| Curation and quarantine | `youtube-pipeline-curation-v1` | SUCCEEDED; 229 seconds; 458 DPU-seconds |
| Safe catalog | `youtube-pipeline-safe-crawler` | SUCCEEDED; crawler returned to READY |
| Quarantine catalog | `youtube-pipeline-quarantine-crawler` | SUCCEEDED; crawler returned to READY |

Total Glue compute for this run was 652 DPU-seconds (194 + 458). This test used the same source CSV batch, so the row counts and dashboard metrics are expected to match the prior successful run. It verifies that a fresh run ID can publish a second isolated set of partitions without overwriting the earlier run. A separate Athena query confirmed that both run IDs coexist in the safe table with 359,936 rows and 10 regions each (query execution ID `40525998-bba4-4e45-9107-7bf7b9f78a0a`).

**Independent Athena validation for this run:**

| Validation | Result | Query execution ID |
|---|---:|---|
| Safe rows / regions / invalid IDs / unique videos | 359,936 / 10 / 0 / 184,180 | `df03422c-775b-4ac9-8e25-bd6bdd297554` |
| Duplicate business-key groups in safe output | 0 | `2054a6f1-c752-43ee-8ad3-c97920a3e553` |
| Quarantine | 2,312 invalid IDs; 1,298 conflicting rows | `ed427d47-6a8e-421c-9947-3463cfee75f4` |
| Regional KPIs | 10 regional rows | `c97c8165-597b-410b-8387-e579251783bd` |
| Top videos | 10 rows | `035e2699-dc67-4d22-81c7-788be08e1ef5` |

The dashboard snapshot was refreshed to this latest run ID. Regional metrics match the previous successful execution because the underlying source batch did not change.

## Dashboard automation — 13 November 2026

- GitHub OIDC provider: `arn:aws:iam::303102153405:oidc-provider/token.actions.githubusercontent.com`
- Refresh role: `arn:aws:iam::303102153405:role/youtube-dashboard-refresh-github-actions`
- GitHub immutable repository identity in the trust condition: owner ID `341680151`, repository ID `1416165027`, branch `main`
- Schedule: hourly at minute 17 UTC, plus manual dispatch
- Successful refresh workflow: `43432957979`
- Idempotency check workflow: `43433160585` (succeeded; no data-change commit)
- Dashboard JSON: `docs/dashboard/data.json`
- Dashboard page: `docs/dashboard/index.html`

The scheduled job selects the latest successful Step Functions execution and refreshes region KPIs, top videos and data-quality metrics from Athena. It commits only when the dashboard payload changes. The refresh role uses short-lived GitHub OIDC credentials, not long-lived AWS keys in GitHub secrets. GitHub Pages still requires one-time enablement by the repository owner.

## AWS resource inventory

The read-only inventory in `us-east-1` found:

- 5 S3 buckets, including the raw and cleansed YouTube buckets.
- At the initial inventory: 6 Glue jobs and 6 Glue crawlers. The new pipeline adds 2 Glue jobs and 3 crawlers (8 jobs and 9 crawlers in total after deployment).
- 1 active Lambda function: `de-youtube-raw-useast1-lambda-json-sheet` (Python 3.12, handler `index.lambda_handler`).
- At the initial inventory: 0 Step Functions state machines. The `youtube-trending-end-to-end` state machine has since been created and successfully executed (see current verification above).
- No S3 bucket notifications were configured on the raw bucket, no Lambda event-source mappings were found for the JSON/reference-data function, and the function has no resource-based policy.
- The Lambda environment points at `s3://de-on-youtube-cleansed-useast1-s3/youtube` with `write_data_operation=append`; leave it untouched until its code and intended invocation path are reviewed.
- The account is not subscribed to Amazon QuickSight. Dashboard/analysis listing returned `UnsupportedUserEditionException`; the dataset listing returned zero datasets.

The Lambda deployment package is not yet captured in this repository. The initial inventory preceded creation of the new Step Functions workflow. A QuickSight dashboard has not been deployed.

## Glue job run history inspected

The Glue API inspection returned the following evidence:

| Glue job | Observed run state | Evidence / issue |
|---|---|---|
| `spark` | Latest returned run: SUCCEEDED (8 Sep 2026) | An earlier run failed at the Parquet write with `s3:PutObject` denied for the cleansed bucket prefix |
| `de-youtube-reference-explode-job` | SUCCEEDED (8 Sep 2026) | Latest returned run succeeded |
| `de-youtube-statistics-reference-data-job` | Latest returned run: SUCCEEDED (8 Sep 2026) | An earlier run failed with `ModuleNotFoundError: gs_flatten`; current job arguments include `gs_flatten.py` via `--extra-py-files` |
| `de-youtube-raw-to-cleansed-glue-job` | Latest returned runs: FAILED (8 Sep 2026) | Errors identify `MXvideos.csv` and `KRvideos.csv` as files that could not be parsed |
| `youtube-tutorial-staging-validation` | SUCCEEDED (17 Oct 2026) | Uses explicit schema and ISO-8859-1 encoding; writes partitioned Parquet to a separate staging prefix |
| `youtube-portfolio-curation-v2` | SUCCEEDED (12 Nov 2026) | 216 seconds, 433 DPU-seconds; writes safe and quarantine Parquet to a new isolated prefix |
| `youtube-pipeline-staging-v1` | SUCCEEDED (13 Nov 2026) | Initial run: 136 seconds / 272 DPU-seconds; latest triggered rerun: 97 seconds / 194 DPU-seconds |

| `youtube-pipeline-curation-v1` | SUCCEEDED (13 Nov 2026) | Initial run: 209 seconds / 419 DPU-seconds; latest triggered rerun: 229 seconds / 458 DPU-seconds |

The API request for most jobs was limited to the latest five returned records. This is not a complete historical audit.

## S3 output presence

The inspection found these objects under the cleansed bucket:

| Prefix | Objects returned |
|---|---:|
| `s3://de-on-youtube-cleansed-useast1-s3/youtube/` | 10 Parquet objects |
| `s3://de-on-youtube-cleansed-useast1-s3/statistics_reference_data/` | 4 Parquet objects |
| `s3://de-on-youtube-cleansed-useast1-s3/curated/youtube_portfolio_v2/safe/` | Partitioned Snappy Parquet, 10 regions |
| `s3://de-on-youtube-cleansed-useast1-s3/curated/youtube_portfolio_v2/quarantine/` | Partitioned Snappy Parquet, invalid and conflicting rows |

The staging job writes to `s3://de-on-youtube-cleansed-useast1-s3/staging/tutorial_compat/youtube/`. Object presence confirms that files exist; it does not independently prove their correctness, freshness, uniqueness, or completeness.

## Athena verification — staging and main table

A query executed successfully on 12 November 2026:

- `db_youtube_cleaned.tutorial_staging_youtube`: 375,942 rows, 10 regions, 0 blank video IDs.
- `db_youtube_cleaned.youtube`: 375,942 rows, 10 regions, 0 blank video IDs.

Query execution ID: `e30c01ab-643e-4cdd-b8e1-058943115fe7`.

A three-table validation query was also executed successfully, returning 375,942 rows in `youtube`, 375,942 rows in `tutorial_staging_youtube`, and 311 rows in `statistics_reference_data`. Query execution ID: `cd3d48e1-c819-4c69-b59a-9ce45cd80a1e`.

The staging job ran on Glue 5.1 with two G.1X workers for 133 seconds. Its CloudWatch output recorded 375,942 rows, 10 regions, `malformed_rows=0`, and `missing_video_id_rows=0`. This blank-ID check did not catch the literal `#NAME?` values reported below.

The staging region distribution was:

| Region | Rows |
|---|---:|
| ca | 40,881 |
| de | 40,840 |
| fr | 40,724 |
| gb | 38,916 |
| in | 37,352 |
| jp | 20,523 |
| kr | 34,567 |
| mx | 40,451 |
| ru | 40,739 |
| us | 40,949 |

Query execution ID: `37badbe0-2b57-4bc2-9020-59dd394b88d3`.

## Athena data-quality findings

The staging table quality query found:

| Check | Result |
|---|---:|
| Total rows | 375,942 |
| Distinct regions | 10 |
| Blank video IDs | 0 |
| Blank regions | 0 |
| Negative metric rows (views, likes, dislikes, comment_count) | 0 |
| Literal `#NAME?` video IDs | 2,312 |
| Usable non-blank, non-`#NAME?` video IDs | 373,630 |

Quality query ID: `043736e0-f242-4d89-b112-cfb75ee9fa67`.

### Duplicate business keys

The business key was defined as `region + video_id + trending_date`, excluding blank and literal `#NAME?` IDs.

| Duplicate check | Result |
|---|---:|
| Duplicate key groups | 12,703 |
| Extra rows beyond one per key | 13,045 |
| Exact duplicate extra rows (full-column distinct) | 12,396 |
| Conflicting distinct variants beyond one per key | 649 |
| Keys with conflicting rows | 649 |
| Rows retained after exact deduplication and excluding conflicting keys | 359,936 |

An improved audit using `SELECT DISTINCT` across every source column (rather than concatenated signatures) confirmed the counts above. Query execution ID: `0a17a220-591c-4152-87f5-22e2126e359d`.

This means the staging output is a useful baseline, but not a clean final fact table. Exact duplicates can be removed safely; conflicting duplicate keys require an explicit reconciliation rule or quarantine.

### Category reference join

The reference table contained 311 rows and 32 distinct category IDs. A direct join by ID produced 3,734,265 joined rows because each category ID is repeated across regional reference files. Grouping the reference table to one row per ID restored 375,942 joined rows.

- Direct join query ID: `4f9c07c2-1726-42d5-8b65-27c18afa3047`.
- Deduplicated lookup query ID: `4946a41d-80c0-435f-b0ef-f8b523134400`.
- Reference row/ID count query ID: `a46a78c6-e792-4cf8-9dd2-2d9efd9fcd4e`.

The revised category-performance query executed successfully and returned 99 region/category rows after deduplicating the reference lookup, removing exact duplicate records, excluding conflicting business keys and filtering the literal `#NAME?` IDs. Query execution ID: `2ee40cd5-aa84-4d28-8b9d-57c613765327`.

A follow-up query found no category IDs with more than one distinct title across the regional copies (query ID `0c3620b4-aa82-4673-a67e-11408fa8f216`). If localized category names are required in a future dataset, preserve the region key rather than collapsing by ID.

## Curated dataset v2 — successful Glue run

The new `youtube-portfolio-curation-v2` job read `db_youtube_cleaned.tutorial_staging_youtube` and wrote only to the new `curated/youtube_portfolio_v2/` prefix. It did not modify the raw or staging data, existing Glue jobs, or existing tables.

- Glue run ID: `jr_905767603af8b4b55f6361a6c0634f7c11705508674bf956d09eeb2045365263`
- State: SUCCEEDED; execution time 216 seconds; 433 DPU-seconds.
- Safe table: `db_youtube_cleaned.youtube_portfolio_v2`
- Quarantine table: `db_youtube_cleaned.youtube_portfolio_v2_quarantine`
- Both tables were registered in the Glue Data Catalog and their region partitions repaired with Athena `MSCK REPAIR TABLE`.

Athena independently verified:

| Check | Result |
|---|---:|
| Safe rows | 359,936 |
| Distinct regions | 10 |
| Invalid IDs in safe table | 0 |
| Duplicate business-key groups in safe table | 0 |
| Invalid video IDs quarantined | 2,312 |
| Conflicting rows quarantined | 1,298 |
| Conflicting business-key groups | 649 |

The 1,298 conflicting rows represent variants associated with 649 business-key groups; the pipeline quarantines all variants rather than selecting an arbitrary winner.

- Safe row/region/invalid-ID query ID: `2c10828f-e06f-4ec9-a9c9-1904335de85c`
- Duplicate-key validation query ID: `d203a273-1512-4af1-9286-6f19fd0f9f6e`
- Quarantine breakdown query ID: `14c3e695-bfdb-464b-9581-16ae67a6f92f`
- Region distribution query ID: `78254065-834a-4702-bdcf-8accc12176e4`
- Safe-table partition repair query ID: `27c63162-036d-420d-8d4b-1f409803220f`
- Quarantine-table partition repair query ID: `5818c4e9-f8ae-421b-ae9e-cde9ee8e6049`

### BI query verification

Three additional dashboard queries executed successfully against the curated table:

- Regional KPIs: `26f0f7ac-218a-4e7e-bf44-8401e5813612`
- Regional category performance: `d85900bd-bbf4-4a88-8c46-c641780ddb91`
- Top videos: `1bf09354-dd09-4a79-9f53-8ae0ecd43498`

The queries are committed under `sql/06` through `sql/08`. Their metric definitions and BI deployment limitation are documented in `docs/dashboard-data-model.md`.
## Earlier Athena count query

An earlier successful query returned 375,942 rows in `db_youtube_cleaned.youtube` and 311 rows in `db_youtube_cleaned.statistics_reference_data`.

Query execution ID: `19ad23fd-b42e-4b92-9e50-198954d261ad`.

## Catalog observations

The cleaned database `db_youtube_cleaned` contained eight tables after curation, including the original tables plus `youtube_portfolio_v2` and `youtube_portfolio_v2_quarantine`. The `cleaned_statistics_reference_data` table's location was under the `youtube/` prefix and should be checked before use.

## Safe next verification steps

1. Capture and review the existing Lambda deployment package before changing its append-mode behavior or invocation path; it remains separate from the new workflow.
2. If hands-off batch initiation is required, deploy and test an S3 batch-ready marker trigger for the state machine. The current state machine is fully orchestrated but manually started.
3. Enable GitHub Pages in repository settings if a hosted dashboard URL is required; otherwise open `docs/dashboard/index.html` directly from the repository. The dashboard is a static query snapshot.
4. Subscribe to QuickSight only if the account owner approves the service and any associated charges; no subscription has been enabled.
5. Investigate the observed mojibake in some text fields (for example, `GarcÃ­a`) in a separate encoding-correction transformation. Do not alter the validated numeric dataset in place.
6. Review the 649 conflicting business keys and establish a documented reconciliation rule before promoting any quarantined variants.


## Current cost-control verification — 13 November 2026 (supersedes older trigger/refresh statements above)

A fresh read-only AWS check was performed after the pipeline tests. The following are the current observed settings:

| Control | Current observed state |
|---|---|
| EventBridge rule `youtube-pipeline-batch-ready` | **DISABLED** |
| Raw S3 bucket EventBridge notification configuration | Empty |
| Lambda `de-youtube-raw-useast1-lambda-json-sheet` reserved concurrency | **0** |
| Step Functions state machine | ACTIVE (definition retained; manual starts remain possible) |
| Running executions in latest returned execution list | None; returned executions were SUCCEEDED, FAILED, SUCCEEDED |
| Dashboard scheduled refresh workflow | Removed from active `.github/workflows/`; archived under `docs/disabled-workflows/` |
| QuickSight account settings | No account settings found; this is consistent with QuickSight not being provisioned for this project |

**Important correction to earlier sections in this file:** the EventBridge rule is no longer enabled, the raw bucket currently has no EventBridge notification configuration, and the dashboard refresh is no longer scheduled hourly. Earlier instructions in this historical record describing automatic marker-triggered runs or hourly refreshes are historical implementation notes, not current operating instructions. Do not upload a marker expecting it to trigger a run.

The state machine, Glue resources, S3 source/curated data and committed dashboard snapshot are preserved. The state machine is still ACTIVE, so a deliberate manual execution can incur Glue and other usage charges. No claim is made that all AWS costs are zero or that the remaining AWS credit guarantees free usage. Check Billing and Cost Explorer directly for current charges and credit balance.
