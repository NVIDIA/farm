## Create A Job CLI

**In this guide:**
- [Overview](#overview)
- [Run the CLI](#run-the-cli)
- [Next steps](#next-steps)

### Overview

Jobs in Farm can execute in multiple environments depending on your needs:
- Bare metal: run shell commands directly on hosts.
- Kubernetes: run as k8s Jobs managed by the controller.
- Docker: run containers directly.
- External APIs: trigger compute through interfaces like NVCT.

For this guide we focus on running locally without containers. The CLI is intentionally simple: it’s the same job logic you could later wrap into a container for k8s orchestration. We will use a small CLI to support a text-processing taskflow where the output of one step becomes the input to another.

Before proceeding, familiarize yourself with the `wordctl` project:
- `user-docs/wordctl/wordctl.py`: the CLI entrypoint that wires commands together.
- `user-docs/wordctl/commands/`: individual transformations (e.g., `piglatinize.py`, `bannerize.py`, `haikuize.py`, `shadowize.py`, `generate_report.py`).
- `user-docs/wordctl/store/`: data abstractions and integrations. The most important piece here is `farm_apis.py`, which connects our job to Farm APIs, specifically the [Tasks service](index.md#swagger-documentation) and the [Results service](index.md#swagger-documentation), enabling jobs to read/write results and coordinate across steps.

### Run the CLI

All commands below run from the repository root (`nv.svc.farm/`). We’ll set an environment variable so the CLI uses the JSON store.

#### 1) Prepare a local store file
Create (or reset) the JSON file we will use for persistence between runs.
```bash
rm -rf ./user-docs/wordctl/store/nodes.json
touch ./user-docs/wordctl/store/nodes.json
```

#### 2) Seed data (store words)
Start the pipeline by storing a phrase; then inspect the results in `./user-docs/wordctl/store/nodes.json`.
```bash
WORDCTL_STORE=json python3 ./user-docs/wordctl/wordctl.py store "A Quick Brown Fox Jumped Over The Lazy Dog" --output-node "store-data-node"
```

Our words were stored under the key we specified using output-node as "store-data-node":
```json
{
  "store-data-node": {
    "node_name": "store-data-node",
    "actions": [],
    "words": ["A", "Quick", "Brown", "Fox", "Jumped", "Over", "The", "Lazy", "Dog"]
  }
}
```

#### 3) Transform: piglatinize
Piglatinize the stored phrase using `store-data-node` as input and save to `piglatinize-data-node`. Inspect results in `./user-docs/wordctl/store/nodes.json`.
```bash
WORDCTL_STORE=json python3 ./user-docs/wordctl/wordctl.py piglatinize --input-node "store-data-node" --output-node "piglatinize-data-node"
```

#### 4) Transform: haikuize, bannerize, shadowize, then generate a report
```bash
WORDCTL_STORE=json python3 ./user-docs/wordctl/wordctl.py haikuize --input-node "piglatinize-data-node" --output-node "haikuize-data-node"
WORDCTL_STORE=json python3 ./user-docs/wordctl/wordctl.py bannerize --input-node "haikuize-data-node" --output-node "bannerize-data-node"
WORDCTL_STORE=json python3 ./user-docs/wordctl/wordctl.py shadowize --input-node "bannerize-data-node" --output-node "shadowize-data-node"
WORDCTL_STORE=json python3 ./user-docs/wordctl/wordctl.py generate-report --input-node "shadowize-data-node"
```

You should see a report similar to:
```bash
Report: shadowize-data-node
===========================
Content:
*****************************************************
**   Ayay Ickquay Ownbray Oxfay Umpedjay Overyay   **░░
**  Ethay Azylay Ogday Ayay Ickquay Ownbray Oxfay  **░░
**          Umpedjay Overyay Ethay Azylay          **░░
*****************************************************░░
  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

#### 5) Inspect final state
Finally, inspect the full state of our data in the store file:
```bash
cat ./user-docs/wordctl/store/nodes.json
```

### Next steps

Now that you’ve built and tested the CLI locally, continue to [Create a Job](create-a-job.md) to learn about:

- **Job Definitions**: Configure how Farm executes your logic (containerized or otherwise)
- **Uploading Jobs**: Register job definitions with the [Jobs service](index.md#swagger-documentation)
- **Submitting Tasks**: Run your first task through the [Tasks service](index.md#swagger-documentation) and view results


