# Authoring Guide: Writing Hardened Workflows

This guide describes the house style every workflow and composite action in this
library follows. The `gha-validator` linter (`gha-lint`) enforces the
machine-checkable parts of it in CI.

## The four hardening rules

The validator implements four rules. Their identifiers are stable and match the
ones reported in the CLI output and SARIF.

| Rule ID | Severity | What it requires |
| --- | --- | --- |
| `pinned-actions` | error | Every `uses:` reference is pinned to a version tag or commit SHA. Local (`./…`) and `docker://` references are exempt. |
| `least-privilege-permissions` | warning | A top-level `permissions:` block is declared, ideally read-only. |
| `job-timeouts` | warning | Every job sets `timeout-minutes`. |
| `concurrency-control` | info | A `concurrency:` group is present. Reusable workflows (`on: workflow_call`) are exempt; the caller owns concurrency. |

Run the linter locally:

```bash
gha-lint .github/workflows            # human-readable
gha-lint .github/workflows --format sarif > gha.sarif
gha-lint .github/workflows --fail-on warning
```

## Reusable workflow checklist

- Trigger with `on: workflow_call` and declare typed `inputs`, `secrets`, and
  `outputs` explicitly. Give every input a `description` and a sensible
  `default`.
- Add a least-privilege top-level `permissions:` block. Start from
  `contents: read` and add only what a job genuinely needs (e.g.
  `packages: write` for GHCR, `security-events: write` for SARIF upload).
- Set `timeout-minutes` on every job.
- Pin third-party actions to a major version tag (`@v4`, `@v5`) or, for higher
  assurance, a full commit SHA.
- Do not declare `concurrency` inside a reusable workflow; let the calling
  workflow decide.
- Never hardcode secrets. Accept them through the `secrets:` block and reference
  them as `${{ secrets.NAME }}`.

## Consumer workflow checklist

A workflow that *calls* these reusable workflows should:

- Define its own `concurrency` group to cancel superseded runs.
- Grant the minimum `permissions` required by the workflows it calls.
- Pin the reusable workflow to a tag or SHA (`@v0.1.0`) in production.

## Composite action checklist

- Use `runs.using: composite` and give every `run` step an explicit `shell:`.
- Declare `inputs` with descriptions and defaults, and `outputs` mapped to step
  outputs via `${{ steps.<id>.outputs.<name> }}`.
- Pass data through environment variables in `run` steps rather than
  interpolating untrusted input directly into shell commands.

## Example: a hardened reusable workflow skeleton

```yaml
name: Reusable Example
on:
  workflow_call:
    inputs:
      target:
        description: What to operate on.
        type: string
        default: "."
permissions:
  contents: read
jobs:
  run:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - run: echo "operating on ${{ inputs.target }}"
```
