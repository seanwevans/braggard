"""Static site renderer."""

from __future__ import annotations

import json
import os
from pathlib import Path
from textwrap import dedent

from jinja2 import Environment, DictLoader


ENV = Environment(
    loader=DictLoader(
        {
            "html": dedent(
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
                {% if summary.repos %}
                <h2>Repositories</h2>
                <ul>
                {% for repo in summary.repos %}
                  <li>{{ repo.name }}: {{ repo.stars }}</li>
                {% endfor %}
                </ul>
                {% endif %}
                </body>
                </html>
                """
            ),
            "markdown": dedent(
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
                {% if summary.repos %}
                ## Repositories
                {% for repo in summary.repos %}
                * {{ repo.name }}: {{ repo.stars }}
                {% endfor %}
                {% endif %}
                """
            ),
            "text": dedent(
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
                {% if summary.repos %}
                Repositories
                {% for repo in summary.repos %}
                - {{ repo.name }}: {{ repo.stars }}
                {% endfor %}
                {% endif %}
                """
            ),
        }
    ),
    autoescape=True,
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
    mapping = {
        "html": ("html", "index.html"),
        "markdown": ("markdown", "index.md"),
        "text": ("text", "report.txt"),
    }
    try:
        template_name, filename = mapping[output_format]
    except KeyError:  # pragma: no cover - handled by ValueError below
        raise ValueError(f"Unsupported format: {output_format}")

    template = ENV.get_template(template_name)
    output = template.render(summary=summary)
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        f.write(output)
