# Dashboard

The dashboard is a small interactive HTML page backed by `data.json`.

## View locally

1. Download the repository or open `docs/dashboard/index.html` from a local checkout.
2. Open `index.html` in a browser. It contains a verified fallback snapshot if the browser blocks local `file://` requests for `data.json`.
3. To preview the latest JSON file as the page would load it when hosted, run a local static server from the repository root:

   ```bash
   python -m http.server 8000
   ```

   Then open `http://localhost:8000/docs/dashboard/`.

## Automatic data refresh

- GitHub Actions workflow: `.github/workflows/refresh-dashboard-data.yml`
- Schedule: hourly at minute 17 UTC, plus manual dispatch.
- Authentication: GitHub Actions OIDC; no long-lived AWS access key is stored in GitHub.
- Source of truth: latest successful execution of the AWS Step Functions state machine, then Athena queries against the run-partitioned safe and quarantine tables.
- Output: `docs/dashboard/data.json`. The workflow commits only when the data changes.
- Publishing: a separate GitHub Pages workflow deploys `docs/dashboard/` after dashboard files change.

The dashboard refresh role is restricted to this repository's `main` branch and read-only access to pipeline execution metadata, curated tables and Athena query results. It cannot start Glue jobs or modify source data.

## Hosting

GitHub Pages must be enabled once in repository settings: **Settings → Pages → Build and deployment → Source: GitHub Actions**. The deployment workflow is already in the repository. Once Pages is enabled, run **Actions → Publish dashboard → Run workflow** for the first deployment. Subsequent new pipeline runs refresh the JSON and trigger deployment automatically.

Amazon QuickSight is intentionally not enabled; the account is not subscribed and no subscription charge was authorised.
