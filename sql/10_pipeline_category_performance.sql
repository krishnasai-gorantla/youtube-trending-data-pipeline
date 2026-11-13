-- Category performance for one automated pipeline execution.
-- Deduplicate regional copies of category metadata before joining.
-- Replace <RUN_ID> with the run_id reported by Step Functions.
WITH category_lookup AS (
    SELECT id, MAX(snippet_title) AS category_name
    FROM db_youtube_cleaned.statistics_reference_data
    GROUP BY id
)
SELECT
    y.region,
    y.category_id,
    COALESCE(c.category_name, 'Unknown') AS category_name,
    COUNT(*) AS trending_observations,
    COUNT(DISTINCT y.video_id) AS unique_videos,
    SUM(y.views) AS cumulative_observed_views,
    ROUND(100.0 * (SUM(y.likes) + SUM(y.comment_count)) / NULLIF(SUM(y.views), 0), 4)
        AS engagement_rate_pct
FROM db_youtube_cleaned.youtube_pipeline_safe AS y
LEFT JOIN category_lookup AS c ON y.category_id = c.id
WHERE y.run_id = '<RUN_ID>'
GROUP BY y.region, y.category_id, COALESCE(c.category_name, 'Unknown')
ORDER BY y.region, cumulative_observed_views DESC;
