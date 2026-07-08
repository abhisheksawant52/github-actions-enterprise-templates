# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-08

### Added

- Hardened reusable workflows callable via `workflow_call`:
  `reusable-python-ci`, `reusable-node-ci`, `reusable-docker-build-push`,
  `reusable-terraform-plan`, `reusable-security-scan`, and `reusable-release`.
- Composite actions: `setup-python-cached`, `semantic-version`, and
  `notify-slack`.
- `gha-validator` (`gha-lint`) linter enforcing pinned actions,
  least-privilege permissions, per-job timeouts, and concurrency groups, with
  text/JSON/SARIF output.
- Documentation: workflow `catalog.md` and an `authoring-guide.md`.
- This repository's own CI pipeline, pre-commit hooks, and open-source project
  files (LICENSE, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, templates,
  CODEOWNERS, dependabot).
