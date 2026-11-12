-- Purpose: quantify duplicate business keys, separating exact duplicates from conflicting records.
-- Business key: region + video_id + trending_date.
-- Invalid '#NAME?' IDs and blank IDs are excluded from this audit.
-- SELECT DISTINCT compares all source fields, avoiding ambiguous concatenated row signatures.
WITH valid_rows AS (
    SELECT *
    FROM db_youtube_cleaned.tutorial_staging_youtube
    WHERE video_id IS NOT NULL
      AND TRIM(video_id) <> ''
      AND video_id <> '#NAME?'
),
distinct_rows AS (
    SELECT DISTINCT
        region, video_id, trending_date, title, channel_title, category_id,
        publish_time, tags, views, likes, dislikes, comment_count,
        thumbnail_link, comments_disabled, ratings_disabled,
        video_error_or_removed, description
    FROM valid_rows
),
key_variants AS (
    SELECT region, video_id, trending_date, COUNT(*) AS variants
    FROM distinct_rows
    GROUP BY region, video_id, trending_date
),
source_key_counts AS (
    SELECT region, video_id, trending_date, COUNT(*) AS copies
    FROM valid_rows
    GROUP BY region, video_id, trending_date
)
SELECT
    (SELECT COUNT(*) FROM valid_rows) AS valid_source_rows,
    (SELECT COUNT(*) FROM distinct_rows) AS unique_full_rows,
    (SELECT COUNT(*) FROM source_key_counts) AS distinct_business_keys,
    (SELECT COUNT(*) FROM source_key_counts WHERE copies > 1) AS duplicate_key_groups,
    (SELECT SUM(copies - 1) FROM source_key_counts WHERE copies > 1) AS duplicate_extra_rows,
    (SELECT COUNT(*) FROM valid_rows) - (SELECT COUNT(*) FROM distinct_rows)
        AS exact_duplicate_extra_rows,
    (SELECT COUNT(*) FROM key_variants WHERE variants > 1) AS conflicting_key_groups,
    (SELECT SUM(variants - 1) FROM key_variants WHERE variants > 1)
        AS conflicting_variant_extras,
    (SELECT COUNT(*) FROM distinct_rows d
        LEFT JOIN key_variants k
          ON d.region = k.region
         AND d.video_id = k.video_id
         AND d.trending_date = k.trending_date
        WHERE k.variants = 1) AS safe_rows_after_excluding_conflicts;
