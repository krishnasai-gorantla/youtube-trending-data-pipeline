# Pipeline Architecture Notes

## Purpose

Document the intended flow for the YouTube Trending Videos learning project. Update this page as each component is implemented and verified.

## Current high-level flow

```text
Regional source CSV files
        |
        v
Amazon S3 - raw zone
        |
        v
AWS Glue crawler
        |
        v
AWS Glue Data Catalog
        |
        v
Transformation layer (planned)
        |
        v
Amazon Athena / SQL (planned)
        |
        v
Analysis and reporting (planned)
```

## Storage layout

The S3 raw zone has been organised by region, using paths similar to `youtube/raw_statistics/region=GB/`.

## Current known issue

The crawler run was observed as `SUCCEEDED`, but the expected Data Catalog table was not visible. AWS error output indicated an S3 `GetObject` access denial for the Glue service. Investigate the crawler's IAM role, bucket/object permissions, and the exact S3 target path. Record the verified root cause and fix here after testing.

## Verification checklist

- [x] Regional CSV files uploaded to S3.
- [x] Glue crawler created and run.
- [ ] Expected table visible in the Glue Data Catalog.
- [ ] Schema and partition layout inspected.
- [ ] Transformation output written and validated.
- [ ] Athena queries executed successfully.
- [ ] Data quality checks documented.

## Security

Never place access keys, secret keys, session tokens, private account identifiers, or unredacted screenshots in this repository.
