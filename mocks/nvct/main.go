// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

package main

import (
	"encoding/json"
	"io"
	"log/slog"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"
)

const LISTEN_ADDR = ":8877"

type Task struct {
	statusId    TaskStatus
	Status      string
	Description string
}

var taskMutex sync.RWMutex
var tasks = make(map[uint64]*Task, 0)
var taskIndex uint64

type TaskStatus int64

const (
	TaskStatusUnknown TaskStatus = iota
	TaskStatusQueued
	TaskStatusRunning
	TaskStatusCompleted
	TaskStatusErrored
	TaskStatusCanceled
)

func (t TaskStatus) toString() string {
	switch t {
	case TaskStatusQueued:
		return "QUEUED"
	case TaskStatusRunning:
		return "RUNNING"
	case TaskStatusCompleted:
		return "COMPLETED"
	case TaskStatusErrored:
		return "ERRORED"
	case TaskStatusCanceled:
		return "CANCELED"
	default:
		return "UNKNOWN"
	}
}

type NvctTaskCreateRequest struct {
	Name    string `json:"name,omitempty"`
	GpuSpec struct {
		Gpu          string `json:"gpu,omitempty"`
		Backend      string `json:"backend,omitempty"`
		InstanceType string `json:"instanceType,omitempty"`
	} `json:"gpuSpecification,omitempty"`
	ContainerImage       string `json:"containerImage,omitempty"`
	ContainerArgs        string `json:"containerArgs,omitempty"`
	ContainerEnvironment []struct {
		Key   string `json:"key,omitempty"`
		Value string `json:"value,omitempty"`
	} `json:"containerEnvironment,omitempty"`
	Models []struct {
		Name    string `json:"name,omitempty"`
		Version string `json:"version,omitempty"`
		Uri     string `json:"uri,omitempty"`
	} `json:"models,omitempty"`
	Resources []struct {
		Name    string `json:"name,omitempty"`
		Version string `json:"version,omitempty"`
		Uri     string `json:"uri,omitempty"`
	} `json:"resources,omitempty"`
	Tags                   []string `json:"tags,omitempty"`
	Description            string   `json:"description,omitempty"`
	MaxRuntime             string   `json:"maxRuntimeDuration,omitempty"`
	MaxQueued              string   `json:"maxQueuedDuration,omitempty"`
	TerminationGracePeriod string   `json:"terminationGracePeriodDuration,omitempty"`
	ResultHandlingStrategy string   `json:"resultHandlingStrategy,omitempty"`
}

type NvctTaskCreateResponse struct {
	TaskInfo NvctTaskInfo `json:"task"`
}

type NvctTaskInfo struct {
	Id         string `json:"id"`
	NcaId      string `json:"ncaId,omitempty"`
	FarmId     string `json:"name,omitempty"`
	Status     string `json:"status"`
	HealthInfo struct {
		SisRequestId string `json:"sisRequestId,omitempty"`
		Error        string `json:"error,omitempty"`
	} `json:"healthInfo,omitempty"`
	Instances []struct {
		InstanceId   string `json:"instanceId,omitempty"`
		SisRequestId string `json:"sisRequestId,omitempty"`
	} `json:"instances,omitempty"`
}

type NvctTaskInfoResponse struct {
	TaskInfo NvctTaskInfo `json:"task"`
}

type NvctBulkTaskRequest struct {
	TaskIds []string `json:"taskIds"`
}

type NvctBulkTaskResponse struct {
	NcaId string         `json:"ncaId"`
	Tasks []NvctBulkTask `json:"tasks"`
}

type NvctBulkTask struct {
	Id     string `json:"id"`
	Name   string `json:"name"`
	Status string `json:"status"`
}

