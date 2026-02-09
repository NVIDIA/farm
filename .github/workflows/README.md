# CI/CD Architecture

This directory contains GitHub Actions workflows organized as a composable architecture with reusable modules.

## Workflow Structure

```
workflows/
├── ci.yaml                 # PR orchestrator
├── release.yaml            # Release orchestrator
├── semantic-release.yaml   # Version management (push to main)
├── _python.yaml            # Reusable: Python lint + test
├── _frontend.yaml          # Reusable: Frontend build + lint + test
├── _docker.yaml            # Reusable: Docker build + save artifact
├── _docker-publish.yaml    # Reusable: Docker load artifact + push
├── _helm.yaml              # Reusable: Helm validate
├── _helm-publish.yaml      # Reusable: Helm publish
└── _e2e.yaml               # Reusable: E2E tests with Playwright
```

### Naming Convention

- **Orchestrators** (`ci.yaml`, `release.yaml`): Trigger on events and coordinate reusable workflows
- **Reusable modules** (`_*.yaml`): Prefixed with underscore, called via `workflow_call`

## Workflows

### `ci.yaml` — Pull Request CI

**Trigger:** `pull_request` to `main`

Runs conditional checks based on changed files:

```
detect-changes
 │
 ├── backend ───→ _python.yaml    (if nv/**, tests/**, pyproject.toml, poetry.lock)
 ├── frontend ──→ _frontend.yaml  (if dashboard-ui/**)
 ├── docker ────→ _docker.yaml    (if Dockerfile*, .dockerignore, OR backend/frontend changed)
 │                    │
 │                    ▼
 │               [artifact: docker-image]
 │                    │
 └── helm ──────→ _helm.yaml      (if helm/**)
 │
 ▼
e2e ───→ _e2e.yaml (downloads docker-image artifact)
 │
 ▼
ci-status (final gate)
```

The `ci-status` job aggregates results and fails if any job failed (skipped jobs are OK).

### `release.yaml` — Release Pipeline

**Trigger:** `release: types: [published]`

Runs all checks then publishes artifacts:

```
determine-version
 │
 ├── backend ───────→ _python.yaml
 ├── frontend ──────→ _frontend.yaml
 ├── docker-build ──→ _docker.yaml
 │                        │
 │                        ▼
 │                   [artifact: docker-image]
 │                        │
 └── helm-validate ─→ _helm.yaml
 │
 ▼
e2e ───→ _e2e.yaml (downloads docker-image artifact)
 │
 ├── publish-docker ──→ _docker-publish.yaml
 │                          │
 │                     [loads artifact, re-tags, pushes]
 │
 └── publish-helm ────→ _helm-publish.yaml
```

### `semantic-release.yaml` — Version Management

**Trigger:** `push` to `main`

Runs semantic-release to:
- Analyze commits since last release
- Determine version bump (major/minor/patch)
- Update `pyproject.toml`, `Chart.yaml`, `CHANGELOG.md`
- Create GitHub release (which triggers `release.yaml`)

## Reusable Modules

### `_python.yaml`

Python backend lint and test.

**Jobs:**
1. `lint` — flake8 (black/isort commented out pending formatting fixes)
2. `test` — pytest (depends on lint)

### `_frontend.yaml`

Frontend build, lint, and test.

**Jobs:**
1. `build` — `npm ci` + `npm run build` (uploads dist artifact)
2. `lint` — `npm run lint` (parallel with tests)
3. `test-node` — `npx vitest run --project=node`
4. `test-browser` — `npx vitest run --project=browser` (with Playwright)

### `_docker.yaml`

Docker image build and artifact upload.

**Inputs:**
| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `registry` | string | `ghcr.io` | Container registry |
| `image_name` | string | `${{ github.repository }}` | Image name |

**Outputs:**
| Output | Description |
|--------|-------------|
| `image_tag` | Primary image tag built |

**Behavior:**
- Builds Docker image
- Saves image as `docker-image` artifact for downstream jobs

### `_docker-publish.yaml`

Docker image publish (loads artifact and pushes to registry).

**Inputs:**
| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `registry` | string | `ghcr.io` | Container registry |
| `image_name` | string | `${{ github.repository }}` | Image name |

**Behavior:**
- Downloads `docker-image` artifact
- Loads and re-tags with release version
- Pushes to container registry

**Tagging strategy:**
- `{{version}}` (e.g., `1.0.0`)
- `{{major}}.{{minor}}` (e.g., `1.0`)

### `_helm.yaml`

Helm chart validation.

**Inputs:**
| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `chart_path` | string | `helm/nv.svc.farm` | Path to Helm chart |

**Jobs:**
1. `validate` — lint + template with test values

### `_helm-publish.yaml`

Helm chart publish.

**Inputs:**
| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `chart_path` | string | `helm/nv.svc.farm` | Path to Helm chart |

**Jobs:**
1. `publish` — package + push to OCI registry

### `_e2e.yaml`

End-to-end tests using Playwright against the full application stack.

**Prerequisites:**
- Requires `docker-image` artifact from `_docker.yaml`

**Steps:**
1. Downloads and loads Docker image artifact
2. Starts services via `docker-compose.yaml`
3. Waits for health check
4. Runs Playwright tests (`dashboard-ui/e2e/`)
5. Uploads test report on failure

**Local development:**
```bash
make e2e-up      # Start services
make e2e-test    # Run Playwright tests
make e2e-down    # Stop services
```

## Docker Artifact Flow

The Docker image is built once and reused across jobs to save CI time:

```
_docker.yaml
    │
    ▼
  docker save
    │
    ▼
 [artifact: docker-image]
    │
    ├────────────────┐
    ▼                ▼
  _e2e.yaml      _docker-publish.yaml
  [docker load]  [docker load]
  [run tests]    [docker push]
```

## Change Detection

The CI workflow uses [dorny/paths-filter](https://github.com/dorny/paths-filter) to detect changes:

| Filter | Paths |
|--------|-------|
| `backend` | `nv/**`, `tests/**`, `pyproject.toml`, `poetry.lock` |
| `frontend` | `dashboard-ui/**` |
| `docker` | `Dockerfile*`, `.dockerignore` |
| `helm` | `helm/**` |

Docker builds also run when backend or frontend changes (for integration testing).

## Branch Protection

Configure the `ci-status` job as a required status check for PRs to main. This ensures all relevant checks pass while allowing skipped jobs (when files didn't change).
