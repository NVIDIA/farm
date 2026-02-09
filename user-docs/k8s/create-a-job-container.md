## Create A Job Container

**In this guide:**
- [Overview](#overview)
- [Create the container](#create-the-container)
- [Running the container](#running-the-container)
- [Next steps](#next-steps)

### Overview

Jobs in Farm can execute in multiple environments depending on your needs:
- Bare metal: run shell commands directly on hosts.
- Kubernetes: run as k8s Jobs managed by the controller.
- Docker: run containers directly.
- External APIs: trigger compute through interfaces like NVCT.

For this guide we focus on Kubernetes, which means our Job Definition includes a container image. The container we build is intentionally simple: a CLI you could also install on bare metal. In other words, the same job logic can be executed without a container when targeting bare metal shell, or wrapped into a container for k8s orchestration.

We will construct a small CLI to support a text-processing taskflow where the output of one job becomes the input to another. This lets you run one-off tasks or orchestrate a multi-step pipeline (DAG) when needed.

Before proceeding, familiarize yourself with the [wordctl container contents](../wordctl/wordctl.py):
- `commands/`: individual text transformations (e.g., `piglatinize.py`, `bannerize.py`, `haikuize.py`, `shadowize.py`, `generate_report.py`).
- `store/`: data abstractions and integrations. The most important piece here is `farm_apis.py`, which connects our job to Farm APIs, specifically the [Tasks service](index.md#swagger-documentation) and the [Results service](index.md#swagger-documentation), enabling jobs to read/write results and coordinate across steps.
- `wordctl.py`: the CLI entrypoint that wires commands together.


### Create the container

This command will build the Docker container and inject it into our cluster. To pick up any changes made to the container, run this command again to overwrite `wordctl:dev`.

```bash
devspace run-pipeline wordctl
```

### Running the container

#### 1) Prepare a local store file
Create (or reset) the JSON file we will mount for persistence between runs.
```bash
rm -rf ./user-docs/wordctl/store/nodes.json
touch ./user-docs/wordctl/store/nodes.json
```

#### 2) Seed data (store words)
Start the pipeline by storing a phrase; then inspect the results in `./user-docs/wordctl/store/nodes.json`.
```bash
docker run \
    -e WORDCTL_STORE="json" \
    -v "$(pwd)/user-docs/wordctl/store/nodes.json:/app/store/nodes.json" \
    wordctl:dev store "A Quick Brown Fox Jumped Over The Lazy Dog" --output-node "store-data-node"
```

Our words were stored under the key we specified using output-node as "store-data-node"
```json
{
    "store-data-node": {
        "node_name": "store-data-node",
        "actions": [],
        "words": [
            "A",
            "Quick",
            "Brown",
            "Fox",
            "Jumped",
            "Over",
            "The",
            "Lazy",
            "Dog"
        ]
    }
}
```

#### 3) Transform: piglatinize
Piglatinize the stored phrase using `store-data-node` as input and save to `piglatinize-data-node`. Inspect results in `./user-docs/wordctl/store/nodes.json`.

```bash
docker run \
    -e WORDCTL_STORE="json" \
    -v "$(pwd)/user-docs/wordctl/store/nodes.json:/app/store/nodes.json" \
    wordctl:dev piglatinize --input-node "store-data-node" --output-node "piglatinize-data-node"
```

Our piglatinize transformation has been applied using our originally stored data as the input!
```json
{
    "store-data-node": {
        "node_name": "store-data-node",
        "actions": [],
        "words": [
            "A",
            "Quick",
            "Brown",
            "Fox",
            "Jumped",
            "Over",
            "The",
            "Lazy",
            "Dog"
        ]
    },
    "piglatinize-data-node": {
        "node_name": "piglatinize-data-node",
        "actions": [
            "piglatinize"
        ],
        "words": [
            "Ayay",
            "Ickquay",
            "Ownbray",
            "Oxfay",
            "Umpedjay",
            "Overyay",
            "Ethay",
            "Azylay",
            "Ogday"
        ]
    }
}
```

#### 4) Transform: haikuize, bannerize, shadowize
Apply the remaining transformations, then generate a report to view the output.
```bash
docker run \
    -e WORDCTL_STORE="json" \
    -v "$(pwd)/user-docs/wordctl/store/nodes.json:/app/store/nodes.json" \
    wordctl:dev haikuize --input-node "piglatinize-data-node" --output-node "haikuize-data-node"

docker run \
    -e WORDCTL_STORE="json" \
    -v "$(pwd)/user-docs/wordctl/store/nodes.json:/app/store/nodes.json" \
    wordctl:dev bannerize --input-node "haikuize-data-node" --output-node "bannerize-data-node"

docker run \
    -e WORDCTL_STORE="json" \
    -v "$(pwd)/user-docs/wordctl/store/nodes.json:/app/store/nodes.json" \
    wordctl:dev shadowize --input-node "bannerize-data-node" --output-node "shadowize-data-node"

docker run \
    -e WORDCTL_STORE="json" \
    -v "$(pwd)/user-docs/wordctl/store/nodes.json:/app/store/nodes.json" \
    wordctl:dev generate-report --input-node "shadowize-data-node"
```

#### 5) View generated report
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

Stats:
- word count: 26
- character count: 328
- transformations: 4 -> piglatinize, haikuize, bannerize, shadowize
- score: 99  (chef's kiss. a true masterpiece of questionable metrics.)
```

#### 6) Inspect final state
Finally, inspect the full state of our data in the store file.
```json
{
    "store-data-node": {
        "node_name": "store-data-node",
        "actions": [],
        "words": [
            "A",
            "Quick",
            "Brown",
            "Fox",
            "Jumped",
            "Over",
            "The",
            "Lazy",
            "Dog"
        ]
    },
    "piglatinize-data-node": {
        "node_name": "piglatinize-data-node",
        "actions": [
            "piglatinize"
        ],
        "words": [
            "Ayay",
            "Ickquay",
            "Ownbray",
            "Oxfay",
            "Umpedjay",
            "Overyay",
            "Ethay",
            "Azylay",
            "Ogday"
        ]
    },
    "haikuize-data-node": {
        "node_name": "haikuize-data-node",
        "actions": [
            "piglatinize",
            "haikuize"
        ],
        "words": [
            "Ayay Ickquay Ownbray Oxfay Umpedjay",
            "Overyay Ethay Azylay Ogday Ayay Ickquay Ownbray",
            "Oxfay Umpedjay Overyay Ethay Azylay"
        ]
    },
    "bannerize-data-node": {
        "node_name": "bannerize-data-node",
        "actions": [
            "piglatinize",
            "haikuize",
            "bannerize"
        ],
        "words": [
            "*****************************************************",
            "**   Ayay Ickquay Ownbray Oxfay Umpedjay Overyay   **",
            "**  Ethay Azylay Ogday Ayay Ickquay Ownbray Oxfay  **",
            "**          Umpedjay Overyay Ethay Azylay          **",
            "*****************************************************"
        ]
    },
    "shadowize-data-node": {
        "node_name": "shadowize-data-node",
        "actions": [
            "piglatinize",
            "haikuize",
            "bannerize",
            "shadowize"
        ],
        "words": [
            "*****************************************************",
            "**   Ayay Ickquay Ownbray Oxfay Umpedjay Overyay   **░░",
            "**  Ethay Azylay Ogday Ayay Ickquay Ownbray Oxfay  **░░",
            "**          Umpedjay Overyay Ethay Azylay          **░░",
            "*****************************************************░░",
            "  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░"
        ]
    }
}
```

### Next steps

Now that you've built and tested the container locally, continue to [Create a Job](create-a-job.md) to learn about:

- **Job Definitions**: Configure how Farm executes your container
- **Uploading Jobs**: Register job definitions with the [Jobs service](index.md#swagger-documentation)
- **Submitting Tasks**: Run your first task through the [Tasks service](index.md#swagger-documentation) and view results
