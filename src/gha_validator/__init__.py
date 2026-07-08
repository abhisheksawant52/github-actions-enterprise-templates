"""gha-validator: a hardening linter for GitHub Actions workflows.

The package exposes a small rule engine that parses workflow YAML and checks it
against enterprise hardening rules (pinned actions, least-privilege
``permissions``, per-job ``timeout-minutes`` and ``concurrency`` groups).
"""

from __future__ import annotations

from .rules import ALL_RULES, Finding
from .validator import discover_workflows, evaluate, exceeds_threshold, max_severity

__all__ = [
    "ALL_RULES",
    "Finding",
    "discover_workflows",
    "evaluate",
    "exceeds_threshold",
    "max_severity",
    "__version__",
]

__version__ = "0.1.0"
