# Braggard Architecture

```
+---------------------+       GitHub GraphQL v4 API
|  Collector (CLI)    |---->  batched queries (JSON)
+---------------------+
          |
          v
+---------------------+       pandas / numpy
|  Analyzer           |---->  tidy CSV + summary.json
+---------------------+
          |
          v
+---------------------+       Jinja2 + Chart.js
|  Renderer           |---->  docs/ (static site)
+---------------------+
          |
(GitHub Action)  deploy.sh
          |
          v
  gh-pages branch  --->  GitHub Pages
```

## 1. Data flow

1. **Collector** writes raw snapshots to `data/YYYY-MM-DDTHHMMSS.json`.
2. **Analyzer** loads those snapshots, creates derived metrics and a canonical
   `summary.json`.
3. **Renderer** hydrates Jinja templates with `summary.json` to build a
   static site in `docs/`.
4. **Deployer** rsyncs `docs/` into the `gh-pages` branch for hosting.

## 2. Runtime environments

| Component  | Runs in | Language | Packaged as |
|------------|---------|----------|-------------|
| Collector  | local CLI / Action | Python 3.12 (optionally Rust) | `braggard` console script |
| Analyzer   | same    | Python (pandas) | module |
| Renderer   | same    | Python + Jinja  | module |
| Deployer   | GitHub Action | Bash | script |

## 3. Extensibility points

* **Plugins** – `entry_points={"braggard.metrics": ...}` to add custom metrics.
* **Themes** – Swap Tailwind config & Jinja templates.
* **Storage back‑ends** – Future option to push to S3 or GCS instead of gh‑pages.

## 4. Sequence diagram (update run)

```text
GitHub Actions    Collector     Analyzer     Renderer     GitHub Pages
     |                |             |             |            |
     |  nightly cron   |             |             |            |
     |---------------> |             |             |            |
     | collect() JSON  |             |             |            |
     | ------------->  |             |             |            |
     |                | analyze() CSV/summary.json |            |
     |                |------------->|             |            |
     |                |             | render() docs/            |
     |                |             |------------->|            |
     | deploy.sh rsync gh-pages push |             |            |
     | -------------------------------------------------------> |
```

## 5. Scaling considerations

* The GitHub API rate‑limit is ~5k requests/hr with PAT – ample if we batch queries.
* Data is read‑only snapshot; no server‑side database required.
* Build time scales roughly linearly with number of repos; paging keeps memory bounded.

---
_Updated: 2025‑07‑07_
