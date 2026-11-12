-- Run after registering the safe Parquet output as
-- db_youtube_cleaned.youtube_portfolio_v2.
SELECT
  COUNT(*) AS safe_rows,
  COUNT(DISTINCT region) AS regions,
  COUNT_IF(video_id IS NULL OR TRIM(video_id) = '' OR UPPER(TRIM(video_id)) = '#NAME?') AS invalid_video_ids
FROM db_youtube_cleaned.youtube_portfolio_v2;

-- Must return zero rows: the curated business key must be unique.
SELECT region, video_id, trending_date, COUNT(*) AS row_count
FROM db_youtube_cleaned.youtube_portfolio_v2
GROUP BY region, video_id, trending_date
HAVING COUNT(*) > 1;

-- Register quarantine output separately as
-- db_youtube_cleaned.youtube_portfolio_v2_quarantine.
SELECT issue_type, COUNT(*) AS rows
FROM db_youtube_cleaned.youtube_portfolio_v2_quarantine
GROUP BY issue_type
ORDER BY issue_type;
