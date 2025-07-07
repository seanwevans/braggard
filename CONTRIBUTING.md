# Contributing Guide

First off, thanks for taking the time to contribute! 🎉

## Ground rules

* Be nice – follow our [Code of Conduct](./CODE_OF_CONDUCT.md).
* Use conventional commits (`feat:`, `fix:`, `docs:` …).
* All new code **must** have unit tests (`pytest`) and type hints (`mypy` clean).
* Run the formatter (`ruff format`) and linter (`ruff check`) before every push.

```bash
pip install -r requirements-dev.txt
ruff format .
ruff check .
pytest
```

## Workflow

1. Fork the repo & create a feature branch:  
   `git checkout -b feat/awesome‑thing`
2. Make your changes.
3. Update docs & tests.
4. Run `npm run tailwind:build` if you touched CSS.
5. Open a PR against `main`.
6. One core maintainer review is required before merge.

## Commit style

```
<type>(scope): <subject>
```
Examples:
* `feat(renderer): add dark‑mode toggle`
* `fix(collector): handle API pagination bug`
* `docs(readme): clarify PAT scope`

## Becoming a maintainer

Frequent, high‑quality contributors may receive push access.  
Show that you care about code quality, documentation, and user success.
