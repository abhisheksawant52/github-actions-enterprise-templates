"""Runtime configuration for the workflow validator.

Configuration is intentionally lightweight: a frozen dataclass populated from
CLI options and environment variables so the linter has no hard dependency on a
settings framework.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

# Severities recognised by the rule engine, ordered from least to most severe.
SEVERITIES: tuple[str, ...] = ("info", "warning", "error")

# Action references that are always allowed to be unpinned (local composite
# actions and ``docker://`` images handle their own pinning semantics).
_DEFAULT_ALLOWED_PREFIXES: tuple[str, ...] = ("./", "docker://")


@dataclass(frozen=True)
class Config:
    """Validator configuration.

    Attributes:
        fail_on: Minimum severity (``info`` | ``warning`` | ``error``) that
            causes the CLI to exit non-zero.
        output_format: One of ``text``, ``json`` or ``sarif``.
        log_level: Standard library logging level name.
        allowed_unpinned_prefixes: ``uses:`` prefixes exempt from the
            pinned-actions rule.
    """

    fail_on: str = "error"
    output_format: str = "text"
    log_level: str = "INFO"
    allowed_unpinned_prefixes: tuple[str, ...] = field(
        default=_DEFAULT_ALLOWED_PREFIXES
    )

    @classmethod
    def from_env(cls, **overrides: object) -> "Config":
        """Build a config from environment variables, applying *overrides*.

        The ``GHA_VALIDATOR_LOG_LEVEL`` variable controls logging verbosity.
        Any keyword override with a non-``None`` value takes precedence.
        """
        base = {
            "log_level": os.environ.get("GHA_VALIDATOR_LOG_LEVEL", "INFO"),
        }
        base.update({k: v for k, v in overrides.items() if v is not None})
        return cls(**base)  # type: ignore[arg-type]
