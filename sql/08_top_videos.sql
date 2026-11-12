-- Top videos by peak observed views within each region.
-- max_by keeps one representative title/channel/category from the
-- observation with the highest views for each region + video_id.
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
FROM db_youtube_cleaned.youtube_portfolio_v2
GROUP BY region, video_id
ORDER BY peak_views DESC
LIMIT 100;
