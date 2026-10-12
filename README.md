# YouTube Trending Data Pipeline

A hands-on data engineering learning project exploring how to ingest, organise, catalogue, query, and analyse YouTube Trending Videos data using AWS and SQL.

> **Status:** In progress. This repository documents my own implementation and learning notes while I build the pipeline. Components and results will be updated as they are verified.

## Project goals

- Organise regional CSV source data in Amazon S3.
- Explore data cataloguing with AWS Glue.
- Practise data transformation and storage formats such as Parquet.
- Query data with Amazon Athena and SQL.
- Document data-quality checks, errors, fixes, and lessons learned.
- Build a reproducible, portfolio-ready project rather than just following a tutorial.

## Technology stack

- **Amazon S3** — raw data storage
- **AWS Glue** — crawler and Data Catalog exploration; transformation work planned/in progress
- **Amazon Athena / SQL** — querying the data (planned until verified end-to-end)
- **Python** — scripting and automation as the project develops
- **GitHub** — version control and technical documentation

## Data

The source dataset contains regional YouTube Trending Videos CSV files. The working S3 layout uses a region-partitioned structure similar to:

```text
youtube/
└── raw_statistics/
    ├── region=CA/
    ├── region=DE/
    ├── region=FR/
    ├── region=GB/
    ├── region=IN/
    ├── region=JP/
    ├── region=KR/
    ├── region=MX/
    ├── region=RU/
    └── region=US/
```

The raw CSV data is not committed to this repository. This keeps the repository focused on code and documentation and avoids unnecessarily committing large data files.

## Architecture

Current learning workflow:

1. Obtain regional CSV files.
2. Store raw files in Amazon S3.
3. Run an AWS Glue crawler to discover the data schema.
4. Resolve catalog and permissions issues.
5. Add transformation and query steps as they are implemented and tested.
6. Record validation results and lessons learned.

The diagram below is a high-level target workflow, not a claim that every stage is complete:

```text
Regional CSV files
       |
       v
Amazon S3 (raw zone)
       |
       v
AWS Glue crawler / Data Catalog
       |
       v
Transformation layer (planned)
       |
       v
Amazon Athena + SQL (planned)
       |
       v
Analysis / reporting (planned)
```

## Current progress

- [x] Created an S3 bucket and uploaded regional CSV files.
- [x] Created an AWS Glue IAM role and crawler.
- [x] Ran the crawler; the latest observed crawler status was `SUCCEEDED`.
- [ ] Confirm that the expected table appears in the Glue Data Catalog.
- [ ] Resolve the observed S3 `GetObject` permission issue affecting Glue.
- [ ] Implement and validate transformations.
- [ ] Run documented Athena queries and data-quality checks.
- [ ] Add reproducible code and screenshots/diagrams where appropriate.

I will only mark a step complete once I have verified it in my own environment.

## Repository structure

```text
.
├── docs/          # Architecture and setup notes
├── notes/         # Progress log, errors, and lessons learned
├── sql/           # Athena / SQL queries
├── src/           # Python scripts and transformation code
├── .gitignore
└── README.md
```

## Security and data handling

- Never commit AWS access keys, secret keys, passwords, session tokens, or `.env` files.
- Do not commit private account details, personal data, or sensitive logs.
- Keep large raw datasets outside Git unless there is a clear, safe reason to include a small sample.
- Use IAM roles and least-privilege permissions where possible.
- Redact account IDs, resource details, and credentials from screenshots and logs before publishing.

## Learning log

For each meaningful step, I aim to record:

- What I was trying to do
- What I expected to happen
- What actually happened
- The error or data-quality issue
- The root cause and fix (once confirmed)
- What I learned and how I verified the result

## Acknowledgements

This is a personal learning project based on a guided data engineering tutorial and my own practice. I will credit the original tutorial and dataset source here once I add their exact titles and links.

---
*Work in progress — documentation will evolve as the implementation is tested.*