func taskCreate(w http.ResponseWriter, r *http.Request) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		slog.Error("failed to read task create body", "error", err)
		w.WriteHeader(http.StatusInternalServerError)
		_, _ = w.Write([]byte("failed to ready post body\n"))
		return
	}

	var req NvctTaskCreateRequest
	if err := json.Unmarshal(body, &req); err != nil {
		slog.Error("failed to unmarshal task create body", "error", err)
		w.WriteHeader(http.StatusBadRequest)
		_, _ = w.Write([]byte("failed to unmarshal body payload\n"))
		return
	}

	taskMutex.Lock()
	defer taskMutex.Unlock()

	taskIndex += 1
	task := Task{
		statusId:    TaskStatusQueued,
		Description: req.Description,
	}
	tasks[taskIndex] = &task

	slog.Info("created task", "taskId", taskIndex, "description", req.Description)

	resp := NvctTaskCreateResponse{
		NvctTaskInfo{
			Id:     strconv.FormatUint(taskIndex, 10),
			Status: task.statusId.toString()}}

	data, err := json.Marshal(resp)
	if err != nil {
		slog.Error("failed to marshal response", "error", err)
		return
	}

	w.Header().Add("Content-Type", "application/json")
	_, err = w.Write(data)
	if err != nil {
		slog.Error("failed to write task create response", "error", err)
	}
}

func init() {
	// This runs automatically when the program starts
	rand.Seed(time.Now().UnixNano())
}

func getRandomNumber() int {
	return rand.Intn(10) + 1
}

func mockTaskProcessing(task *Task) {
	// Only process tasks that are currently running
	if task.statusId != TaskStatusRunning {
		return
	}

	// Check for special task names that should simulate errors
	switch task.Description {
	case "error":
		// Always set to errored status
		task.statusId = TaskStatusErrored
		slog.Debug("mock task processing: setting task to errored", "taskName", task.Description)
	case "random-error":
		// Randomly set to either errored or completed
		if getRandomNumber() >= 5 {
			task.statusId = TaskStatusErrored
			slog.Debug("mock task processing: randomly set task to errored", "taskName", task.Description)
		} else {
			task.statusId = TaskStatusCompleted
			slog.Debug("mock task processing: randomly set task to completed", "taskName", task.Description)
		}
	}
}

func incrementTaskStatus(task *Task) {
	// Check for special mock task processing first
	mockTaskProcessing(task)

	// If the task was processed by mockTaskProcessing and is now in a terminal state,
	// don't proceed with normal status progression
	if task.statusId == TaskStatusErrored || task.statusId == TaskStatusCompleted {
		return
	}

	// Define valid status transitions
	nextStatus := getNextStatus(task.statusId)
	if nextStatus != TaskStatusUnknown {
		task.statusId = nextStatus
	}
}

func getNextStatus(current TaskStatus) TaskStatus {
	slog.Debug("getting next status", "current", current)
	switch current {
	case TaskStatusQueued:
		return TaskStatusRunning
	case TaskStatusRunning:
		return TaskStatusCompleted
	default:
		return current
	}
}

func taskInfo(w http.ResponseWriter, r *http.Request) {
	taskIdRaw := r.PathValue("taskId")
	taskId, err := strconv.ParseUint(taskIdRaw, 10, 64)
	if err != nil {
		slog.Debug("failed to parse int from taskId", "error", err, "taskIdRaw", taskIdRaw)
		w.WriteHeader(http.StatusBadRequest)
		_, _ = w.Write([]byte("failed to convert taskId to an int\n"))
		return
	}

	taskMutex.RLock()
	defer taskMutex.RUnlock()
	taskInfo, ok := tasks[taskId]
	if !ok {
		slog.Debug("requested taskid does not exist", "taskid", taskId)
		w.WriteHeader(http.StatusNotFound)
		_, _ = w.Write([]byte("requested taskid does not exist\n"))
		return
	}
	slog.Debug("incrementing task status", "taskId", taskId)
	incrementTaskStatus(taskInfo)
	taskInfo.Status = taskInfo.statusId.toString()
	resp := NvctTaskInfoResponse{
		NvctTaskInfo{
			Id:     strconv.FormatUint(taskId, 10),
			Status: taskInfo.statusId.toString()}}

	info, err := json.Marshal(resp)
	if err != nil {
		slog.Debug("failed to marshal task info", "error", err, "taskid", taskId)
		w.WriteHeader(http.StatusInternalServerError)
		_, _ = w.Write([]byte("failed to marshal task info to json\n"))
		return
	}

	slog.Debug("task info provided", "taskid", taskId)

	w.Header().Add("Content-Type", "application/json")
	_, err = w.Write(info)
	if err != nil {
		slog.Error("failed to write task info response", "error", err)
	}
}

