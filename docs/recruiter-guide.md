# Project notes for interviews

## Short description

I built a batch pipeline around the public Kaggle YouTube Trending Videos dataset. It uses S3, Glue and PySpark to process regional CSV files, checks data quality, stores accepted and rejected records separately, and makes the accepted data available for Athena queries. I also made a small HTML dashboard from the query results.

## CV entry

**YouTube Trending Data Pipeline**  
*AWS S3, AWS Glue, PySpark, Glue Data Catalog, Athena, SQL, Python*

- Processed YouTube trending-video CSV data from 10 regions with AWS Glue and PySpark, writing the transformed data to Parquet in S3.
- Added checks for invalid video IDs, exact duplicates and conflicting business keys; separated rejected records into a quarantine dataset.
- Queried the curated data with Athena and built an HTML dashboard showing regional and category metrics.

The latest validated run produced 359,936 accepted rows, with zero duplicate business-key groups in the accepted output.

## How to explain it

Use this as a reminder of the order of the work, not as a script to memorise:

1. The source was the public Kaggle YouTube Trending Videos dataset, split into regional CSV files.
2. I stored the files in S3 and used Glue/PySpark to read them with a defined schema and write Parquet.
3. I checked the data before using it for analysis. The source included literal `#NAME?` values in `video_id`, exact duplicate rows and cases where the same business key had different record values.
4. I used `(region, video_id, trending_date)` as the business key. Exact duplicates were removed. Where records with the same key disagreed, I kept them in quarantine instead of picking a winner.
5. The accepted and quarantine datasets were registered in the Glue Data Catalog. I used Athena SQL for the analysis and built a dashboard from the query output.

Be ready to explain what each stage does and why you made those data-quality decisions. It is better to describe one part clearly than to recite a polished answer.

## Results to know

| Measure | Result |
|---|---:|
| Rows read into staging | 375,942 |
| Regions | 10 |
| Accepted rows | 359,936 |
| Unique video IDs in accepted data | 184,180 |
| Invalid-ID rows quarantined | 2,312 |
| Conflicting rows quarantined | 1,298 |
| Conflicting business-key groups | 649 |
| Duplicate business-key groups in accepted data | 0 |

## Questions you may be asked

**Why did you use Parquet?**  
It is a columnar format that supports compression and lets analytical queries read only the columns they need.

**What is the business key?**  
`(region, video_id, trending_date)`. A video can trend in more than one region or on more than one date, so the region and date are part of the key.

**Why quarantine conflicting records?**  
If two rows have the same key but disagree on other fields, choosing one without a rule could hide a data issue. Quarantine keeps the records available for investigation.

**What did you find in the source data?**  
There were 2,312 literal `#NAME?` values in the video ID field and 649 business-key groups with conflicting variants. The curation output retained 1,298 rows from those conflicting groups in quarantine.

**How did you check the result?**  
I queried the outputs in Athena. The latest run had 359,936 accepted rows across 10 regions and no duplicate business-key groups in the accepted data.

**Is the pipeline live?**  
No. It is a tested batch pipeline using a historical dataset. The AWS workflow completed successful executions, but automatic triggers and scheduled dashboard refreshes are paused to control costs. The dashboard is a static snapshot.

**What would you improve?**  
I would improve text encoding, add automated tests with sample input files, and make the refresh process easier to run and verify without leaving AWS services running unnecessarily.

## Be accurate about the scope

- The dataset is from Kaggle; it is not a live YouTube API feed.
- The dashboard uses a committed JSON snapshot and does not query AWS in the browser.
- The top-video table is limited to the records included in the snapshot. It is not a full ranking for every region.
- Amazon QuickSight is not used in this project.
- The project was informed by a public AWS tutorial. Be clear about which parts were adapted and which data-quality, orchestration, SQL and dashboard work you implemented.

## Links

- [Repository](https://github.com/krishnasai-gorantla/youtube-trending-data-pipeline)
- [Live dashboard](https://krishnasai-gorantla.github.io/youtube-trending-data-pipeline/)
- [Pipeline run and AWS evidence](verified-aws-state.md)
- [SQL queries](../sql/)
