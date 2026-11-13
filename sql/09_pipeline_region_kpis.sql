-- Regional KPIs for one automated pipeline execution.
-- Replace <RUN_ID> with the run_id reported by Step Functions.
SELECT
    region,
    COUNT(*) AS trending_observations,
    COUNT(DISTINCT video_id) AS unique_videos,
    SUM(views) AS cumulative_observed_views,
    ROUND(AVG(views), 0) AS avg_views_per_observation,
    ROUND(100.0 * (SUM(likes) + SUM(comment_count)) / NULLIF(SUM(views), 0), 4)
        AS engagement_rate_pct
FROM db_youtube_cleaned.youtube_pipeline_safe
WHERE run_id = '<RUN_ID>'
GROUP BY region
ORDER BY region;
