"""Static site renderer."""

from __future__ import annotations

import json
import os
from pathlib import Path
from textwrap import dedent

from jinja2 import Template


HTML_TEMPLATE = Template(
    dedent(
        """
        <!DOCTYPE html>
        <html lang="en">
        <meta charset="utf-8" />
        <title>Braggard Report</title>
        <body>
        <h1>Braggard Report</h1>
        <p>Generated at {{ summary.generated_at }}</p>
        <h2>Aggregates</h2>
        <ul>
          <li>Total repos: {{ summary.aggregate.repo_count }}</li>
          <li>Total stars: {{ summary.aggregate.total_stars }}</li>
        </ul>
        <h2>Languages</h2>
        <ul>
        {% for lang, count in summary.aggregate.languages.items() %}
          <li>{{ lang }}: {{ count }}</li>
        {% endfor %}
        </ul>
        </body>
        </html>
        """
    )
)


def render(
    output_dir: str = "docs", *, summary_path: str | Path = "summary.json"
) -> None:
    """Render ``summary_path`` into ``output_dir/index.html``."""

    if not os.path.exists(summary_path):
        raise FileNotFoundError("Run `braggard analyze` first")

    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    output = HTML_TEMPLATE.render(summary=summary)
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(output)
