# Recruiter and interview guide

## Project in one line

Built and tested an AWS batch data pipeline for YouTube Trending Videos data across 10 regions, with PySpark transformations, data-quality quarantine, Athena analytics and an interactive dashboard snapshot.

## Resume entry

**YouTube Trending Videos — End-to-End Data Engineering Pipeline**  
*AWS S3, AWS Glue, PySpark, Glue Data Catalog, Athena, SQL, Python, GitHub Actions*

- Built and tested an AWS batch pipeline to process YouTube trending-video data across 10 regions, transforming raw CSVs into analytics-ready Parquet with S3, Glue and PySpark.
- Implemented data-quality controls for invalid IDs, exact duplicates and conflicting business keys, separating accepted records from quarantined records; validated 359,936 safe records with zero duplicate business-key groups.
- Developed Athena SQL analysis for regional KPIs, category performance and top videos, and built an interactive HTML dashboard backed by a documented data snapshot.

**Accuracy note:** The pipeline's orchestration was successfully tested, but automatic AWS triggers and scheduled refreshes are currently paused to control cloud usage. Describe this as a tested pipeline, not a continuously running production service.

## 60-second explanation

“I built an end-to-end batch data engineering project using the Kaggle YouTube Trending dataset. The raw regional CSV files are stored in Amazon S3. I used AWS Glue and PySpark to apply a defined schema and convert the data into Parquet. A curation stage then checks data quality: it rejects invalid video IDs, removes exact duplicate rows, and quarantines records where the same region, video ID and trending date have conflicting values. The accepted and rejected datasets are stored separately and registered in the Glue Data Catalog. I used Athena SQL to analyse regional performance, category performance and top videos, then presented the results in an interactive dashboard. The key learning was that data quality is not just removing nulls; choosing a business key and preserving conflicting records for audit are equally important. I tested the end-to-end orchestration and paused automatic triggers afterwards to avoid unnecessary AWS costs.”

## Architecture walkthrough

1. **Raw layer — S3:** source CSV files are organised by region.
2. **Staging — Glue/PySpark:** reads CSVs with an explicit schema and writes Snappy Parquet into run-specific partitions.
3. **Catalog — Glue Data Catalog:** crawlers register the staging and curated partitions so Athena can query them.
4. **Curation — Glue/PySpark:** validates IDs, removes exact duplicates and quarantines conflicting business-key records.
5. **Analytics — Athena SQL:** computes regional KPIs, category performance and top-video summaries.
6. **Presentation — HTML/JSON:** the dashboard renders a committed snapshot; it does not query AWS in the browser.

## Useful technical questions

**Why Parquet instead of CSV?**  
Parquet is columnar and compressed, so analytical queries can read only required columns and generally scan less data.

**Why use both a safe and quarantine dataset?**  
It keeps bad or ambiguous records visible for investigation instead of silently deleting them, while protecting downstream analysis.

**What is the business key?**  
`(region, video_id, trending_date)`. Two records can share that key but differ in other fields; those conflicts are not safe to resolve by arbitrarily keeping one.

**What was the main data-quality issue?**  
The source included 2,312 literal `#NAME?` values in `video_id`, plus conflicting variants for 649 business-key groups. The latest quarantine snapshot recorded 1,298 conflicting rows.

**How did you validate the result?**  
I used Athena checks to confirm 359,936 safe rows across 10 regions, zero invalid IDs and zero duplicate business-key groups in the safe output.

**Why Step Functions?**  
It coordinates the Glue jobs and crawler stages in a defined order, passing a unique run ID so outputs are isolated and earlier runs are preserved.

**Is it live or continuously running?**  
No. It is a tested batch pipeline using a historical Kaggle dataset. Automatic triggers and scheduled dashboard refreshes are intentionally paused to control cloud costs. The dashboard is a static snapshot.

**What would you improve next?**  
Add CI tests against representative input fixtures, stronger text-encoding normalisation, a controlled manual refresh procedure and alerting for failed runs. Any production schedule would need a clear cost budget and monitoring.

## Evidence links

- [GitHub repository](https://github.com/krishnasai-gorantla/youtube-trending-data-pipeline)
- [Dashboard HTML source](dashboard/index.html)
- [Dashboard JSON snapshot](dashboard/data.json)
- [AWS verification record](verified-aws-state.md)
- [End-to-end orchestration runbook](end-to-end-orchestration.md)
- [Athena SQL scripts](../sql/)

## Be transparent

This is a portfolio project based on a public dataset and informed by a public tutorial. The additional work documented here includes stricter data validation, business-key conflict handling, quarantine outputs, run-isolated orchestration, Athena analytics and the dashboard. Do not present the dashboard as live YouTube data or the AWS workflow as an always-on production service.
