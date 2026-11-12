-- Purpose: validate that the two core cleaned tables are queryable and record current row counts.
SELECT 'youtube' AS dataset, COUNT(*) AS row_count
FROM db_youtube_cleaned.youtube
UNION ALL
SELECT 'statistics_reference_data' AS dataset, COUNT(*) AS row_count
FROM db_youtube_cleaned.statistics_reference_data;
