# AWS Verification Record

This file records evidence gathered from the connected AWS environment. Treat it as a dated snapshot, not a live status page. Re-run checks before deployment or a CV claim.

## Glue job run history inspected

The most recent runs returned by the Glue API inspection were dated **8 September 2026**.

| Glue job | Observed run state | Evidence / issue |
|---|---|---|
| `spark` | Latest returned run: SUCCEEDED | An earlier run failed at the Parquet write with `s3:PutObject` denied for the cleansed bucket prefix |
| `de-youtube-reference-explode-job` | SUCCEEDED | Latest returned run succeeded |
| `de-youtube-statistics-reference-data-job` | Latest returned run: SUCCEEDED | An earlier run failed with `ModuleNotFoundError: gs_flatten`; current job arguments include `gs_flatten.py` via `--extra-py-files` |
| `de-youtube-raw-to-cleansed-glue-job` | Latest returned runs: FAILED | Errors identify `MXvideos.csv` and `KRvideos.csv` as files that could not be parsed |

The API request for job runs was limited to the latest five returned records per job. This is not a complete historical audit.

## S3 output presence

The inspection found these objects under the cleansed bucket:

| Prefix | Objects returned |
|---|---:|
| `s3://de-on-youtube-cleansed-useast1-s3/youtube/` | 10 Parquet objects |
| `s3://de-on-youtube-cleansed-useast1-s3/statistics_reference_data/` | 4 Parquet objects |

Object presence confirms that files exist. It does not independently prove their correctness, freshness, uniqueness, or completeness.

## Athena verification

A non-destructive Athena query successfully executed:

```sql
SELECT 'youtube' AS dataset, COUNT(*) AS row_count
FROM db_youtube_cleaned.youtube
UNION ALL
SELECT 'statistics_reference_data' AS dataset, COUNT(*) AS row_count
FROM db_youtube_cleaned.statistics_reference_data;
```

Recorded result:

| Dataset | Row count |
|---|---:|
| `db_youtube_cleaned.youtube` | 375,942 |
| `db_youtube_cleaned.statistics_reference_data` | 311 |

Query execution ID: `19ad23fd-b42e-4b92-9e50-198954d261ad`.

These counts are historical. They do not establish the latest run state or prove that the data is free of duplicates and malformed records.

## Catalog observations

The cleaned database `db_youtube_cleaned` contained six tables during inspection, including:

- `youtube` — main statistics table, including `region`, `video_id`, `category_id`, views and engagement fields.
- `statistics_reference_data` — category reference fields including `id` and `snippet_title`.
- `youtube_analytics`, `youtube_curated`, and `tutorial_staging_youtube` — additional analytics/curated/staging tables.

A table named `cleaned_statistics_reference_data` was also present with a location under the `youtube/` prefix. Its schema/location should be checked before it is used. Do not assume all six tables are current or correctly mapped.

## Safe next verification steps

1. Re-run the two Athena row-count queries.
2. Check the latest Glue job run status and full error messages.
3. Inspect sample rows, schema and region distribution in Athena.
4. Compare source record counts with output counts and check duplicate business keys.
5. Confirm each catalog table's S3 location.
6. Test any new transformation in a new S3 prefix; do not overwrite the existing data.
