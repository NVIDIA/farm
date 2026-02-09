## Advanced Taskflow Features

Farm provides two key features for building resilient taskflows: dependency resolution strategies and automatic retries.

**In this guide:**
- [Dependency Resolution Strategy](#dependency-resolution-strategy)
- [Automatic Retry Configuration](#automatic-retry-configuration)
- [Combining Features](#combining-features)

### Dependency Resolution Strategy

By default, tasks only run if all dependencies succeed (strategy: `ON_SUCCESS`). If any dependency fails, downstream tasks become `unschedulable`. However, some tasks—like cleanup, logging, or reporting—need to run regardless of upstream failures.

#### Demonstrating ON_SUCCESS (Default)

Let's use a word processing pipeline where we insert an `error` node by utilizing the built in `--error` or `--random-error` flags to one of our transformations:

```
            store-node
                |
    --------------------------
    |           |            |
 haikuize   piglatinize!  bannerize
    |           |            |
    --------------------------
                |
          generate-report   (unschedulable: depends on failed piglatinize)
```

Create `./user-docs/advanced-taskflow.json`. The key change is setting `task_args.error: true` on `piglatinize-node`, which causes that task attempt to fail deterministically under the default ON_SUCCESS strategy:

```json
{
    "user": "local-user",
    "name": "Word Processing Pipeline (Default Behavior)",
    "nodes": [
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "store",
                    "output_node": "store-node",
                    "text": "The Quick Brown Fox Jumps Over The Lazy Dog"
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
                    "output_node": "piglatinize-node",
                    "error": true
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
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "bannerize",
                    "input_node": "store-node",
                    "output_node": "bannerize-node"
                },
                "task_comment": "bannerize-node",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["store-node"],
            "name": "bannerize-node"
        },
        {
            "task": {
                "task_type": "wordctl",
                "task_args": {
                    "subcommand": "generate-report",
                    "input_node_list": "haikuize-node,piglatinize-node,bannerize-node"
                },
                "task_comment": "generate-report",
                "metadata": {
                    "_retry": {
                        "is_retryable": false
                    }
                }
            },
            "depends_on": ["haikuize-node", "piglatinize-node", "bannerize-node"],
            "name": "generate-report"
        }
    ]
}
```

Submit and observe in the [dashboard](http://farm.127-0-0-1.nip.io:8080/queue/management/dashboard):

```bash
curl -X POST "http://farm.127-0-0-1.nip.io:8080/queue/management/tasks/submit-graph" \
  -H "Content-Type: application/json" --data-binary @./user-docs/advanced-taskflow.json
```

**Result**: `haikuize-node` and `bannerize-node` complete successfully, but `piglatinize-node` fails due to the injected `--error`. Because `generate-report` depends on all three transformations, it becomes `unschedulable`. This is the default `ON_SUCCESS` behavior—it prevents processing incomplete data.

#### Using ALWAYS_RUN

Set `dependency_resolution_strategy: "ALWAYS_RUN"` in task metadata to run regardless of upstream failures. Ideal for cleanup, logging, reporting, and notifications.

Update `./user-docs/advanced-taskflow.json` to add `ALWAYS_RUN` to the `generate-report` task:

```json
{
    "task": {
        "task_type": "wordctl",
        "task_args": {
            "subcommand": "generate-report",
            "input_node_list": "haikuize-node,piglatinize-node,bannerize-node"
        },
        "task_comment": "generate-report",
        "metadata": {
            "_retry": {
                "is_retryable": false
            },
            "dag": {
                "dependency_resolution_strategy": "ALWAYS_RUN"
            }
        }
    },
    "depends_on": ["haikuize-node", "piglatinize-node", "bannerize-node"],
    "name": "generate-report"
}
```

Submit and observe:

```bash
curl -X POST "http://farm.127-0-0-1.nip.io:8080/queue/management/tasks/submit-graph" \
  -H "Content-Type: application/json" --data-binary @./user-docs/advanced-taskflow.json
```

**Result**: `piglatinize-node` still fails (due to `--error`), but `generate-report` has `ALWAYS_RUN`, so it runs once all dependencies finish. The report shows output from the two successful transformations: `haikuize-node` and `bannerize-node`. The `piglatinize-node` output is missing since it failed.

Click on the `generate-report` task in the dashboard to view the task detail page and see the partial report with the two successful transformation outputs.

### Automatic Retry Configuration

Configure automatic retries for transient failures (network issues, resource constraints, service timeouts) using the `_retry` metadata:

```json
"metadata": {
    "_retry": {
        "is_retryable": true,  // Enable retries (default: true)
        "limit": 5             // Max attempts (default: 3)
    }
}
```

#### Example with --random-error flag

Inject probabilistic failure directly on a `wordctl` task using the `--random-error` flag. Update `./user-docs/advanced-taskflow.json` to change the `piglatinize-node` task:

```json
{
    "task": {
        "task_type": "wordctl",
        "task_args": {
            "subcommand": "piglatinize",
            "input_node": "store-node",
            "output_node": "piglatinize-node",
            "random_error": true,
            "error_message": "Piglatinize failed with forced error using the --random-error flag"
        },
        "task_comment": "piglatinize-node",
        "metadata": {
            "_retry": {
                "is_retryable": true,
                "limit": 5
            }
        }
    },
    "depends_on": ["store-node"],
    "name": "piglatinize-node"
}
```

The `--random-error` flag introduces a probabilistic failure of 66% per attempt. Retries are controlled by `_retry` (e.g., `limit: 5`). Once an attempt succeeds, downstream tasks can proceed.

Submit and watch in the [dashboard](http://farm.127-0-0-1.nip.io:8080/queue/management/dashboard):

```bash
curl -X POST "http://farm.127-0-0-1.nip.io:8080/queue/management/tasks/submit-graph" \
  -H "Content-Type: application/json" --data-binary @./user-docs/advanced-taskflow.json
```

**Result**: The `piglatinize-node` task will likely fail on initial attempts, then automatically retry up to 5 times. Once an attempt succeeds, `generate-report` completes with all three transformation outputs.

Click on the `piglatinize-node` task in the dashboard to view retry counts and attempt history (see **Revisions**). Once complete, check the `generate-report` task to see all three transformation outputs in the final report.

### Combining Features

Combine both features for robust, fault-tolerant taskflows:

```json
{
    "task": {
        "task_type": "wordctl",
        "task_args": {
            "subcommand": "generate-report",
            "input_node_list": "haikuize-node,piglatinize-node,bannerize-node"
        },
        "task_comment": "generate-report",
        "metadata": {
            "_retry": {
                "is_retryable": true,
                "limit": 10
            },
            "dag": {
                "dependency_resolution_strategy": "ALWAYS_RUN"
            }
        }
    },
    "depends_on": ["haikuize-node", "piglatinize-node", "bannerize-node"],
    "name": "generate-report"
}
```

This task runs regardless of upstream failures (`ALWAYS_RUN`) and retries up to 10 times if report generation fails.

