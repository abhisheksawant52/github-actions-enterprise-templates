"""Load GitHub Actions workflows and evaluate them against hardening rules."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

from .config import SEVERITIES, Config
from .rules import ALL_RULES, Finding

logger = logging.getLogger(__name__)

_SEVERITY_ORDER = {name: index for index, name in enumerate(SEVERITIES)}


@dataclass(frozen=True)
class WorkflowFile:
    """A parsed workflow document paired with its source path."""

    path: Path
    document: dict


def discover_workflows(root: Path) -> list[Path]:
    """Return all ``*.yml`` / ``*.yaml`` files under *root* (a dir or a file)."""
    if root.is_file():
        return [root]
    return sorted(
        p for p in root.rglob("*") if p.suffix in {".yml", ".yaml"} and p.is_file()
    )


def load_workflow(path: Path) -> WorkflowFile | None:
    """Parse a single workflow file, returning ``None`` if it is not a mapping."""
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:  # pragma: no cover - defensive
        logger.warning("Skipping unparseable workflow %s: %s", path, exc)
        return None
    if not isinstance(document, dict):
        return None
    return WorkflowFile(path=path, document=document)


def evaluate(paths: Iterable[Path], config: Config | None = None) -> list[Finding]:
    """Run every rule against every workflow and collect the findings."""
    cfg = config or Config()
    findings: list[Finding] = []
    for path in paths:
        workflow = load_workflow(path)
        if workflow is None:
            continue
        for rule in ALL_RULES:
            findings.extend(rule(workflow.document, str(workflow.path), cfg))
    return findings


def max_severity(findings: Iterable[Finding]) -> str | None:
    """Return the highest severity present, or ``None`` for an empty set."""
    severities = [f.severity for f in findings]
    if not severities:
        return None
    return max(severities, key=lambda s: _SEVERITY_ORDER.get(s, 0))


def exceeds_threshold(findings: Iterable[Finding], fail_on: str) -> bool:
    """True if any finding is at or above the *fail_on* severity threshold."""
    threshold = _SEVERITY_ORDER.get(fail_on, len(SEVERITIES) - 1)
    return any(_SEVERITY_ORDER.get(f.severity, 0) >= threshold for f in findings)
