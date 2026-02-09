// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

package main

import (
	"sync"
	"time"

	"github.com/google/uuid"
)

// FunctionStatus represents the status of a function
type FunctionStatus string

const (
	StatusInactive  FunctionStatus = "INACTIVE"
	StatusActive    FunctionStatus = "ACTIVE"
	StatusError     FunctionStatus = "ERROR"
	StatusDeploying FunctionStatus = "DEPLOYING"
)

// FunctionType represents the type of function
type FunctionType string

const (
	FunctionTypeDefault FunctionType = "DEFAULT"
)

// HealthConfig represents the health check configuration
type HealthConfig struct {
	URI                string `json:"uri"`
	Port               int    `json:"port"`
	Protocol           string `json:"protocol"`
	ExpectedStatusCode int    `json:"expectedStatusCode"`
	Timeout            string `json:"timeout"`
}

// ActiveInstance represents an active function instance
type ActiveInstance struct {
	InstanceID        string    `json:"instanceId"`
	FunctionID        string    `json:"functionId"`
	FunctionVersionID string    `json:"functionVersionId"`
	InstanceType      string    `json:"instanceType"`
	InstanceStatus    string    `json:"instanceStatus"`
	SisRequestID      string    `json:"sisRequestId"`
	NcaID             string    `json:"ncaId"`
	GPU               string    `json:"gpu"`
	Backend           string    `json:"backend"`
	Location          string    `json:"location"`
	InstanceCreatedAt time.Time `json:"instanceCreatedAt"`
	InstanceUpdatedAt time.Time `json:"instanceUpdatedAt"`
}

// CreateFunctionRequest represents the request to create a function
type CreateFunctionRequest struct {
	Name                 string       `json:"name"`
	Tags                 []string     `json:"tags"`
	Health               HealthConfig `json:"health"`
	InferenceURL         string       `json:"inferenceUrl"`
	InferencePort        int          `json:"inferencePort"`
	ContainerImage       string       `json:"containerImage,omitempty"`
	ContainerEnvironment []string     `json:"containerEnvironment,omitempty"`
	HelmChart            string       `json:"helmChart,omitempty"`
	HelmChartServiceName string       `json:"helmChartServiceName,omitempty"`
}

// Function represents a created function
type Function struct {
	ID                   string           `json:"id"`
	NcaID                string           `json:"ncaId"`
	VersionID            string           `json:"versionId"`
	Name                 string           `json:"name"`
	Status               FunctionStatus   `json:"status"`
	InferenceURL         string           `json:"inferenceUrl"`
	InferencePort        int              `json:"inferencePort"`
	APIBodyFormat        string           `json:"apiBodyFormat"`
	HealthURI            string           `json:"healthUri"`
	CreatedAt            time.Time        `json:"createdAt"`
	Description          string           `json:"description"`
	Health               HealthConfig     `json:"health"`
	FunctionType         FunctionType     `json:"functionType"`
	ContainerImage       string           `json:"containerImage,omitempty"`
	ContainerEnvironment []string         `json:"containerEnvironment,omitempty"`
	HelmChart            string           `json:"helmChart,omitempty"`
	HelmChartServiceName string           `json:"helmChartServiceName,omitempty"`
	ActiveInstances      []ActiveInstance `json:"activeInstances,omitempty"`
}

// CreateFunctionResponse represents the response for creating a function
type CreateFunctionResponse struct {
	Function Function `json:"function"`
}

// GetFunctionDetailsResponse represents the response for getting function details
type GetFunctionDetailsResponse struct {
	Function Function `json:"function"`
}

// FunctionStore represents the in-memory store for functions
type FunctionStore struct {
	functions map[string]Function
	mutex     sync.RWMutex
}

// NewFunctionStore creates a new function store
func NewFunctionStore() *FunctionStore {
	return &FunctionStore{
		functions: make(map[string]Function),
	}
}

// CreateFunction adds a function to the store
func (fs *FunctionStore) CreateFunction(function Function) {
	fs.mutex.Lock()
	defer fs.mutex.Unlock()
	fs.functions[function.ID] = function
}

