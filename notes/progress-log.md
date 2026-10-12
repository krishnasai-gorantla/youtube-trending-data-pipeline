# Project Progress Log

Use one dated entry for each meaningful work session. Keep notes specific to what was actually tested.

## Entry template

### YYYY-MM-DD — Short task name

- **Goal:**
- **What I did:**
- **Expected result:**
- **Actual result:**
- **Error or issue:**
- **Root cause:** (only after confirmed)
- **Fix and verification:**
- **What I learned:**
- **Next step:**

## Known starting point

- Regional CSV files were uploaded to an S3 raw zone.
- An AWS Glue crawler was created and run.
- The observed crawler status was `SUCCEEDED`.
- The expected table was not visible in the Data Catalog at the time of troubleshooting.
- An S3 `GetObject` access-denied error was observed. The exact root cause and successful fix still need to be confirmed.

Add new entries as you continue the tutorial. Avoid recording secrets, account IDs, or other sensitive details.
