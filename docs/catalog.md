# Workflow & Action Catalog

This library ships hardened, reusable GitHub Actions workflows (callable via
`workflow_call`) and composite actions. Every workflow declares a
least-privilege `permissions` block, per-job `timeout-minutes`, and pins actions
to major version tags. The `gha-validator` linter enforces these properties in
CI.

Reference workflows at a stable ref, e.g. `@main` or a release tag `@v0.1.0`.

## Reusable workflows

| Workflow | Purpose | Key inputs | Secrets | Outputs |
| --- | --- | --- | --- | --- |
| `reusable-python-ci.yml` | Lint (ruff/black) and test a Python project across a version matrix | `python-versions`, `working-directory`, `run-lint` | — | — |
| `reusable-node-ci.yml` | Install, lint, test and build a Node.js project across a version matrix | `node-versions`, `package-manager`, `build-script` | — | — |
| `reusable-docker-build-push.yml` | Build a container image and optionally push it to GHCR | `image-name`, `registry`, `push`, `platforms` | `registry-token` | `image-digest` |
| `reusable-terraform-plan.yml` | `fmt`/`init`/`validate`/`plan` a Terraform root module | `working-directory`, `terraform-version`, `var-file` | `cloud-credentials` | — |
| `reusable-security-scan.yml` | Trivy filesystem scan + CodeQL analysis, uploading SARIF | `languages`, `trivy-severity`, `run-codeql` | — | — |
| `reusable-release.yml` | Compute the next version, tag, and publish a GitHub Release | `release-as`, `tag-prefix`, `draft` | — | `version` |

### `reusable-python-ci.yml`

```yaml
jobs:
  ci:
    uses: abhisheksawant52/github-actions-enterprise-templates/.github/workflows/reusable-python-ci.yml@main
    with:
      python-versions: '["3.11", "3.12"]'
      working-directory: .
```

### `reusable-node-ci.yml`

```yaml
jobs:
  ci:
    uses: abhisheksawant52/github-actions-enterprise-templates/.github/workflows/reusable-node-ci.yml@main
    with:
      node-versions: '["20", "22"]'
      package-manager: npm
```

### `reusable-docker-build-push.yml`

Requires `permissions: packages: write` in the caller when pushing to GHCR.

```yaml
jobs:
  image:
    permissions:
      contents: read
      packages: write
    uses: abhisheksawant52/github-actions-enterprise-templates/.github/workflows/reusable-docker-build-push.yml@main
    with:
      image-name: ${{ github.repository }}
      push: ${{ github.ref == 'refs/heads/main' }}
    secrets:
      registry-token: ${{ secrets.GITHUB_TOKEN }}
```

### `reusable-terraform-plan.yml`

```yaml
jobs:
  plan:
    uses: abhisheksawant52/github-actions-enterprise-templates/.github/workflows/reusable-terraform-plan.yml@main
    with:
      working-directory: environments/dev
      var-file: dev.tfvars
```

### `reusable-security-scan.yml`

```yaml
jobs:
  scan:
    permissions:
      contents: read
      security-events: write
    uses: abhisheksawant52/github-actions-enterprise-templates/.github/workflows/reusable-security-scan.yml@main
    with:
      languages: '["python"]'
```

### `reusable-release.yml`

```yaml
jobs:
  release:
    permissions:
      contents: write
    uses: abhisheksawant52/github-actions-enterprise-templates/.github/workflows/reusable-release.yml@main
    with:
      release-as: minor
```

## Composite actions

| Action | Purpose | Key inputs | Outputs |
| --- | --- | --- | --- |
| `actions/setup-python-cached` | Install Python with pip caching and optionally install the project | `python-version`, `install`, `install-args` | `python-version` |
| `actions/semantic-version` | Compute the next semantic version/tag from the latest git tag | `release-as`, `tag-prefix` | `version`, `tag` |
| `actions/notify-slack` | Post a workflow status message to a Slack webhook | `webhook-url`, `status`, `message` | — |

### Using a composite action

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: abhisheksawant52/github-actions-enterprise-templates/actions/setup-python-cached@main
    with:
      python-version: "3.12"
```