func taskCancel(w http.ResponseWriter, r *http.Request) {
	taskIdRaw := r.PathValue("taskId")
	taskId, err := strconv.ParseUint(taskIdRaw, 10, 64)
	if err != nil {
		slog.Debug("failed to parse int from taskid", "error", err, "taskidRaw", taskIdRaw)
		w.WriteHeader(http.StatusBadRequest)
		_, _ = w.Write([]byte("failed to convert taskId to an int\n"))
		return
	}

	taskMutex.Lock()
	defer taskMutex.Unlock()

	_, ok := tasks[taskId]
	if !ok {
		slog.Debug("requested taskid does not exist", "taskid", taskId)
		w.WriteHeader(http.StatusNotFound)
		_, _ = w.Write([]byte("requested taskid does not exist\n"))
		return
	}

	tasks[taskId].statusId = TaskStatusCanceled

	slog.Info("cancelled task", "taskId", taskId)
}

func taskBulkInfo(w http.ResponseWriter, r *http.Request) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		slog.Error("failed to read bulk task info body", "error", err)
		w.WriteHeader(http.StatusInternalServerError)
		_, _ = w.Write([]byte("failed to read post body\n"))
		return
	}

	var req NvctBulkTaskRequest
	if err := json.Unmarshal(body, &req); err != nil {
		slog.Error("failed to unmarshal bulk task info body", "error", err)
		w.WriteHeader(http.StatusBadRequest)
		_, _ = w.Write([]byte("failed to unmarshal body payload\n"))
		return
	}

	taskMutex.RLock()
	defer taskMutex.RUnlock()

	var bulkTasks []NvctBulkTask

	for _, taskIdStr := range req.TaskIds {
		taskId, err := strconv.ParseUint(taskIdStr, 10, 64)
		if err != nil {
			slog.Debug("failed to parse taskId", "error", err, "taskId", taskIdStr)
			continue // Skip invalid task IDs
		}

		taskInfo, ok := tasks[taskId]
		if !ok {
			slog.Debug("taskid does not exist", "taskid", taskId)
			continue // Skip non-existent tasks
		}

		incrementTaskStatus(taskInfo)
		taskInfo.Status = taskInfo.statusId.toString()

		bulkTask := NvctBulkTask{
			Id:     taskIdStr,
			Name:   taskInfo.Description,
			Status: taskInfo.statusId.toString(),
		}
		bulkTasks = append(bulkTasks, bulkTask)
	}

	resp := NvctBulkTaskResponse{
		NcaId: "mock-nca-id",
		Tasks: bulkTasks,
	}

	data, err := json.Marshal(resp)
	if err != nil {
		slog.Error("failed to marshal bulk task response", "error", err)
		w.WriteHeader(http.StatusInternalServerError)
		_, _ = w.Write([]byte("failed to marshal response\n"))
		return
	}

	w.Header().Add("Content-Type", "application/json")
	_, err = w.Write(data)
	if err != nil {
		slog.Error("failed to write bulk task response", "error", err)
	}
}

func main() {
	logger := slog.New(
		slog.NewJSONHandler(
			os.Stdout,
			&slog.HandlerOptions{Level: slog.LevelDebug}))
	slog.SetDefault(logger)

	http.HandleFunc("/v1/nvct/tasks", taskCreate)
	http.HandleFunc("/v1/nvct/tasks/{taskId}", taskInfo)
	http.HandleFunc("/v1/nvct/tasks/{taskId}/cancel", taskCancel)
	http.HandleFunc("/v1/nvct/tasks/bulk", taskBulkInfo) // Add this line

	slog.Info("waiting for connections", "listen_addr", LISTEN_ADDR)

	if err := http.ListenAndServe(LISTEN_ADDR, nil); err != nil {
		panic(err)
	}
}
