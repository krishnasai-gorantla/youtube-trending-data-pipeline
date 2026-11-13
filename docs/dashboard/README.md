# Dashboard

The dashboard is a lightweight interactive HTML page backed by the committed `data.json` snapshot.

## View locally

From the repository root:

```bash
python -m http.server 8000
```

Open `http://localhost:8000/docs/dashboard/`. The page also contains a fallback snapshot if local browser security blocks the JSON request.

## Data freshness

- Snapshot file: `docs/dashboard/data.json`
- Latest snapshot timestamp: 2026-11-13 13:06:47 UTC
- Source: latest verified successful AWS pipeline execution at the time the snapshot was generated.
- This is a historical dataset snapshot, not a live feed.

The scheduled Athena refresh workflow has been removed from active GitHub Actions workflows to avoid recurring AWS usage. Its prior workflow file is retained as a disabled archive under `docs/disabled-workflows/`. Do not restore or schedule it unless you explicitly decide to incur the associated Athena and GitHub Actions usage.

## Publish with GitHub Pages

The repository contains `.github/workflows/publish-dashboard.yml`. GitHub Pages must first be enabled by a repository administrator:

1. Open **Repository → Settings → Pages**.
2. Under **Build and deployment**, choose **GitHub Actions** as the source.
3. Open **Actions → Publish dashboard** and run the workflow manually.
4. After the workflow succeeds, use the page URL reported by the deployment job. Do not use a guessed URL before deployment is confirmed.

The linked GitHub account has repository admin permission, but this workflow does not enable Pages settings itself.

## AWS cost notes

The dashboard is static and can be viewed without running AWS services. Amazon QuickSight is not used and no QuickSight subscription has been created. The data refresh is intentionally manual/offline at present.
