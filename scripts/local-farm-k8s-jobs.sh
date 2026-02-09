#!/usr/bin/env bash

set -e
set -u

export NV__SVC__FARM__JOBS__STORE_CLASS="nv.svc.farm.services.jobs.facilities.store.directory.DirectoryJobStore"
export NV__SVC__FARM__CONTROLLER__JOB_MANAGER_CLASS="nv.svc.farm.services.jobs.facilities.manager.k8s.KubernetesProcessManager"

farm
