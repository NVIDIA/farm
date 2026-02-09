## Getting Started

This guide helps you set up and run the Farm service locally.

**In this guide:**
- [Clone the Repository](#clone-the-repository)
- [Install Dependencies](#install-dependencies)
- [Run Locally](#run-locally)
- [Next steps](#next-steps)

### Clone the Repository

First, clone the Farm repository:

```bash
git clone ssh://.../farm.git
cd nv.svc.farm
```

### Install Dependencies

Project Python requirement (from `pyproject.toml`): `>=3.10.1,<4.0.0`

- Python >= 3.10.1,<4.0.0 (3.12.x recommended)
- Poetry (latest)

Installation references:
- Python: https://www.python.org/downloads/
- Poetry: https://python-poetry.org/docs/#installation

### Run Locally

From the project root:

fetch the dashboard
```bash
cd dashboard-ui && npm ci && npm run build -- --outDir ../nv/svc/farm/services/dashboard/build --emptyOutDir
```

build and start farm
```bash
poetry env use python3.12
poetry install -v --without dev
poetry run farm
```

### Next steps

Now that Farm is deployed and running, continue to [Create a Job CLI](create-a-job-cli.md) to learn about:

- **Running the job CLI locally**: Use Python to execute transformations
- **Testing locally**: Validate outputs written to the local JSON store
- **Understanding job structure**: See how the CLI interacts with Farm APIs and storage
