# Braggard

**Braggard** is an automated portfolio‑stats generator for GitHub developers.  
It scans your repositories, extracts rich metrics, and publishes a shareable GitHub Pages site so you can showcase your coding prowess.

---

## ✨ Features

| Category | What you get |
|----------|--------------|
| **One‑command data grab** | `braggard collect <user>` hits the GitHub GraphQL API and stores raw JSON for reproducibility |
| **Deep analytics** | Lines‑of‑code per language, commit velocity, issue/PR impact, CI pass‑rate, test coverage, traffic analytics |
| **Beautiful dashboards** | Responsive static site built with Jinja + Chart.js + Tailwind, dark‑mode ready |
| **Automated deployment** | GitHub Action pushes updates to `gh-pages` nightly or on‑push |
| **Private‑repo friendly** | Supply a fine‑grained PAT and Braggard can include your private work in aggregate stats |
| **GitHub‑friendly requests** | Adds `User-Agent: braggard/<version>` to API calls |
| **Social preview image** | Optional OG image generator so links look great on social media |

---

## 🚀 Quick start

```bash
# Install
pip install braggard

# Set a GitHub token (needs repo‑read + actions‑read)
export BRAGGARD_TOKEN=<your_pat>

# Run locally
braggard collect  <your‑github‑user>
braggard analyze
braggard render
braggard deploy   # → pushes docs/ to gh-pages
```

The `braggard render` command accepts `--summary-path` to load a summary JSON
from a custom location instead of the default `summary.json`. Use `--format`
to choose between HTML (default), Markdown, or plain text output.

Or simply enable the supplied **GitHub Action** (`.github/workflows/braggard.yml`) and let it run unattended.

## 📝 Configuration

Braggard reads settings from `braggard.toml`. The file is searched for in
this order:

1. the path given on the command line or passed to `load_config`
2. `./braggard.toml` in the current directory
3. `$XDG_CONFIG_HOME/braggard/braggard.toml` or
   `~/.config/braggard/braggard.toml`

The first file found is used; otherwise a `FileNotFoundError` is raised.

---

## 📚 Docs & meta‑files

* [ROADMAP](./ROADMAP.md) – delivery phases & milestones  
* [SPEC](./SPEC.md) – technical specification & data model  
* [ARCHITECTURE](./ARCHITECTURE.md) – component interactions & diagrams  
* [CONTRIBUTING](./CONTRIBUTING.md) – how to hack on Braggard  
* [SECURITY](./SECURITY.md) – vulnerability disclosure policy  
* [CODE OF CONDUCT](./CODE_OF_CONDUCT.md)

---

## 🛠 Development

Install the development requirements and install the project in editable mode:

```bash
pip install -r requirements-dev.txt
pip install -e .
```

Run tests with `pytest` or use the pre‑commit hooks:

```bash
pre-commit run --all-files
```

---

## ❤️ Contributing

Pull‑requests are welcome! See [CONTRIBUTING](./CONTRIBUTING.md).

Released under the MIT License © 2025 Sean Evans.
