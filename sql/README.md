# Athena SQL

Run these queries in the Athena workgroup configured for the project. They assume the Glue Data Catalog database `db_youtube_cleaned`.

- `01_table_validation.sql` — row counts for the main and staging datasets. The query was executed successfully on 12 November 2026.
- `02_category_performance.sql` — category analysis using the staging dataset. It deduplicates the reference lookup, removes exact duplicate rows, excludes conflicting business keys and filters the literal `#NAME?` IDs. Executed successfully on 12 November 2026 (99 region/category result rows; query ID `2ee40cd5-aa84-4d28-8b9d-57c613765327`).
- `03_duplicate_audit.sql` — measures exact and conflicting duplicate business keys. Executed successfully on 12 November 2026.
- `04_staging_quality.sql` — reports row quality metrics and region distribution. The corresponding quality checks were executed successfully on 12 November 2026.

Do not describe an unexecuted query as tested. Record the execution date, workgroup, query execution ID, and result summary when validating additional SQL.
