// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

package main

import (
	"encoding/json"
	"fmt"
	"io"
	"math/rand"
	"net/http"
	"strings"
	"time"
)

// Global function store
var functionStore *FunctionStore

// InitFunctionStore initializes the global function store
func InitFunctionStore() {
	functionStore = NewFunctionStore()
}

// HelloHandler handles GET /hello requests
func HelloHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello, World!")
}

// HealthHandler handles GET /health requests
func HealthHandler(w http.ResponseWriter, r *http.Request) {
	response := struct {
		Status    string `json:"status"`
		Timestamp string `json:"timestamp"`
		Service   string `json:"service"`
	}{
		Status:    "healthy",
		Timestamp: fmt.Sprintf("%d", time.Now().Unix()),
		Service:   "nvcf-mock-service",
	}

	WriteJSONResponse(w, http.StatusOK, response)
}

// CreateFunctionHandler handles POST /functions requests
func CreateFunctionHandler(w http.ResponseWriter, r *http.Request) {
	// Check authorization
	authHeader := r.Header.Get("Authorization")
	if authHeader == "" {
		WriteErrorResponse(w, http.StatusUnauthorized, "Missing authorization header")
		return
	}

	if !strings.HasPrefix(authHeader, "Bearer ") {
		WriteErrorResponse(w, http.StatusUnauthorized, "Invalid authorization format")
		return
	}

	// Extract and validate token
	token := strings.TrimPrefix(authHeader, "Bearer ")
	if token == "" {
		WriteErrorResponse(w, http.StatusUnauthorized, "Empty bearer token")
		return
	}

	// Check content type
	contentType := r.Header.Get("Content-Type")
	if contentType != "application/json" {
		WriteErrorResponse(w, http.StatusBadRequest, "Content-Type must be application/json")
		return
	}

	// Read request body
	body, err := io.ReadAll(r.Body)
	if err != nil {
		WriteErrorResponse(w, http.StatusBadRequest, "Failed to read request body")
		return
	}
	defer r.Body.Close()

	// Parse request
	var req CreateFunctionRequest
	if err := json.Unmarshal(body, &req); err != nil {
		WriteErrorResponse(w, http.StatusBadRequest, "Invalid JSON in request body")
		return
	}

	// Validate request
	if validationErrors := ValidateCreateFunctionRequest(&req); validationErrors != nil {
		errorMsg := FormatValidationErrors(validationErrors)
		WriteErrorResponse(w, http.StatusBadRequest, "Validation failed", errorMsg)
		return
	}

	// Create function from request
	function := CreateFunctionFromRequest(&req)

	// Store the function
	functionStore.CreateFunction(function)

	// Create response
	response := CreateFunctionResponseFromFunction(function)

	// Return success response
	WriteJSONResponse(w, http.StatusCreated, response)
}

// GetFunctionHandler handles GET /functions/{id} requests
func GetFunctionHandler(w http.ResponseWriter, r *http.Request) {
	// Check authorization
	authHeader := r.Header.Get("Authorization")
	if authHeader == "" {
		WriteErrorResponse(w, http.StatusUnauthorized, "Missing authorization header")
		return
	}

	if !strings.HasPrefix(authHeader, "Bearer ") {
		WriteErrorResponse(w, http.StatusUnauthorized, "Invalid authorization format")
		return
	}

	// Extract and validate token
	token := strings.TrimPrefix(authHeader, "Bearer ")
	if token == "" {
		WriteErrorResponse(w, http.StatusUnauthorized, "Empty bearer token")
		return
	}

	// Extract function ID from URL path
	path := r.URL.Path
	if len(path) < 11 { // "/functions/" is 11 characters
		WriteErrorResponse(w, http.StatusBadRequest, "Invalid function ID")
		return
	}

	functionID := path[11:] // Remove "/functions/" prefix
	if functionID == "" {
		WriteErrorResponse(w, http.StatusBadRequest, "Function ID is required")
		return
	}

	// Get function from store
	function, exists := functionStore.GetFunction(functionID)
	if !exists {
		WriteErrorResponse(w, http.StatusNotFound, "Function not found")
		return
	}

	// Enhance function with active instances
	enhancedFunction := EnhanceFunctionWithActiveInstances(function)

	// Return function
	WriteJSONResponse(w, http.StatusOK, GetFunctionDetailsResponseFromFunction(enhancedFunction))
}

