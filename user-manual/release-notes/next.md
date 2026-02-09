# Next

**Release Date**: January 2026

## Highlights

**First Open Source Release**

This is the first open source release of Farm.

**Taskflows**

Taskflows have been added to Farm as a method to represent a complex directed acyclic graph (DAG) when processing tasks. This permits more complex workflows including processing tasks following fan-in and fan-out patterns.

Examples for the creation and usage of the Taskflow feature are provided as part of the `/user-docs/k8s` and `/user-docs/local` usage guides.

## Added

- Nothing here yet.

## Fixed

- Nothing here yet.

## Improved

- K8s task queueing has been improved to use available bulk APIs.

## Removed

- Batch IDs have been deprecated and replaced with Taskflows for grouping tasks as a unit.

- MySQL and Redis deployments are no longer performed via the included Helm charts due to the Bitnami chart removal. Users should deploy a compatible database and redis instance independently of the included Helm charts.
