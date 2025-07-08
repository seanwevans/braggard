# Braggard Technical Specification

## 1. Terminology

| Term | Meaning |
|------|---------|
| **Collector** | CLI that queries the GitHub GraphQL v4 API and stores raw snapshots in `data/` |
| **Analyzer** | Transforms raw JSON into tidy dataframes and a canonical `summary.json` |
| **Renderer** | Converts `summary.json` into a static site inside `docs/` |
| **Deployer** | Pushes `docs/` to the `gh-pages` branch (or a `/docs` folder for project sites) |

## 2. Module responsibilities

### 2.1 Collector

* **Input** – GitHub username, optional token, CLI flags
* **Output** – timestamped raw JSON dump per run
* Requests send `User-Agent: braggard/<version>`
* **Data points fetched**  
  * repo name, description, homepage, primaryLanguage  
  * stars, forks, watchers  
  * last push date, default branch SHA  
  * language breakdown (via `repositoryLanguages`)  
  * weekly commit counts (via `history(first: 0)` & `committedDate` bucketing)  
  * CI success status (last N workflows)  
  * traffic stats (`views`, `clones`) *if authorized*  

### 2.2 Analyzer

1. Load dump(s) → pandas DataFrame.
2. Derive metrics:

   | Metric | Formula / Note |
   |--------|---------------|
   | **Total LOC** | `Σ language.sizerInBytes` converted via [linguist‑langs.json] |
   | **Commit velocity** | commits / week (rolling 52‑week window) |
   | **Bus factor** | fraction of commits authored by top N contributors |
   | **CI pass‑rate** | successful runs / total runs (max N=100) |
   | **PR impact** | merged external PRs / total external PRs |
   | **Issue responsiveness** | median time‑to‑first‑response |

3. Dump tidy CSV & a single `summary.json`.

### 2.3 Renderer

* Jinja2 templates render cards & charts.
* Chart.js used for interactive plots; data inlined as `<script type="application/json">`.
* Tailwind CSS for styling (self‑hosted; purgeCSS to reduce bloat).
* Generates `/index.html` plus `/assets/`.
* Social preview OG image produced via Pillow (`scripts/og.py`).

### 2.4 Deployer

* Shell script `deploy.sh` executed by workflow:
  ```bash
  git fetch
  git switch gh-pages || git switch -c gh-pages
  rsync -a --delete docs/ .
  git add .
  git commit -m "braggard: $(date +%F)"
  git push origin gh-pages
  ```
* Idempotent; safe to re‑run.

## 3. CLI commands

| Command | Description |
|---------|-------------|
| `braggard collect <user>` | Fetch data & store raw JSON |
| `braggard analyze` | Produce tidy CSV + summary.json |
| `braggard render` | Build static site into `docs/` |
| `braggard deploy` | Push `docs/` → `gh-pages` |

All commands accept `--token`, `--include-private`, and `--since YYYY-MM-DD`.

## 4. Configuration

* **braggard.toml**

  ```toml
  [user]
  handle = "seanwevans"
  include_private = true

  [metrics]
  ci_pass_window = 100      # last 100 runs
  commit_history_years = 3
  ```

## 5. Data model (`summary.json` v1)

```json
{
  "generated_at": "2025-07-07T20:32:10Z",
  "repos": [
    {
      "name": "moqtail",
      "stars": 42,
      "forks": 3,
      "loc_by_language": {"Rust": 12450, "Python": 2110},
      "last_push": "2025-07-06T18:22:00Z",
      "commit_velocity": 3.5,
      "ci_pass_rate": 0.92
    }
  ],
  "aggregate": {
    "total_loc": 238200,
    "languages": {"Rust": 0.63, "Python": 0.21, "C": 0.06, "Other": 0.10},
    "commits_per_week": 5.6,
    "pr_impact": 0.71
  }
}
```

## 6. External dependencies

| Tool | Why |
|------|-----|
| **GitHub GraphQL v4 API** | Primary data source |
| **pandas / numpy** | ETL and stats |
| **jinja2** | Templating |
| **chart.js** | Client‑side charts |
| **tailwindcss** | Styling |
| **gh‑linguist** | Precise LOC fallback |

## 7. Non‑goals (v1)

* Real‑time dashboards — Braggard is deliberately snapshot‑based.
* In‑browser OAuth flow — PAT is explicit.
* Dynamic server — output is static to keep hosting trivial.

---
_Spec version: 2025‑07‑07 (v0.1)_
