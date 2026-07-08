"""Unit tests for the workflow hardening rules."""

from gha_validator.config import Config
from gha_validator.rules import (
    check_concurrency,
    check_job_timeouts,
    check_least_privilege,
    check_pinned_actions,
)

CFG = Config()

HARDENED = {
    "on": {"push": {"branches": ["main"]}},
    "permissions": {"contents": "read"},
    "concurrency": {"group": "ci-${{ github.ref }}", "cancel-in-progress": True},
    "jobs": {
        "build": {
            "timeout-minutes": 15,
            "steps": [{"uses": "actions/checkout@v4"}],
        }
    },
}

RISKY = {
    "on": {"push": {"branches": ["main"]}},
    "jobs": {
        "build": {
            "steps": [{"uses": "actions/checkout"}],
        }
    },
}

REUSABLE = {
    "on": {"workflow_call": {"inputs": {}}},
    "permissions": {"contents": "read"},
    "jobs": {"build": {"timeout-minutes": 10, "steps": [{"uses": "actions/checkout@v4"}]}},
}


def test_hardened_workflow_has_no_findings():
    assert check_pinned_actions(HARDENED, "wf", CFG) == []
    assert check_least_privilege(HARDENED, "wf", CFG) == []
    assert check_job_timeouts(HARDENED, "wf", CFG) == []
    assert check_concurrency(HARDENED, "wf", CFG) == []


def test_unpinned_action_is_flagged_as_error():
    findings = check_pinned_actions(RISKY, "wf", CFG)
    assert len(findings) == 1
    assert findings[0].severity == "error"
    assert findings[0].rule == "pinned-actions"


def test_missing_permissions_is_warning():
    findings = check_least_privilege(RISKY, "wf", CFG)
    assert findings and findings[0].severity == "warning"


def test_missing_timeout_is_flagged():
    assert check_job_timeouts(RISKY, "wf", CFG)[0].rule == "job-timeouts"


def test_missing_concurrency_is_info():
    findings = check_concurrency(RISKY, "wf", CFG)
    assert findings and findings[0].severity == "info"


def test_reusable_workflow_is_exempt_from_concurrency():
    assert check_concurrency(REUSABLE, "wf", CFG) == []


def test_local_composite_action_is_not_flagged():
    doc = {"jobs": {"b": {"steps": [{"uses": "./actions/setup-python-cached"}]}}}
    assert check_pinned_actions(doc, "wf", CFG) == []