// GetFunctionDetailsHandler handles GET /functions/{id}/versions/{versionId} requests
func GetFunctionDetailsHandler(w http.ResponseWriter, r *http.Request) {
	// Check authorization
	authHeader := r.Header.Get("Authorization")
	if authHeader == "" {
		WriteErrorResponse(w, http.StatusUnauthorized, "Missing authorization header")
		return
	}

	if !strings.HasPrefix(authHeader, "Bearer ") {
		WriteErrorResponse(w, http.StatusUnauthorized, "Invalid authorization format")
		return
	}

	// Extract and validate token
	token := strings.TrimPrefix(authHeader, "Bearer ")
	if token == "" {
		WriteErrorResponse(w, http.StatusUnauthorized, "Empty bearer token")
		return
	}

	// Parse URL path: /functions/{functionId}/versions/{versionId}
	path := r.URL.Path
	pathParts := strings.Split(strings.TrimPrefix(path, "/"), "/")

	if len(pathParts) != 4 || pathParts[0] != "functions" || pathParts[2] != "versions" {
		WriteErrorResponse(w, http.StatusBadRequest, "Invalid URL format. Expected: /functions/{functionId}/versions/{versionId}")
		return
	}

	functionID := pathParts[1]
	versionID := pathParts[3]

	if functionID == "" {
		WriteErrorResponse(w, http.StatusBadRequest, "Function ID is required")
		return
	}

	if versionID == "" {
		WriteErrorResponse(w, http.StatusBadRequest, "Version ID is required")
		return
	}

	// Get function from store
	function, exists := functionStore.GetFunction(functionID)
	if !exists {
		WriteErrorResponse(w, http.StatusNotFound, "Function not found")
		return
	}

	// Check if version ID matches (in a real implementation, you might have multiple versions)
	if function.VersionID != versionID {
		WriteErrorResponse(w, http.StatusNotFound, "Version not found")
		return
	}

	// Enhance function with active instances
	enhancedFunction := EnhanceFunctionWithActiveInstances(function)

	// Return function details
	WriteJSONResponse(w, http.StatusOK, GetFunctionDetailsResponseFromFunction(enhancedFunction))
}

func ListFunctionsHandler(w http.ResponseWriter, r *http.Request) {
	// Check authorization
	authHeader := r.Header.Get("Authorization")
	if authHeader == "" {
		WriteErrorResponse(w, http.StatusUnauthorized, "Missing authorization header")
		return
	}

	if !strings.HasPrefix(authHeader, "Bearer ") {
		WriteErrorResponse(w, http.StatusUnauthorized, "Invalid authorization format")
		return
	}

	// Extract and validate token
	token := strings.TrimPrefix(authHeader, "Bearer ")
	if token == "" {
		WriteErrorResponse(w, http.StatusUnauthorized, "Empty bearer token")
		return
	}

	// Get query parameters
	visibility := r.URL.Query().Get("visibility")

	// For now, we'll accept any visibility value (private, public, etc.)
	// In a real implementation, you might filter based on visibility
	if visibility == "" {
		visibility = "private" // default to private
	}

	// Get all functions from store
	allFunctions := functionStore.GetAllFunctions()

	// Process functions and potentially update DEPLOYING status to ACTIVE
	enhancedFunctions := make([]Function, 0, len(allFunctions))
	for _, function := range allFunctions {
		// Check if function is in DEPLOYING status and randomly update to ACTIVE
		if function.Status == StatusDeploying {
			// 25% chance to update to ACTIVE
			if rand.Float32() < 0.25 {
				function.Status = StatusActive
				// Update the function in the store
				functionStore.CreateFunction(function)
			}
		}

		enhancedFunction := EnhanceFunctionWithActiveInstances(function)
		enhancedFunctions = append(enhancedFunctions, enhancedFunction)
	}

	// Create response with functions array
	response := struct {
		Functions []Function `json:"functions"`
	}{
		Functions: enhancedFunctions,
	}

	WriteJSONResponse(w, http.StatusOK, response)
}

