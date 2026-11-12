# AWS Verification Record

This file records evidence gathered from the connected AWS environment. Treat it as a snapshot, not a live status page. Re-run checks before deployment or a CV claim.

## AWS resource inventory

The read-only inventory in `us-east-1` found:

- 5 S3 buckets, including the raw and cleansed YouTube buckets.
- 5 Glue jobs and 6 Glue crawlers.
- 1 active Lambda function: `de-youtube-raw-useast1-lambda-json-sheet` (Python 3.12, handler `index.lambda_handler`).
- 0 Step Functions state machines.

The Lambda deployment package is not yet captured in this repository. No Step Functions orchestration was found in this region during the inspection. QuickSight resources were not audited, so no claim is made about dashboards.

## Glue job run history inspected

The Glue API inspection returned the following evidence:

| Glue job | Observed run state | Evidence / issue |
|---|---|---|
| `spark` | Latest returned run: SUCCEEDED (8 Sep 2026) | An earlier run failed at the Parquet write with `s3:PutObject` denied for the cleansed bucket prefix |
| `de-youtube-reference-explode-job` | SUCCEEDED (8 Sep 2026) | Latest returned run succeeded |
| `de-youtube-statistics-reference-data-job` | Latest returned run: SUCCEEDED (8 Sep 2026) | An earlier run failed with `ModuleNotFoundError: gs_flatten`; current job arguments include `gs_flatten.py` via `--extra-py-files` |
| `de-youtube-raw-to-cleansed-glue-job` | Latest returned runs: FAILED (8 Sep 2026) | Errors identify `MXvideos.csv` and `KRvideos.csv` as files that could not be parsed |
| `youtube-tutorial-staging-validation` | SUCCEEDED (17 Oct 2026) | Uses explicit schema and ISO-8859-1 encoding; writes partitioned Parquet to a separate staging prefix |

The API request for most jobs was limited to the latest five returned records. This is not a complete historical audit.

## S3 output presence

The inspection found these objects under the cleansed bucket:

| Prefix | Objects returned |
|---|---:|
| `s3://de-on-youtube-cleansed-useast1-s3/youtube/` | 10 Parquet objects |
| `s3://de-on-youtube-cleansed-useast1-s3/statistics_reference_data/` | 4 Parquet objects |

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
| Exact duplicate extra rows | 12,386 |
| Conflicting duplicate extra rows | 659 |
| Keys with conflicting rows | 649 |

Query execution ID: `57b0bd72-f6b8-4392-911a-69d56b68a71c`.

This means the staging output is a useful baseline, but not a clean final fact table. Exact duplicates can be removed safely; conflicting duplicate keys require an explicit reconciliation rule or quarantine.

### Category reference join

The reference table contained 311 rows and 32 distinct category IDs. A direct join by ID produced 3,734,265 joined rows because each category ID is repeated across regional reference files. Grouping the reference table to one row per ID restored 375,942 joined rows.

- Direct join query ID: `4f9c07c2-1726-42d5-8b65-27c18afa3047`.
- Deduplicated lookup query ID: `4946a41d-80c0-435f-b0ef-f8b523134400`.
- Reference row/ID count query ID: `a46a78c6-e792-4cf8-9dd2-2d9efd9fcd4e`.

The revised category-performance query executed successfully and returned 99 region/category rows after deduplicating the reference lookup, removing exact duplicate records, excluding conflicting business keys and filtering the literal `#NAME?` IDs. Query execution ID: `2ee40cd5-aa84-4d28-8b9d-57c613765327`.

A follow-up query found no category IDs with more than one distinct title across the regional copies (query ID `0c3620b4-aa82-4673-a67e-11408fa8f216`). If localized category names are required in a future dataset, preserve the region key rather than collapsing by ID.

## Earlier Athena count query

An earlier successful query returned 375,942 rows in `db_youtube_cleaned.youtube` and 311 rows in `db_youtube_cleaned.statistics_reference_data`.

Query execution ID: `19ad23fd-b42e-4b92-9e50-198954d261ad`.

## Catalog observations

The cleaned database `db_youtube_cleaned` contained six tables during inspection, including `youtube`, `tutorial_staging_youtube`, `statistics_reference_data`, `youtube_analytics`, `youtube_curated`, and a table named `cleaned_statistics_reference_data`. The last table's location was under the `youtube/` prefix and should be checked before use.

## Safe next verification steps

1. Inspect the Glue staging job's CloudWatch log for its malformed-row count.
2. Quarantine `#NAME?` IDs and malformed CSV rows rather than silently dropping the corrupt-record marker.
3. Remove exact duplicate rows and quarantine the 649 conflicting business keys for reconciliation.
4. Deduplicate category reference data by ID (or retain region for localized labels).
5. Confirm every Glue Catalog table's S3 location and schema.
6. Re-run Athena checks after each isolated transformation and compare counts before promotion.
