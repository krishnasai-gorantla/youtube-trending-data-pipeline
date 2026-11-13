# YouTube Trending Data Engineering Pipeline

An AWS batch data-engineering portfolio project built around the Kaggle YouTube Trending Videos dataset. It demonstrates ingestion, schema-aware transformation, data-quality controls, quarantine handling, catalog registration, SQL analytics and a lightweight interactive dashboard.

> **Portfolio status (13 November 2026):** The end-to-end AWS pipeline has completed successful test executions and its latest verified snapshot contains **359,936 safe records across 10 regions**. Automatic AWS triggers and scheduled dashboard refreshes are intentionally paused to avoid ongoing cloud usage. Source data, S3 outputs, Glue jobs, Step Functions definition, SQL and the static dashboard snapshot are preserved.

## What this project demonstrates

- Ingesting regional CSV data from Amazon S3.
- Transforming raw data to Snappy Parquet with AWS Glue and PySpark.
- Applying explicit validation, exact-row deduplication and business-key conflict detection.
- Separating accepted records from rejected records in safe and quarantine outputs.
- Registering partitions and tables in the AWS Glue Data Catalog.
- Querying curated data with Amazon Athena.
- Building regional, category and top-video analytics and a static interactive HTML dashboard.
- Designing a run-isolated Step Functions orchestration flow and documenting cloud cost controls.

## Architecture

```text
Kaggle regional CSV files
          |
          v
    Amazon S3 (raw)
          |
          v
AWS Glue + PySpark staging
          |
          v
  Staging Parquet / Catalog
          |
          v
   Data-quality curation
       /          \
      v            v
 Safe Parquet   Quarantine Parquet
      \            /
       v          v
      Glue Data Catalog
              |
              v
        Amazon Athena
              |
       SQL analytics
              |
              v
   Interactive HTML dashboard
   (static, versioned snapshot)
```

The implemented Step Functions workflow coordinates staging, catalog registration, curation and separate safe/quarantine catalog registration. It has completed successful test executions. The EventBridge batch-ready rule is currently **DISABLED** and the raw bucket EventBridge notification configuration is empty, so uploading a marker will not start a new run unless the trigger is deliberately reconfigured. This is intentional for cost control.

## Verified data-quality snapshot

Latest published dashboard snapshot: `docs/dashboard/data.json`.

| Metric | Verified result |
|---|---:|
| Staging records | 375,942 |
| Regions | 10 |
| Safe curated records | 359,936 |
| Unique video IDs in safe set | 184,180 |
| Invalid IDs retained in quarantine | 2,312 |
| Conflicting rows retained in quarantine | 1,298 |
| Duplicate business-key groups in safe output | 0 |

The business key is `(region, video_id, trending_date)`. Exact duplicate rows are removed. If multiple non-identical records share a business key, all conflicting variants are quarantined rather than selecting one arbitrarily. The reference category lookup must be deduplicated by category ID before joining because the source contains repeated regional copies.

These figures describe the historical dataset snapshot, not live YouTube activity.

## Technology

Amazon S3 · AWS Glue · PySpark · Glue Data Catalog · Amazon Athena · AWS Step Functions · EventBridge · Python · SQL · GitHub Actions · HTML/CSS/JavaScript

Amazon QuickSight is not part of this implementation; no QuickSight subscription was created. The dashboard is a static HTML application backed by a committed JSON snapshot.

## Explore the project

- [Interactive dashboard source](docs/dashboard/index.html) — open locally or use GitHub Pages after enabling it.
- [Dashboard data snapshot](docs/dashboard/data.json)
- [End-to-end architecture and runbook](docs/end-to-end-orchestration.md)
- [Verified AWS state and execution evidence](docs/verified-aws-state.md)
- [Recruiter and interview guide](docs/recruiter-guide.md)
- [Dashboard hosting instructions](docs/dashboard/README.md)
- [Athena SQL](sql/)

## Run the dashboard locally

From the repository root:

```bash
python -m http.server 8000
```

Open `http://localhost:8000/docs/dashboard/`. The page includes a fallback snapshot for browsers that restrict local JSON loading.

## Cost-conscious operating status

No recurring dashboard refresh workflow is active. The former hourly workflow has been removed from `.github/workflows/` and retained as a disabled archive under `docs/disabled-workflows/`. The EventBridge trigger is disabled, the raw S3 EventBridge notification configuration is empty, and the JSON-reference Lambda has reserved concurrency set to zero. Do not start Glue jobs, Athena queries or Step Functions executions unless you intend to incur usage-based charges. AWS credits are not a hard spending cap.

## Known limitations

- The source is a historical Kaggle dataset; the dashboard is not live.
- Some source titles contain character-encoding artefacts; numeric metrics and quality checks were validated separately.
- The pipeline is preserved and tested, but automatic execution is paused.
- GitHub Pages is not yet confirmed as enabled. Follow the dashboard hosting instructions to publish a public rendered dashboard URL.

## Attribution

The project was developed as a learning portfolio using the public Kaggle YouTube Trending Videos dataset and was informed by a public AWS data-engineering tutorial. The repository documents the additional validation, quarantine, run-isolation, SQL analytics and dashboard work completed here.
