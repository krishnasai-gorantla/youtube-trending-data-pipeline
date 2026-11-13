# Dashboard

The dashboard is a small HTML page that reads the committed `data.json` file. It does not connect to AWS or YouTube when someone opens it.

## Open it

- [Open the published dashboard](https://krishnasai-gorantla.github.io/youtube-trending-data-pipeline/)
- To run it locally, start a server from the repository root:

```bash
python -m http.server 8000
```

Then visit `http://localhost:8000/docs/dashboard/`.

## Data in the dashboard

- Snapshot: `data.json`
- Snapshot timestamp: 13 November 2026, 13:06:47 UTC
- Source: Athena query results from the latest verified successful pipeline run.
- The source dataset is historical Kaggle data, not live YouTube activity.

The regional summary contains all ten regions. The top-video table contains ten records per region (100 total), ranked by peak observed views. Likes are taken from the same observation as the peak views.

## Updating the dashboard

The dashboard data is currently a static snapshot. The scheduled AWS refresh is paused to avoid recurring Athena and other AWS usage. To update it, the pipeline and Athena queries need to be run deliberately, the JSON snapshot regenerated and checked, and the change committed.

GitHub Actions publishes changes to the dashboard through `.github/workflows/publish-dashboard.yml`. GitHub Pages is enabled and the latest publish workflow completed successfully.

## Cost

Viewing the published or local dashboard does not require an AWS job to run. Starting Glue jobs, Step Functions executions or Athena queries can incur usage-based charges.