// DeployFunctionHandler handles POST /deployments/functions/{functionId}/versions/{versionId} requests
func DeployFunctionHandler(w http.ResponseWriter, r *http.Request) {
	// Check authorization
	authHeader := r.Header.Get("Authorization")
	if authHeader == "" {
		WriteErrorResponse(w, http.StatusUnauthorized, "Missing authorization header")
		return
	}

	if !strings.HasPrefix(authHeader, "Bearer ") {
		WriteErrorResponse(w, http.StatusUnauthorized, "Invalid authorization format")
		return
	}

	// Extract and validate token
	token := strings.TrimPrefix(authHeader, "Bearer ")
	if token == "" {
		WriteErrorResponse(w, http.StatusUnauthorized, "Empty bearer token")
		return
	}

	// Check content type
	contentType := r.Header.Get("Content-Type")
	if contentType != "application/json" {
		WriteErrorResponse(w, http.StatusBadRequest, "Content-Type must be application/json")
		return
	}

	// Parse URL path: /deployments/functions/{functionId}/versions/{versionId}
	path := r.URL.Path
	pathParts := strings.Split(strings.TrimPrefix(path, "/"), "/")

	if len(pathParts) != 5 || pathParts[0] != "deployments" || pathParts[1] != "functions" || pathParts[3] != "versions" {
		WriteErrorResponse(w, http.StatusBadRequest, "Invalid URL format. Expected: /deployments/functions/{functionId}/versions/{versionId}")
		return
	}

	functionID := pathParts[2]
	versionID := pathParts[4]

	if functionID == "" {
		WriteErrorResponse(w, http.StatusBadRequest, "Function ID is required")
		return
	}

	if versionID == "" {
		WriteErrorResponse(w, http.StatusBadRequest, "Version ID is required")
		return
	}

	// Get function from store
	function, exists := functionStore.GetFunction(functionID)
	if !exists {
		WriteErrorResponse(w, http.StatusNotFound, "Function not found")
		return
	}

	// Check if version ID matches
	if function.VersionID != versionID {
		WriteErrorResponse(w, http.StatusNotFound, "Version not found")
		return
	}

	// Check if function is already deploying
	if function.Status == StatusDeploying {
		WriteErrorResponse(w, http.StatusBadRequest, "Function is already deploying")
		return
	}

	// Read request body
	body, err := io.ReadAll(r.Body)
	if err != nil {
		WriteErrorResponse(w, http.StatusBadRequest, "Failed to read request body")
		return
	}
	defer r.Body.Close()

	// Parse request
	var req DeployFunctionRequest
	if err := json.Unmarshal(body, &req); err != nil {
		WriteErrorResponse(w, http.StatusBadRequest, "Invalid JSON in request body")
		return
	}

	// Validate request
	if validationErrors := ValidateDeployFunctionRequest(&req); validationErrors != nil {
		errorMsg := FormatValidationErrors(validationErrors)
		WriteErrorResponse(w, http.StatusBadRequest, "Validation failed", errorMsg)
		return
	}

	// Create deployment from request
	deployment := CreateDeploymentFromRequest(&req, function)

	// Update function status to deploying
	function.Status = StatusDeploying
	functionStore.CreateFunction(function) // Update the function in store

	// Create response
	response := DeployFunctionResponseFromDeployment(deployment)

	// Return success response
	WriteJSONResponse(w, http.StatusCreated, response)
}