// GetFunction retrieves a function by ID
func (fs *FunctionStore) GetFunction(id string) (Function, bool) {
	fs.mutex.RLock()
	defer fs.mutex.RUnlock()
	function, exists := fs.functions[id]
	return function, exists
}

// GetAllFunctions returns all functions
func (fs *FunctionStore) GetAllFunctions() []Function {
	fs.mutex.RLock()
	defer fs.mutex.RUnlock()

	functions := make([]Function, 0, len(fs.functions))
	for _, function := range fs.functions {
		functions = append(functions, function)
	}
	return functions
}

// DeleteFunction removes a function from the store
func (fs *FunctionStore) DeleteFunction(id string) bool {
	fs.mutex.Lock()
	defer fs.mutex.Unlock()

	_, exists := fs.functions[id]
	if exists {
		delete(fs.functions, id)
		return true
	}
	return false
}

// GenerateFunctionID generates a new UUID for function ID
func GenerateFunctionID() string {
	return uuid.New().String()
}

// GenerateNcaID generates a realistic NCA ID
func GenerateNcaID() string {
	return "2Q-" + uuid.New().String()[:22]
}

// GenerateVersionID generates a new UUID for version ID
func GenerateVersionID() string {
	return uuid.New().String()
}

// GenerateInstanceID generates a new instance ID
func GenerateInstanceID() string {
	return uuid.New().String() + ".np-sjc6-04-gs"
}

// GenerateSisRequestID generates a new SIS request ID
func GenerateSisRequestID() string {
	return uuid.New().String()
}

// DeploymentSpecification represents a deployment specification
type DeploymentSpecification struct {
	InstanceType          string `json:"instanceType"`
	GPU                   string `json:"gpu"`
	MaxInstances          int    `json:"maxInstances"`
	MinInstances          int    `json:"minInstances"`
	MaxRequestConcurrency int    `json:"maxRequestConcurrency"`
	PreferredOrder        int    `json:"preferredOrder,omitempty"`
	CPUArch               string `json:"cpuArch,omitempty"`
	OS                    string `json:"os,omitempty"`
	DriverVersion         string `json:"driverVersion,omitempty"`
	Storage               string `json:"storage,omitempty"`
	SystemMemory          string `json:"systemMemory,omitempty"`
	GPUMemory             string `json:"gpuMemory,omitempty"`
}

// DeployFunctionRequest represents the request to deploy a function
type DeployFunctionRequest struct {
	DeploymentSpecifications []DeploymentSpecification `json:"deploymentSpecifications"`
}

// Deployment represents a function deployment
type Deployment struct {
	FunctionID               string                    `json:"functionId"`
	FunctionVersionID        string                    `json:"functionVersionId"`
	DeploymentID             string                    `json:"deploymentId"`
	FunctionName             string                    `json:"functionName"`
	NcaID                    string                    `json:"ncaId"`
	FunctionStatus           FunctionStatus            `json:"functionStatus"`
	RequestQueueURL          string                    `json:"requestQueueUrl"`
	DeploymentSpecifications []DeploymentSpecification `json:"deploymentSpecifications"`
	CreatedAt                time.Time                 `json:"createdAt"`
	LastUpdatedAt            time.Time                 `json:"lastUpdatedAt"`
}

// DeployFunctionResponse represents the response for deploying a function
type DeployFunctionResponse struct {
	Deployment Deployment `json:"deployment"`
}

// RequestStatus represents an error response for deployment
type RequestStatus struct {
	StatusCode        string `json:"statusCode"`
	StatusDescription string `json:"statusDescription"`
	RequestID         string `json:"requestId"`
}

// DeployFunctionErrorResponse represents an error response for deployment
type DeployFunctionErrorResponse struct {
	RequestStatus RequestStatus `json:"requestStatus"`
}

// ProblemDetails represents a problem details error response
type ProblemDetails struct {
	Type     string `json:"type"`
	Title    string `json:"title"`
	Status   int    `json:"status"`
	Detail   string `json:"detail"`
	Instance string `json:"instance"`
}
