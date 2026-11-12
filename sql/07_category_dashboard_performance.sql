-- Regional category performance.
-- The reference table has repeated regional copies, so reduce it to one
-- row per category ID before joining to avoid multiplying fact rows.
WITH category_lookup AS (
    SELECT
        id,
        MAX(snippet_title) AS category_name
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
    ROUND(
        100.0 * (SUM(y.likes) + SUM(y.comment_count)) / NULLIF(SUM(y.views), 0),
        4
    ) AS engagement_rate_pct
FROM db_youtube_cleaned.youtube_portfolio_v2 AS y
LEFT JOIN category_lookup AS c
    ON y.category_id = c.id
GROUP BY
    y.region,
    y.category_id,
    COALESCE(c.category_name, 'Unknown')
ORDER BY
    y.region,
    cumulative_observed_views DESC;
