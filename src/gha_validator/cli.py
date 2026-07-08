"""Command-line entrypoint for ``gha-validator`` (``gha-lint``)."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import click

from .config import Config
from .rules import Finding
from .validator import discover_workflows, evaluate, exceeds_threshold


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
    )


def _render_text(findings: list[Finding]) -> str:
    if not findings:
        return "No issues found."
    lines = [
        f"[{f.severity.upper()}] {f.source}: {f.rule} — {f.message}"
        for f in findings
    ]
    lines.append(f"\n{len(findings)} issue(s) found.")
    return "\n".join(lines)


def _render_json(findings: list[Finding]) -> str:
    return json.dumps([f.__dict__ for f in findings], indent=2)


def _render_sarif(findings: list[Finding]) -> str:
    level_map = {"error": "error", "warning": "warning", "info": "note"}
    results = [
        {
            "ruleId": f.rule,
            "level": level_map[f.severity],
            "message": {"text": f.message},
            "locations": [
                {"physicalLocation": {"artifactLocation": {"uri": f.source}}}
            ],
        }
        for f in findings
    ]
    sarif = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [{"tool": {"driver": {"name": "gha-validator"}}, "results": results}],
    }
    return json.dumps(sarif, indent=2)


_RENDERERS = {"text": _render_text, "json": _render_json, "sarif": _render_sarif}


@click.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(list(_RENDERERS)),
    default="text",
    help="Output format for findings.",
)
@click.option(
    "--fail-on",
    type=click.Choice(["info", "warning", "error"]),
    default="error",
    help="Minimum severity that fails the run.",
)
def main(path: Path, output_format: str, fail_on: str) -> None:
    """Lint hardened GitHub Actions workflows found under PATH.

    Checks pinned actions, least-privilege permissions, per-job timeouts and
    concurrency groups, then exits non-zero when a finding meets the
    ``--fail-on`` threshold.
    """
    config = Config.from_env(output_format=output_format, fail_on=fail_on)
    _configure_logging(config.log_level)
    workflows = discover_workflows(path)
    findings = evaluate(workflows, config)
    click.echo(_RENDERERS[output_format](findings))
    if exceeds_threshold(findings, fail_on):
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
