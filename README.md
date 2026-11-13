# YouTube Trending Data Pipeline

This is a batch data-engineering project using the public Kaggle YouTube Trending Videos dataset. I used AWS S3, Glue and PySpark to process the regional CSV files, apply data-quality rules and write Parquet outputs. I then queried the curated data with Athena and built a small HTML dashboard from the query results.

## Current status

The latest successful pipeline run is dated 13 November 2026. It processed 375,942 staging rows from 10 regions and produced 359,936 accepted rows. Invalid video IDs and conflicting business-key records were kept in a separate quarantine output.

The pipeline has been run and validated, but it is not running continuously. Automatic AWS triggers and scheduled dashboard refreshes are paused to avoid ongoing charges. The dashboard uses a committed data snapshot; it is not connected to YouTube or AWS live queries.

## What I worked on

- Stored the regional source CSV files in Amazon S3.
- Used AWS Glue and PySpark to apply a schema and write Snappy Parquet.
- Defined the business key as `(region, video_id, trending_date)`.
- Removed exact duplicate rows and quarantined invalid video IDs and conflicting records instead of choosing an arbitrary version.
- Registered the staging, safe and quarantine outputs in the Glue Data Catalog.
- Used Athena SQL for regional, category and top-video analysis.
- Built an HTML dashboard that reads a JSON snapshot of the query results.

## Architecture

```text
Kaggle CSV files
      |
      v
Amazon S3 (raw)
      |
      v
AWS Glue / PySpark
      |
      v
Staging Parquet
      |
      v
Data-quality curation
    /       \
   v         v
Safe data  Quarantine
    \       /
     v     v
Glue Data Catalog
      |
      v
Amazon Athena
      |
      v
HTML dashboard (static snapshot)
```

AWS Step Functions coordinates the staging, curation and crawler steps. The workflow completed successful test executions. Its automatic trigger is currently disabled; a future run must be started deliberately.

## Latest validated data

| Check | Result |
|---|---:|
| Staging rows | 375,942 |
| Regions | 10 |
| Accepted rows | 359,936 |
| Unique video IDs in accepted data | 184,180 |
| Invalid-ID rows quarantined | 2,312 |
| Conflicting rows quarantined | 1,298 |
| Duplicate business-key groups in accepted data | 0 |

The 1,298 conflicting rows came from 649 business-key groups. If records shared a business key but differed in other fields, I quarantined all variants rather than deciding which one was correct.

These counts describe the dataset snapshot, not live YouTube activity.

## Tools

Amazon S3, AWS Glue, PySpark, Glue Data Catalog, Amazon Athena, AWS Step Functions, Python, SQL, GitHub Actions, HTML, CSS and JavaScript.

## Project files

- [Live dashboard](https://krishnasai-gorantla.github.io/youtube-trending-data-pipeline/)
- [Dashboard source and data](docs/dashboard/)
- [Athena SQL queries](sql/)
- [Pipeline architecture](docs/end-to-end-orchestration.md)
- [AWS verification notes](docs/verified-aws-state.md)
- [Interview notes](docs/recruiter-guide.md)

## View the dashboard locally

From the repository root, run:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/docs/dashboard/`.

## Limitations and next steps

- The source is a historical Kaggle dataset, not a live YouTube feed.
- The dashboard contains a limited top-video snapshot; it is not a complete ranking for every region.
- Some source text has encoding artefacts that still need cleaning.
- AWS automatic triggers and scheduled refreshes are paused.
- A useful next improvement would be to add more automated tests using representative input files and to improve text-encoding handling.

## Dataset and project background

The source data is the public Kaggle YouTube Trending Videos dataset. I used a public AWS data-engineering tutorial as a starting point, then added the data-quality curation, quarantine handling, run-isolated orchestration, Athena queries and dashboard documented in this repository.
