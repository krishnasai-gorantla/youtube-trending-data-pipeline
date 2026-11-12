# Athena SQL

Run these queries in the Athena workgroup configured for the project. They assume the Glue Data Catalog database `db_youtube_cleaned`.

- `01_table_validation.sql` — row counts for the two core datasets. This query was previously executed successfully; the recorded results were 375,942 and 311 rows respectively. Re-run it to refresh the counts.
- `02_category_performance.sql` — category-level descriptive analysis using the `youtube` and `statistics_reference_data` tables. This query is provided for validation and analysis; it has not yet been recorded as executed.

Do not describe an unexecuted query as tested. Record the execution date, workgroup, query execution ID, and result summary when validating additional SQL.
