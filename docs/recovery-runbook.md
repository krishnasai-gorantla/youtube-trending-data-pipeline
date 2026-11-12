# Recovery Runbook

## Guardrails

- Keep the existing raw and cleansed S3 objects.
- Keep the four captured Glue scripts unchanged until the replacement is validated.
- Do not rerun the append-mode `spark` job against the current `youtube/` prefix.
- Do not widen IAM policies broadly. Fix only the exact required S3 prefix permission after reviewing the role policy.
- Test new output in a separate versioned prefix.

## Recovery sequence

### Phase 1 — Establish a baseline

- Re-run Athena row counts and capture the execution ID.
- Inspect the Glue job's current script location, arguments, role and latest run.
- Confirm the catalog table locations and schemas.
- Save a small set of representative source and output records for comparison (redact sensitive information).

### Phase 2 — Fix ingestion and parsing

- Determine the encoding and CSV dialect for all regional files, not only the two failing files.
- Test multiline/quote/escape behaviour and malformed-record handling.
- Preserve malformed records in a quarantine location with source file and error reason.
- Compare parsed row counts with source counts.

### Phase 3 — Separate transformation outputs

- Assign one owner/job per S3 output prefix.
- Avoid writing both the direct CSV job and catalog-based job into `youtube/`.
- Add deterministic rerun behaviour and deduplication keys.
- Keep the existing data unchanged until a full comparison passes.

### Phase 4 — Data quality and catalog

- Validate required columns and types.
- Check null keys, duplicate keys, valid region codes, timestamp parsing and non-negative metrics.
- Confirm the Glue Catalog location/schema/partition metadata matches the new output.
- Run Athena checks for counts, duplicates, nulls and category joins.

### Phase 5 — Analytics and presentation

- Build category and region aggregates only from validated data.
- Add tested SQL and a dashboard only when the corresponding output exists.
- Document the exact job sequence, configuration, costs and limitations.

## Completion criteria

The project is ready to present as end-to-end only when a clean run can be repeated from documented inputs, each stage has successful execution evidence, quality checks pass, Athena queries return expected results, and the dashboard (if claimed) is demonstrably connected to the curated data.
