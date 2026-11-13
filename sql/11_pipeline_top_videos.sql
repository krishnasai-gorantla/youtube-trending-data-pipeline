-- Top videos by peak observed views for one automated execution.
-- Replace <RUN_ID> with the run_id reported by Step Functions.
SELECT
    region,
    video_id,
    max_by(title, views) AS title,
    max_by(channel_title, views) AS channel_title,
    max_by(category_id, views) AS category_id,
    MAX(views) AS peak_views,
    MAX(likes) AS peak_likes,
    MAX(comment_count) AS peak_comments,
    COUNT(*) AS trending_observations
FROM db_youtube_cleaned.youtube_pipeline_safe
WHERE run_id = '<RUN_ID>'
GROUP BY region, video_id
ORDER BY peak_views DESC
LIMIT 100;
