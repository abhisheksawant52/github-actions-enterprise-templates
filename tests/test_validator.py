"""Integration-style tests for workflow discovery and evaluation."""

from pathlib import Path

from gha_validator.config import Config
from gha_validator.validator import (
    discover_workflows,
    evaluate,
    exceeds_threshold,
    max_severity,
)

HARDENED_WORKFLOW = """
name: CI
on:
  push:
    branches: [main]
permissions:
  contents: read
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
"""

RISKY_WORKFLOW = """
name: risky
on:
  push:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout
"""


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


def test_hardened_workflow_produces_no_findings(tmp_path: Path):
    _write(tmp_path, "ci.yml", HARDENED_WORKFLOW)
    findings = evaluate(discover_workflows(tmp_path), Config())
    assert findings == []
    assert max_severity(findings) is None


def test_risky_workflow_fails_threshold(tmp_path: Path):
    _write(tmp_path, "risky.yml", RISKY_WORKFLOW)
    findings = evaluate(discover_workflows(tmp_path), Config())
    rules = {f.rule for f in findings}
    assert "pinned-actions" in rules
    assert "least-privilege-permissions" in rules
    assert max_severity(findings) == "error"
    assert exceeds_threshold(findings, "error") is True


def test_discovery_finds_nested_workflows(tmp_path: Path):
    (tmp_path / "nested").mkdir()
    _write(tmp_path, "a.yml", HARDENED_WORKFLOW)
    _write(tmp_path / "nested", "b.yaml", HARDENED_WORKFLOW)
    assert len(discover_workflows(tmp_path)) == 2
