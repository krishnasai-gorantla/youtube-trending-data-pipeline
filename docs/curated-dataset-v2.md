# Curated YouTube analytics dataset — v2

This job reads the existing Glue Catalog table `db_youtube_cleaned.tutorial_staging_youtube`. It does not modify the raw bucket, staging prefix, existing Glue jobs, or existing tables.

## Data rules

1. Reject null, blank, and literal `#NAME?` video IDs into quarantine.
2. Remove exact full-row duplicates.
3. Quarantine every row belonging to a repeated business key `(region, video_id, trending_date)` when the distinct rows disagree. No arbitrary winner is selected.
4. Publish only rows with unique business keys.

The verified baseline is 359,936 safe rows across 10 regions. The job fails before writing if the safe row or region count differs from that baseline, so source drift requires review rather than silently publishing a different dataset. The completed Glue 5.1 run produced 359,936 safe rows, 2,312 invalid-ID rows and 1,298 conflicting rows (649 conflicting business-key groups).

## Isolated output

- Safe Parquet: `s3://de-on-youtube-cleansed-useast1-s3/curated/youtube_portfolio_v2/safe/`
- Quarantine Parquet: `s3://de-on-youtube-cleansed-useast1-s3/curated/youtube_portfolio_v2/quarantine/`

Both writes use `errorifexists`. A rerun cannot overwrite existing output. If a run partially writes and fails, inspect the prefix and remove it manually only after review; do not point this job at an existing prefix.

## Glue job arguments

- `--SOURCE_DATABASE db_youtube_cleaned`
- `--SOURCE_TABLE tutorial_staging_youtube`
- `--OUTPUT_BUCKET de-on-youtube-cleansed-useast1-s3`
- `--OUTPUT_PREFIX curated/youtube_portfolio_v2`
- `--EXPECTED_SAFE_ROWS 359936`
- `--EXPECTED_REGIONS 10`

Glue 5.1, Python 3, two G.1X workers. The job uses the existing `de-youtube-glue-s3-role`. Its S3 write access to the new curation prefix and the Glue script asset path was checked before execution.

## Validation after the run

Both output locations are registered as separate Glue Catalog tables: `db_youtube_cleaned.youtube_portfolio_v2` and `db_youtube_cleaned.youtube_portfolio_v2_quarantine`. Athena `MSCK REPAIR TABLE` completed for both. Validation returned 359,936 safe rows, 10 regions, zero invalid IDs and zero duplicate business-key groups. Quarantine contains 2,312 `invalid_video_id` rows and 1,298 `conflicting_business_key` rows. The validation SQL is in `sql/05_curated_validation.sql`.
