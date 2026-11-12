-- Purpose: compare trending observations and recorded view totals by category.
-- Note: total_recorded_views sums views across trending observations, not unique lifetime views.
SELECT
    r.snippet_title AS category_name,
    COUNT(*) AS trending_observations,
    COUNT(DISTINCT y.video_id) AS distinct_videos,
    SUM(y.views) AS total_recorded_views,
    AVG(y.views) AS average_views_per_observation
FROM db_youtube_cleaned.youtube AS y
JOIN db_youtube_cleaned.statistics_reference_data AS r
    ON y.category_id = r.id
GROUP BY r.snippet_title
ORDER BY total_recorded_views DESC;
