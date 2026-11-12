# BI dashboard data model

The curated Athena table is the source of truth for analysis:

- Fact table: `db_youtube_cleaned.youtube_portfolio_v2`
- Quarantine table: `db_youtube_cleaned.youtube_portfolio_v2_quarantine`
- Category lookup: `db_youtube_cleaned.statistics_reference_data`

## Validated dashboard queries

| File | Grain | Suggested visual |
|---|---|---|
| `sql/06_region_dashboard_kpis.sql` | One row per region | KPI cards, regional bar chart |
| `sql/07_category_dashboard_performance.sql` | One row per region/category | Category ranking, stacked bars |
| `sql/08_top_videos.sql` | One row per region/video | Top-video table |

All three queries were executed successfully in Athena against the curated table on 12 November 2026.

## Metric definitions

- `trending_observations`: number of video-region-day rows in the dataset.
- `unique_videos`: distinct video IDs within the selected region/category.
- `cumulative_observed_views`: sum of views across daily trending observations. The same video may appear on multiple days, so this is not a unique lifetime-view total.
- `peak_views`: maximum observed views for a video in a region.
- `engagement_rate_pct`: (likes + comments) / views × 100. Dislikes are not included.
- Category names are joined from `snippet_title` after reducing the reference table to one row per ID. Do not join its 311 regional copies directly.

## Current BI deployment limitation

The AWS account is not currently subscribed to Amazon QuickSight. The QuickSight dashboard and analysis APIs returned `UnsupportedUserEditionException`, and the dataset listing returned no datasets. Therefore, this repository contains tested Athena datasets/queries, not a deployed QuickSight dashboard.

Do not enable a QuickSight subscription or incur additional BI-service charges without the account owner's explicit decision. These SQL outputs can also be consumed by Power BI or another BI tool.

## Known data presentation caveat

The original CSV files required ISO-8859-1 decoding to ingest the full dataset. A sample top-video title currently displays `GarcÃ­a` rather than `García`, indicating mojibake in at least some text values. Numeric metrics and row-quality checks passed, but text encoding should be corrected in a separately tested transformation before presenting titles as polished dashboard labels.
