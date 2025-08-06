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

MARKDOWN_TEMPLATE = Template(
    dedent(
        """
        # Braggard Report

        Generated at {{ summary.generated_at }}

        ## Aggregates

        * Total repos: {{ summary.aggregate.repo_count }}
        * Total stars: {{ summary.aggregate.total_stars }}

        ## Languages
        {% for lang, count in summary.aggregate.languages.items() %}
        * {{ lang }}: {{ count }}
        {% endfor %}
        """
    )
)

TEXT_TEMPLATE = Template(
    dedent(
        """
        Braggard Report

        Generated at {{ summary.generated_at }}

        Aggregates
        - Total repos: {{ summary.aggregate.repo_count }}
        - Total stars: {{ summary.aggregate.total_stars }}

        Languages
        {% for lang, count in summary.aggregate.languages.items() %}
        - {{ lang }}: {{ count }}
        {% endfor %}
        """
    )
)


def render(
    output_dir: str = "docs",
    *,
    summary_path: str | Path = "summary.json",
    output_format: str = "html",
) -> None:
    """Render ``summary_path`` into ``output_dir``.

    ``output_format`` determines which file is created. Supported formats are
    ``"html"``, ``"markdown"``, and ``"text"``.
    """

    if not os.path.exists(summary_path):
        raise FileNotFoundError("Run `braggard analyze` first")

    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    output_format = output_format.lower()
    if output_format == "html":
        template = HTML_TEMPLATE
        filename = "index.html"
    elif output_format == "markdown":
        template = MARKDOWN_TEMPLATE
        filename = "index.md"
    elif output_format == "text":
        template = TEXT_TEMPLATE
        filename = "report.txt"
    else:
        raise ValueError(f"Unsupported format: {output_format}")

    output = template.render(summary=summary)
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        f.write(output)