// DeleteDeploymentHandler handles DELETE /deployments/functions/{functionId}/versions/{versionId} requests
func DeleteDeploymentHandler(w http.ResponseWriter, r *http.Request) {
	// Check authorization
	authHeader := r.Header.Get("Authorization")
	if authHeader == "" {
		WriteErrorResponse(w, http.StatusUnauthorized, "Missing authorization header")
		return
	}

	if !strings.HasPrefix(authHeader, "Bearer ") {
		WriteErrorResponse(w, http.StatusUnauthorized, "Invalid authorization format")
		return
	}

	// Extract and validate token
	token := strings.TrimPrefix(authHeader, "Bearer ")
	if token == "" {
		WriteErrorResponse(w, http.StatusUnauthorized, "Empty bearer token")
		return
	}

	// Parse URL path: /deployments/functions/{functionId}/versions/{versionId}
	path := r.URL.Path
	pathParts := strings.Split(strings.TrimPrefix(path, "/"), "/")

	if len(pathParts) != 5 || pathParts[0] != "deployments" || pathParts[1] != "functions" || pathParts[3] != "versions" {
		WriteErrorResponse(w, http.StatusBadRequest, "Invalid URL format. Expected: /deployments/functions/{functionId}/versions/{versionId}")
		return
	}

	functionID := pathParts[2]
	versionID := pathParts[4]

	if functionID == "" {
		WriteErrorResponse(w, http.StatusBadRequest, "Function ID is required")
		return
	}

	if versionID == "" {
		WriteErrorResponse(w, http.StatusBadRequest, "Version ID is required")
		return
	}

	// Get function from store
	function, exists := functionStore.GetFunction(functionID)
	if !exists {
		WriteErrorResponse(w, http.StatusNotFound, "Function not found")
		return
	}

	// Check if version ID matches
	if function.VersionID != versionID {
		WriteErrorResponse(w, http.StatusNotFound, "Version not found")
		return
	}

	// Update function status to INACTIVE (graceful deletion)
	function.Status = StatusInactive
	functionStore.CreateFunction(function) // Update the function in store

	// Create response with updated function
	response := struct {
		Function Function `json:"function"`
	}{
		Function: function,
	}

	// Return success response
	WriteJSONResponse(w, http.StatusOK, response)
}

// DeleteFunctionHandler handles DELETE /functions/{functionId}/versions/{versionId} requests
func DeleteFunctionHandler(w http.ResponseWriter, r *http.Request) {
	// Check authorization
	authHeader := r.Header.Get("Authorization")
	if authHeader == "" {
		WriteErrorResponse(w, http.StatusUnauthorized, "Missing authorization header")
		return
	}

	if !strings.HasPrefix(authHeader, "Bearer ") {
		WriteErrorResponse(w, http.StatusUnauthorized, "Invalid authorization format")
		return
	}

	// Extract and validate token
	token := strings.TrimPrefix(authHeader, "Bearer ")
	if token == "" {
		WriteErrorResponse(w, http.StatusUnauthorized, "Empty bearer token")
		return
	}

	// Parse URL path: /functions/{functionId}/versions/{versionId}
	path := r.URL.Path
	pathParts := strings.Split(strings.TrimPrefix(path, "/"), "/")

	if len(pathParts) != 4 || pathParts[0] != "functions" || pathParts[2] != "versions" {
		WriteErrorResponse(w, http.StatusBadRequest, "Invalid URL format. Expected: /functions/{functionId}/versions/{versionId}")
		return
	}

	functionID := pathParts[1]
	versionID := pathParts[3]

	if functionID == "" {
		WriteErrorResponse(w, http.StatusBadRequest, "Function ID is required")
		return
	}

	if versionID == "" {
		WriteErrorResponse(w, http.StatusBadRequest, "Version ID is required")
		return
	}

	// Get function from store
	function, exists := functionStore.GetFunction(functionID)
	if !exists {
		// Return 404 with ProblemDetails format
		problemDetails := ProblemDetails{
			Type:     "urn:kaizen:problem-details:not-found",
			Title:    "Not Found",
			Status:   404,
			Detail:   fmt.Sprintf("Function id '%s': Version '%s' not found", functionID, versionID),
			Instance: r.URL.Path,
		}
		WriteJSONResponse(w, http.StatusNotFound, problemDetails)
		return
	}

	// Check if version ID matches
	if function.VersionID != versionID {
		// Return 404 with ProblemDetails format
		problemDetails := ProblemDetails{
			Type:     "urn:kaizen:problem-details:not-found",
			Title:    "Not Found",
			Status:   404,
			Detail:   fmt.Sprintf("Function id '%s': Version '%s' not found", functionID, versionID),
			Instance: r.URL.Path,
		}
		WriteJSONResponse(w, http.StatusNotFound, problemDetails)
		return
	}

	// Delete the function from store
	deleted := functionStore.DeleteFunction(functionID)
	if !deleted {
		WriteErrorResponse(w, http.StatusInternalServerError, "Failed to delete function")
		return
	}

	// Return null response on successful deletion (matching real API behavior)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("null"))
}
