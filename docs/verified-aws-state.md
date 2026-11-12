# AWS Verification Record

This file records evidence gathered from the connected AWS environment. Treat it as a snapshot, not a live status page. Re-run checks before deployment or a CV claim.

## AWS resource inventory

The read-only inventory in `us-east-1` found:

- 5 S3 buckets, including the raw and cleansed YouTube buckets.
- 6 Glue jobs and 6 Glue crawlers.
- 1 active Lambda function: `de-youtube-raw-useast1-lambda-json-sheet` (Python 3.12, handler `index.lambda_handler`).
- 0 Step Functions state machines.
- No S3 bucket notifications were configured on the raw bucket, no Lambda event-source mappings were found for the JSON/reference-data function, and the function has no resource-based policy.
- The Lambda environment points at `s3://de-on-youtube-cleansed-useast1-s3/youtube` with `write_data_operation=append`; leave it untouched until its code and intended invocation path are reviewed.
- The account is not subscribed to Amazon QuickSight. Dashboard/analysis listing returned `UnsupportedUserEditionException`; the dataset listing returned zero datasets.

The Lambda deployment package is not yet captured in this repository. No Step Functions orchestration was found in this region during the inspection. A QuickSight dashboard has not been deployed.

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

1. Capture and review the existing Lambda deployment package before changing its append-mode behavior or invocation path.
2. Decide whether to create a Step Functions workflow; none currently exists, and the existing staging/curation jobs intentionally use fixed, non-overwriting output prefixes.
3. Subscribe to QuickSight only if the account owner approves the service and any associated charges; otherwise use the validated Athena queries with Power BI or another BI tool.
4. Investigate the observed mojibake in some text fields (for example, `GarcÃ­a`) in a separate encoding-correction transformation. Do not alter the validated numeric dataset in place.
5. Review the 649 conflicting business keys and establish a documented reconciliation rule before promoting any quarantined variants.
