-- Top 10 videos by peak observed views for each region in one pipeline run.
-- Replace <RUN_ID> with the run_id reported by Step Functions.
-- Keep title, channel, views and likes from the same highest-view observation.
WITH video_observations AS (
    SELECT
        region,
        video_id,
        title,
        channel_title,
        views,
        likes,
        comment_count,
        trending_date,
        ROW_NUMBER() OVER (
            PARTITION BY region, video_id
            ORDER BY views DESC, trending_date DESC
        ) AS observation_rank
    FROM db_youtube_cleaned.youtube_pipeline_safe
    WHERE run_id = '<RUN_ID>'
),
video_peaks AS (
    SELECT
        region,
        video_id,
        title,
        channel_title,
        views AS peak_views,
        likes AS likes_at_peak_views,
        comment_count AS comments_at_peak_views,
        trending_date AS peak_observation_date
    FROM video_observations
    WHERE observation_rank = 1
),
regional_rankings AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY region
            ORDER BY peak_views DESC, video_id
        ) AS region_rank
    FROM video_peaks
)
SELECT
    region,
    video_id,
    title,
    channel_title,
    peak_views,
    likes_at_peak_views,
    comments_at_peak_views,
    peak_observation_date
FROM regional_rankings
WHERE region_rank <= 10
ORDER BY region, region_rank;
