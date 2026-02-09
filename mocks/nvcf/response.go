// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

package main

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/google/uuid"
)

// ErrorResponse represents an error response
type ErrorResponse struct {
	Error   string `json:"error"`
	Message string `json:"message,omitempty"`
}

// WriteJSONResponse writes a JSON response to the HTTP writer
func WriteJSONResponse(w http.ResponseWriter, statusCode int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)

	if data != nil {
		json.NewEncoder(w).Encode(data)
	}
}

// WriteErrorResponse writes an error response to the HTTP writer
func WriteErrorResponse(w http.ResponseWriter, statusCode int, errorMsg string, details ...string) {
	response := ErrorResponse{
		Error: errorMsg,
	}

	if len(details) > 0 {
		response.Message = details[0]
	}

	WriteJSONResponse(w, statusCode, response)
}

// CreateFunctionFromRequest creates a Function from a CreateFunctionRequest
func CreateFunctionFromRequest(req *CreateFunctionRequest) Function {
	now := time.Now()

	function := Function{
		ID:              GenerateFunctionID(),
		NcaID:           GenerateNcaID(),
		VersionID:       GenerateVersionID(),
		Name:            req.Name,
		Status:          StatusInactive,
		InferenceURL:    req.InferenceURL,
		InferencePort:   req.InferencePort,
		APIBodyFormat:   "CUSTOM",
		HealthURI:       req.Health.URI,
		CreatedAt:       now,
		Description:     req.Name,
		Health:          req.Health,
		FunctionType:    FunctionTypeDefault,
		ActiveInstances: []ActiveInstance{},
	}

	// Add container-specific fields if present
	if req.ContainerImage != "" {
		function.ContainerImage = req.ContainerImage
		if req.ContainerEnvironment != nil {
			function.ContainerEnvironment = req.ContainerEnvironment
		}
	}

	// Add helm-specific fields if present
	if req.HelmChart != "" {
		function.HelmChart = req.HelmChart
		function.HelmChartServiceName = req.HelmChartServiceName
	}

	return function
}

// CreateFunctionResponseFromFunction creates a CreateFunctionResponse from a Function
func CreateFunctionResponseFromFunction(function Function) CreateFunctionResponse {
	return CreateFunctionResponse{
		Function: function,
	}
}

// GetFunctionDetailsResponseFromFunction creates a GetFunctionDetailsResponse from a Function
func GetFunctionDetailsResponseFromFunction(function Function) GetFunctionDetailsResponse {
	return GetFunctionDetailsResponse{
		Function: function,
	}
}

// GenerateActiveInstance creates a mock active instance
func GenerateActiveInstance(functionID, versionID string) ActiveInstance {
	now := time.Now()
	createdAt := now.Add(-5 * time.Minute) // Instance created 5 minutes ago

	return ActiveInstance{
		InstanceID:        GenerateInstanceID(),
		FunctionID:        functionID,
		FunctionVersionID: versionID,
		InstanceType:      "example-instance",
		InstanceStatus:    "ACTIVE",
		SisRequestID:      GenerateSisRequestID(),
		NcaID:             "example-ncaid",
		GPU:               "example-gpu",
		Backend:           "example-backend",
		Location:          "example-location",
		InstanceCreatedAt: createdAt,
		InstanceUpdatedAt: now,
	}
}

// EnhanceFunctionWithActiveInstances adds active instances to a function based on its status
func EnhanceFunctionWithActiveInstances(function Function) Function {
	// Only add active instances for ACTIVE functions
	if function.Status == StatusActive {
		// Add 1-2 active instances for ACTIVE functions
		numInstances := 1
		if uuid.New().ID()%2 == 0 { // Randomly add a second instance
			numInstances = 2
		}

		instances := make([]ActiveInstance, 0, numInstances)
		for i := 0; i < numInstances; i++ {
			instances = append(instances, GenerateActiveInstance(function.ID, function.VersionID))
		}
		function.ActiveInstances = instances
	} else {
		// Other statuses have no active instances
		function.ActiveInstances = []ActiveInstance{}
	}

	return function
}

// GenerateDeploymentID generates a new deployment ID
func GenerateDeploymentID() string {
	return uuid.New().String()
}

// GenerateRequestID generates a new request ID
func GenerateRequestID() string {
	return uuid.New().String()
}

// EnhanceDeploymentSpecification adds additional details to a deployment specification
func EnhanceDeploymentSpecification(spec DeploymentSpecification) DeploymentSpecification {
	// Add default values for enhanced specifications
	spec.PreferredOrder = 1
	spec.CPUArch = "AMD64"
	spec.OS = "Ubuntu 22.04"
	spec.DriverVersion = "570.133.11"
	spec.Storage = "175.26Gi"
	spec.SystemMemory = "28GB"

	// Set GPU memory based on GPU type
	switch spec.GPU {
	case "L40":
		spec.GPUMemory = "48GB"
	case "L40G":
		spec.GPUMemory = "24GB"
	default:
		spec.GPUMemory = "48GB"
	}

	return spec
}

// CreateDeploymentFromRequest creates a Deployment from a DeployFunctionRequest and function
func CreateDeploymentFromRequest(req *DeployFunctionRequest, function Function) Deployment {
	now := time.Now()

	// Enhance deployment specifications
	enhancedSpecs := make([]DeploymentSpecification, 0, len(req.DeploymentSpecifications))
	for _, spec := range req.DeploymentSpecifications {
		enhancedSpecs = append(enhancedSpecs, EnhanceDeploymentSpecification(spec))
	}

	deployment := Deployment{
		FunctionID:               function.ID,
		FunctionVersionID:        function.VersionID,
		DeploymentID:             GenerateDeploymentID(),
		FunctionName:             function.Name,
		NcaID:                    function.NcaID,
		FunctionStatus:           StatusDeploying,
		RequestQueueURL:          "",
		DeploymentSpecifications: enhancedSpecs,
		CreatedAt:                now,
		LastUpdatedAt:            now,
	}

	return deployment
}

// DeployFunctionResponseFromDeployment creates a DeployFunctionResponse from a Deployment
func DeployFunctionResponseFromDeployment(deployment Deployment) DeployFunctionResponse {
	return DeployFunctionResponse{
		Deployment: deployment,
	}
}
