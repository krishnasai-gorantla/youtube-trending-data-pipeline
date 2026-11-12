-- Regional KPI dataset for a BI dashboard.
-- Source: validated curated table only.
-- cumulative_observed_views sums daily trending observations; it is not
-- a unique lifetime-view total per video.
SELECT
    region,
    COUNT(*) AS trending_observations,
    COUNT(DISTINCT video_id) AS unique_videos,
    SUM(views) AS cumulative_observed_views,
    ROUND(AVG(views), 0) AS avg_views_per_observation,
    ROUND(
        100.0 * (SUM(likes) + SUM(comment_count)) / NULLIF(SUM(views), 0),
        4
    ) AS engagement_rate_pct
FROM db_youtube_cleaned.youtube_portfolio_v2
GROUP BY region
ORDER BY region;
