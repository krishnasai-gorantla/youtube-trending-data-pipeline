-- Purpose: validate the row counts and region coverage of the main, staging and reference tables.
SELECT
    'youtube' AS dataset,
    COUNT(*) AS row_count,
    COUNT(DISTINCT region) AS region_count
FROM db_youtube_cleaned.youtube

UNION ALL

SELECT
    'tutorial_staging_youtube' AS dataset,
    COUNT(*) AS row_count,
    COUNT(DISTINCT region) AS region_count
FROM db_youtube_cleaned.tutorial_staging_youtube

UNION ALL

SELECT
    'statistics_reference_data' AS dataset,
    COUNT(*) AS row_count,
    CAST(NULL AS BIGINT) AS region_count
FROM db_youtube_cleaned.statistics_reference_data;
