"""Hardening rules for GitHub Actions workflows.

Each rule is a pure callable ``(document, source, config) -> list[Finding]``
over the parsed YAML document, which makes every rule trivially unit-testable.
The rule identifiers here are the contract documented in ``docs/catalog.md`` and
``docs/authoring-guide.md``; keep the three in sync.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .config import Config

# Matches ``owner/repo`` or ``owner/repo/path@ref``. An unpinned reference
# (no ``@ref``) is flagged by the pinned-actions rule.
_ACTION_REF = re.compile(r"^(?P<action>[\w.-]+/[\w./-]+?)(?:@(?P<ref>.+))?$")


@dataclass(frozen=True)
class Finding:
    """A single rule violation.

    Attributes:
        rule: Stable rule identifier (e.g. ``pinned-actions``).
        severity: One of ``info``, ``warning`` or ``error``.
        message: Human-readable explanation of the violation.
        source: Path of the workflow file the finding relates to.
    """

    rule: str
    severity: str
    message: str
    source: str


def _jobs(document: dict) -> dict:
    """Return the ``jobs`` mapping, or an empty dict when absent/malformed."""
    jobs = document.get("jobs")
    return jobs if isinstance(jobs, dict) else {}


def _is_reusable(document: dict) -> bool:
    """True when the workflow is a reusable one (``on: workflow_call``)."""
    on = document.get(True, document.get("on"))
    if isinstance(on, dict):
        return "workflow_call" in on
    if isinstance(on, list):
        return "workflow_call" in on
    return on == "workflow_call"


def check_pinned_actions(
    document: dict, source: str, config: Config
) -> list[Finding]:
    """Every ``uses:`` reference must be pinned to a tag or commit SHA."""
    findings: list[Finding] = []
    for job_name, job in _jobs(document).items():
        if not isinstance(job, dict):
            continue
        for step in job.get("steps", []) or []:
            uses = step.get("uses") if isinstance(step, dict) else None
            if not uses or uses.startswith(config.allowed_unpinned_prefixes):
                continue
            match = _ACTION_REF.match(uses)
            if match and not match.group("ref"):
                findings.append(
                    Finding(
                        rule="pinned-actions",
                        severity="error",
                        message=(
                            f"job '{job_name}': action '{uses}' is not pinned "
                            "to a version tag or commit SHA"
                        ),
                        source=source,
                    )
                )
    return findings


def check_least_privilege(
    document: dict, source: str, config: Config
) -> list[Finding]:
    """A top-level ``permissions`` block should be declared (least privilege)."""
    if "permissions" not in document:
        return [
            Finding(
                rule="least-privilege-permissions",
                severity="warning",
                message=(
                    "no top-level 'permissions' block; the GITHUB_TOKEN "
                    "defaults to broad write access"
                ),
                source=source,
            )
        ]
    return []


def check_job_timeouts(
    document: dict, source: str, config: Config
) -> list[Finding]:
    """Every job should set ``timeout-minutes`` to bound runaway runners."""
    findings: list[Finding] = []
    for job_name, job in _jobs(document).items():
        if isinstance(job, dict) and "timeout-minutes" not in job:
            findings.append(
                Finding(
                    rule="job-timeouts",
                    severity="warning",
                    message=f"job '{job_name}' has no 'timeout-minutes'",
                    source=source,
                )
            )
    return findings


def check_concurrency(
    document: dict, source: str, config: Config
) -> list[Finding]:
    """A ``concurrency`` group avoids redundant/overlapping runs.

    Reusable workflows (``on: workflow_call``) are exempt: concurrency is the
    responsibility of the calling workflow, so requiring it here would produce
    false positives across the template library.
    """
    if _is_reusable(document):
        return []
    if "concurrency" not in document:
        return [
            Finding(
                rule="concurrency-control",
                severity="info",
                message="no 'concurrency' group; overlapping runs are not cancelled",
                source=source,
            )
        ]
    return []


# Rule execution order is stable so text/JSON/SARIF output is deterministic.
ALL_RULES = (
    check_pinned_actions,
    check_least_privilege,
    check_job_timeouts,
    check_concurrency,
)
