# Project Progress Log

Use one dated entry for each meaningful work session. Keep notes specific to what was actually tested. Do not record credentials, account IDs, or sensitive output.

## Entry — Captured Glue scripts for portfolio

- **Goal:** Preserve the actual AWS Glue ETL implementation in version control and document what the code shows.
- **What I did:** Captured four scripts from the AWS Glue Console and added them under `src/glue/`.
- **Scripts captured:**
  - `spark.py` — reads regional CSVs, extracts region from the source file path, writes Snappy Parquet in append mode.
  - `de-youtube-reference-explode-job.py` — reads multiline JSON, explodes `items`, selects reference fields, writes Snappy Parquet in overwrite mode.
  - `de-youtube-raw-to-cleansed-glue-job.py` — reads a Glue Catalog table, maps 17 columns, evaluates `ColumnCount > 0`, writes Snappy Parquet.
  - `de-youtube-statistics-reference-data-job.py` — reads a catalog table and a Parquet path, applies `gs_flatten(maxLevels=0)` to the catalog frame, then commits.
- **Verified from code:** The CSV job uses append mode; the JSON reference job uses overwrite mode. The data-quality ruleset contains only `ColumnCount > 0`.
- **Not yet verified:** Successful run statuses, output file existence and contents, final schemas/row counts, Athena query results, job orchestration, and the reference-data job's dependency/configuration.
- **Potential follow-up:** Inspect the Visual job's configuration for `de-youtube-statistics-reference-data-job` and confirm how `gs_flatten` is provided. The captured script does not show an output/write step for this job.
- **Next step:** Check Glue run history and output S3 paths, then add tested Athena queries and actual validation results.

## Entry template

### YYYY-MM-DD — Short task name

- **Goal:**
- **What I did:**
- **Expected result:**
- **Actual result:**
- **Error or issue:**
- **Root cause:** (only after confirmed)
- **Fix and verification:**
- **What I learned:**
- **Next step:**
