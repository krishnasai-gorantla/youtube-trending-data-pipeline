# Curated YouTube analytics dataset — v2

This job reads the existing Glue Catalog table `db_youtube_cleaned.tutorial_staging_youtube`. It does not modify the raw bucket, staging prefix, existing Glue jobs, or existing tables.

## Data rules

1. Reject null, blank, and literal `#NAME?` video IDs into quarantine.
2. Remove exact full-row duplicates.
3. Quarantine every row belonging to a repeated business key `(region, video_id, trending_date)` when the distinct rows disagree. No arbitrary winner is selected.
4. Publish only rows with unique business keys.

The verified baseline is 359,936 safe rows across 10 regions. The job fails before writing if the safe row or region count differs from that baseline, so source drift requires review rather than silently publishing a different dataset.

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

Glue 5.1, Python 3, two G.1X workers. The job uses the existing `de-youtube-glue-s3-role`; confirm its write permissions cover only the intended output prefix and the Glue script asset path before execution.

## Validation after the run

Register the two output locations as separate Glue Catalog tables, then run `sql/05_curated_validation.sql`. Confirm 359,936 safe rows, 10 regions, no invalid IDs, and no duplicate business keys. Quarantine counts are retained for audit.
