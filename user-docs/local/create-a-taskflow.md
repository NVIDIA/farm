## Create A Taskflow

**In this guide:**
- [Overview](#overview)
- [Understanding the DAG Payload](#understanding-the-dag-payload)
- [Simple Taskflow: Store → Piglatinize](#simple-taskflow-store--piglatinize)
- [Fan-Out DAG: Store → (Piglatinize + Haikuize)](#fan-out-dag-store--piglatinize--haikuize)
- [Fan-In DAG: (Store1 → Bannerize, Store2 → Shadowize) → Generate-Report](#fan-in-dag-store1--bannerize-store2--shadowize--generate-report)
- [Putting It All Together](#putting-it-all-together)
- [Next Steps](#next-steps)

### Overview

Now that you've created individual tasks, you can orchestrate them into a multi-step taskflow using Farm's DAG (Directed Acyclic Graph) capabilities. In this guide, you'll:
1. Understand the DAG submission payload and how it relates to task and job definitions
2. Create a simple two-step taskflow using the [Tasks service](index.md#swagger-documentation) `/submit-graph` endpoint
3. Build a fan-out DAG where one task triggers multiple parallel tasks
4. Build a fan-in DAG where multiple tasks converge into a single downstream task

The key difference between submitting individual tasks and submitting a taskflow is that taskflows automatically manage dependencies: tasks wait for their upstream dependencies to complete before starting, and Farm coordinates the execution order.

### Understanding the DAG Payload

A DAG submission consists of three main components:

1. **user**: The user submitting the taskflow (same as individual task submission)
2. **name**: A descriptive name for the DAG (used for display and tracking)
3. **nodes**: An array of task nodes, where each node contains:
   - **task**: A complete task definition (identical to what you'd submit via `/submit`)
   - **depends_on**: An array of node names this task depends on
   - **name**: A unique identifier for this node in the graph

Each node's `task` object uses the same structure you learned in [Create a Job](create-a-job.md), including `task_type`, `task_args`, `task_requirements`, and `metadata`. The `depends_on` array establishes the execution order: a task won't start until all tasks listed in `depends_on` have completed successfully.

Farm validates the graph structure to ensure it's acyclic (no circular dependencies) and that all dependency references point to valid nodes. Once validated, tasks with no dependencies start immediately, while dependent tasks wait in an `unscheduled` state.

> **Note:** The DAG uses each node's `name` as a unique identifier during validation. Ensure all node names are unique and that dependencies reference valid names. You may also notice that `input_node` and entries in `input_node_list` mirror node names. This is by design: `wordctl` stores the node name alongside the data so results can be referenced by node name at submission time. This is an implementation detail of `wordctl` that leverages unique node names for simple, consistent addressing. For details, see the store integration in [farm_apis.py](../wordctl/store/farm_apis.py).

### Simple Taskflow: Store → Piglatinize

Let's start with a basic two-step pipeline: store some text, then transform it using piglatinize. Create `./user-docs/simple-taskflow.json`:

```json
{
    "user": "local-user",
    "name": "Simple Store to Piglatinize",
    "nodes": [
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "store",
                    "output_node": "store-node",
                    "text": "Hello World"
                },
                "task_comment": "store-node",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": [],
            "name": "store-node"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "piglatinize",
                    "input_node": "store-node",
                    "output_node": "piglatinize-node"
                },
                "task_comment": "piglatinize-node",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["store-node"],
            "name": "piglatinize-node"
        }
    ]
}
```

Note how:
- `store-node` has an empty `depends_on` array, so it starts immediately
- `piglatinize-node` depends on `store-node` and uses it as `input_node`
- Each `output_node`/`input_node` used by wordctl matches a specific node in the graph

Submit the taskflow:
```bash
curl -X POST \
  "http://localhost:8222/queue/management/tasks/submit-graph" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  --data-binary @./user-docs/simple-taskflow.json
```

The response includes a `dag_id` and a list of `task_ids`:
```json
{
    "dag_id": "a3f5c8d1-2b4e-4a7c-9f8e-1d3c5b7a9e2f",
    "task_ids": [
        "b4e6d9f2-3c5f-4b8d-af9f-2e4d6c8b0f3g",
        "c5f7eaf3-4d6g-5c9e-bg0g-3f5e7d9c1g4h"
    ]
}
```

Monitor the DAG in the [dashboard](http://localhost:8222/queue/management/dashboard). You'll see:
1. `store-node` starts immediately and completes
2. `piglatinize-node` waits until `store-node` finishes, then runs automatically

Once both tasks complete, verify the results:
```bash
# Check the piglatinize-node result (use the appropriate task_id from the response)
curl "http://localhost:8222/queue/management/results/task/<piglatinize-task-id>"
```

You should see the piglatinized version of "Hello World".

### Fan-Out DAG: Store → (Piglatinize + Haikuize)

A fan-out pattern has one root task that triggers multiple parallel downstream tasks. This is useful when you need to apply different transformations to the same data. Create `./user-docs/fan-out-taskflow.json`:

```json
{
    "user": "local-user",
    "name": "Fan-Out: Store to Multiple Transforms",
    "nodes": [
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "store",
                    "output_node": "store-node",
                    "text": "The Quick Brown Fox"
                },
                "task_comment": "store-node",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": [],
            "name": "store-node"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "piglatinize",
                    "input_node": "store-node",
                    "output_node": "piglatinize-node"
                },
                "task_comment": "piglatinize-node",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["store-node"],
            "name": "piglatinize-node"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "haikuize",
                    "input_node": "store-node",
                    "output_node": "haikuize-node"
                },
                "task_comment": "haikuize-node",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["store-node"],
            "name": "haikuize-node"
        }
    ]
}
```

Here's the dependency structure:
```
     store-node
          |
    -------------
    |           |
piglatinize  haikuize
```

Both `piglatinize-node` and `haikuize-node` depend on `store-node`, so they:
- Wait for `store-node` to complete
- Start in parallel once `store-node` finishes
- Each processes the stored data independently

Submit the taskflow:
```bash
curl -X POST \
  "http://localhost:8222/queue/management/tasks/submit-graph" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  --data-binary @./user-docs/fan-out-taskflow.json
```

Watch the [dashboard](http://localhost:8222/queue/management/dashboard) to see the parallel execution. After `store-node` completes, both transformation tasks start simultaneously (assuming sufficient cluster resources).

### Fan-In DAG: (Store1 → Bannerize, Store2 → Shadowize) → Generate-Report

A fan-in pattern has multiple independent root tasks that converge into a single downstream task. This is useful when you need to combine outputs from different pipelines. Create `./user-docs/fan-in-taskflow.json`:

```json
{
    "user": "local-user",
    "name": "Fan-In: Multiple Stores to Single Report",
    "nodes": [
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "store",
                    "output_node": "store1-node",
                    "text": "Roses are red"
                },
                "task_comment": "store1-node",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": [],
            "name": "store1-node"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "store",
                    "output_node": "store2-node",
                    "text": "Violets are blue"
                },
                "task_comment": "store2-node",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": [],
            "name": "store2-node"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "bannerize",
                    "input_node": "store1-node",
                    "output_node": "bannerize-node"
                },
                "task_comment": "bannerize-node",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["store1-node"],
            "name": "bannerize-node"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "shadowize",
                    "input_node": "store2-node",
                    "output_node": "shadowize-node"
                },
                "task_comment": "shadowize-node",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["store2-node"],
            "name": "shadowize-node"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "generate-report",
                    "input_node_list": "bannerize-node,shadowize-node"
                },
                "task_comment": "report-node",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["bannerize-node", "shadowize-node"],
            "name": "report-node"
        }
    ]
}
```

Here's the dependency structure:
```
 store1-node       store2-node
     |                 |
bannerize-node    shadowize-node
     |                 |
     -------------------
              |
         report-node
```

The execution flow:
1. `store1-node` and `store2-node` start immediately in parallel
2. Once `store1-node` completes, `bannerize-node` starts
3. Once `store2-node` completes, `shadowize-node` starts
4. `report-node` waits for both `bannerize-node` and `shadowize-node` to finish
5. Once both dependencies complete, `report-node` generates a combined report

Note how `report-node` uses `input_node_list` with comma-separated values to consume outputs from multiple upstream tasks.

Submit the taskflow:
```bash
curl -X POST \
  "http://localhost:8222/queue/management/tasks/submit-graph" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  --data-binary @./user-docs/fan-in-taskflow.json
```

After all tasks complete, check the final report by viewing the task logs in the [dashboard](http:localhost:8222/queue/management/dashboard) to see the generated report combining both transformation outputs.

### Putting It All Together

Now let's combine everything you've learned by adding a new transformation to the container and building a complex multi-branch DAG. You'll create a `shuffleize` command that randomly shuffles word order, then compose a taskflow with three parallel processing pipelines that each apply the full transformation sequence.

#### Add the shuffleize command

First, create the new command file at `./user-docs/wordctl/commands/shuffleize.py`:

```python
"""Shuffleize command: randomly shuffle word order."""

import argparse
import random
from typing import Dict, List

from store import load_node, save_node


def _shuffleize(words: List[str]) -> List[str]:
    """Shuffle the order of words randomly."""
    shuffled = words.copy()
    random.shuffle(shuffled)
    return shuffled


def _shuffleize_data(data: Dict[str, str], node_name: str) -> Dict[str, str]:
    data["node_name"] = node_name
    data["actions"].append("shuffleize")
    data["words"] = _shuffleize(data["words"])
    return data


def add_parser(subparsers) -> None:
    """Register the 'shuffleize' subcommand."""
    sp = subparsers.add_parser("shuffleize", help="Shuffle word order")
    sp.add_argument("--input-node", required=True, help="Node to read input text from")
    sp.add_argument("--output-node", default="ROOT_NODE", help="Node name to store into")
    sp.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    """Execute the shuffleize command using the provided CLI ``args``."""
    input_node = load_node(args.input_node)
    data = _shuffleize_data(input_node, args.output_node)
    save_node(args.output_node, data)
```

#### Register the new command

Update `./user-docs/wordctl/wordctl.py` to import and register the shuffleize command. Change the import line:

```python
from commands import store, piglatinize, haikuize, bannerize, shadowize, shuffleize, generate_report
```

And add the parser registration in the `make_parser` function (after shadowize):

```python
    shuffleize.add_parser(subparsers)
```

#### Create the multi-branch taskflow

Create `./user-docs/complete-taskflow.json` with three parallel pipelines that each shuffle the data differently, apply all transformations, and converge to a final report:

```json
{
    "user": "local-user",
    "name": "Complete Multi-Branch Transformation Pipeline",
    "nodes": [
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "store",
                    "output_node": "store-node",
                    "text": "A Quick Brown Fox Jumped Over The Lazy Dog"
                },
                "task_comment": "store-node",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": [],
            "name": "store-node"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "shuffleize",
                    "input_node": "store-node",
                    "output_node": "shuffle-node-1"
                },
                "task_comment": "shuffle-node-1",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["store-node"],
            "name": "shuffle-node-1"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "shuffleize",
                    "input_node": "store-node",
                    "output_node": "shuffle-node-2"
                },
                "task_comment": "shuffle-node-2",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["store-node"],
            "name": "shuffle-node-2"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "shuffleize",
                    "input_node": "store-node",
                    "output_node": "shuffle-node-3"
                },
                "task_comment": "shuffle-node-3",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["store-node"],
            "name": "shuffle-node-3"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "piglatinize",
                    "input_node": "shuffle-node-1",
                    "output_node": "piglatinize-node-1"
                },
                "task_comment": "piglatinize-node-1",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["shuffle-node-1"],
            "name": "piglatinize-node-1"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "piglatinize",
                    "input_node": "shuffle-node-2",
                    "output_node": "piglatinize-node-2"
                },
                "task_comment": "piglatinize-node-2",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["shuffle-node-2"],
            "name": "piglatinize-node-2"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "piglatinize",
                    "input_node": "shuffle-node-3",
                    "output_node": "piglatinize-node-3"
                },
                "task_comment": "piglatinize-node-3",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["shuffle-node-3"],
            "name": "piglatinize-node-3"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "haikuize",
                    "input_node": "piglatinize-node-1",
                    "output_node": "haikuize-node-1"
                },
                "task_comment": "haikuize-node-1",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["piglatinize-node-1"],
            "name": "haikuize-node-1"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "haikuize",
                    "input_node": "piglatinize-node-2",
                    "output_node": "haikuize-node-2"
                },
                "task_comment": "haikuize-node-2",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["piglatinize-node-2"],
            "name": "haikuize-node-2"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "haikuize",
                    "input_node": "piglatinize-node-3",
                    "output_node": "haikuize-node-3"
                },
                "task_comment": "haikuize-node-3",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["piglatinize-node-3"],
            "name": "haikuize-node-3"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "bannerize",
                    "input_node": "haikuize-node-1",
                    "output_node": "bannerize-node-1"
                },
                "task_comment": "bannerize-node-1",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["haikuize-node-1"],
            "name": "bannerize-node-1"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "bannerize",
                    "input_node": "haikuize-node-2",
                    "output_node": "bannerize-node-2"
                },
                "task_comment": "bannerize-node-2",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["haikuize-node-2"],
            "name": "bannerize-node-2"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "bannerize",
                    "input_node": "haikuize-node-3",
                    "output_node": "bannerize-node-3"
                },
                "task_comment": "bannerize-node-3",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["haikuize-node-3"],
            "name": "bannerize-node-3"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "shadowize",
                    "input_node": "bannerize-node-1",
                    "output_node": "shadowize-node-1"
                },
                "task_comment": "shadowize-node-1",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["bannerize-node-1"],
            "name": "shadowize-node-1"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "shadowize",
                    "input_node": "bannerize-node-2",
                    "output_node": "shadowize-node-2"
                },
                "task_comment": "shadowize-node-2",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["bannerize-node-2"],
            "name": "shadowize-node-2"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "shadowize",
                    "input_node": "bannerize-node-3",
                    "output_node": "shadowize-node-3"
                },
                "task_comment": "shadowize-node-3",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["bannerize-node-3"],
            "name": "shadowize-node-3"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "generate-report",
                    "input_node_list": "shadowize-node-1,shadowize-node-2,shadowize-node-3"
                },
                "task_comment": "generate-report",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["shadowize-node-1", "shadowize-node-2", "shadowize-node-3"],
            "name": "generate-report"
        }
    ]
}
```

This DAG creates the following execution flow:

```
                    store-node
                         |
          -------------------------------
          |              |              |
   shuffle-node-1  shuffle-node-2  shuffle-node-3
          |              |              |
 piglatinize-node-1 piglatinize-node-2 piglatinize-node-3
          |              |              |
   haikuize-node-1  haikuize-node-2  haikuize-node-3
          |              |              |
  bannerize-node-1 bannerize-node-2 bannerize-node-3
          |              |              |
  shadowize-node-1 shadowize-node-2 shadowize-node-3
          |              |              |
          -------------------------------
                         |
                   generate-report
```

Each branch:
1. Shuffles the original stored words (creating three different random orderings)
2. Applies the full transformation pipeline independently
3. Converges to a single report that displays all three variants

#### Submit and monitor the taskflow

Submit the complete taskflow:

```bash
curl -X POST \
  "http://localhost:8222/queue/management/tasks/submit-graph" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  --data-binary @./user-docs/complete-taskflow.json
```

Watch the execution in the [dashboard](http://localhost:8222/queue/management/dashboard). You'll see:

1. **store-node** runs first
2. Three **shuffle-node** tasks start in parallel
3. Each branch cascades through its transformation pipeline
4. **generate-report** waits for all three shadowize tasks to complete
5. The final report shows three different shuffled variations with all transformations applied

This demonstrates Farm's power: you defined a complex 17-task taskflow with multiple fan-out and fan-in patterns, and Farm automatically orchestrated the entire execution, managing dependencies, coordinating results, and ensuring tasks run in the correct order.

### Next Steps

You've now mastered the fundamentals of Farm taskflows! Continue to [Advanced Taskflow Features](advanced-taskflow-features.md) to learn about:

- **Dependency Resolution Strategies**: Run tasks regardless of upstream failures (useful for cleanup, reporting, and notifications)
- **Automatic Retry Configuration**: Handle transient failures with configurable retry logic
- **Combining Features**: Build production-ready, fault-tolerant pipelines

