// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

package main

import (
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"strings"
	"time"
)

// FunctionRouter handles routing for function endpoints
func FunctionRouter(w http.ResponseWriter, r *http.Request) {
	path := r.URL.Path

	// Check if it's a version-specific request
	if strings.Contains(path, "/versions/") {
		if r.Method == "DELETE" {
			DeleteFunctionHandler(w, r)
			return
		}
		GetFunctionDetailsHandler(w, r)
		return
	}

	// Check if it's a GET request to /functions (list functions)
	if r.Method == "GET" && (path == "/functions" || strings.HasPrefix(path, "/functions?")) {
		ListFunctionsHandler(w, r)
		return
	}

	// Otherwise, it's a regular function request (GET /functions/{id})
	GetFunctionHandler(w, r)
}

func main() {
	// Initialize the function store
	InitFunctionStore()

	// Initialize random seed for status updates
	rand.Seed(time.Now().UnixNano())

	// Define the port
	port := ":8877"

	// Register handlers
	http.HandleFunc("/hello", HelloHandler)
	http.HandleFunc("/health", HealthHandler)
	http.HandleFunc("/functions", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "POST" {
			CreateFunctionHandler(w, r)
		} else if r.Method == "GET" {
			ListFunctionsHandler(w, r)
		} else {
			WriteErrorResponse(w, http.StatusMethodNotAllowed, "Method not allowed")
		}
	})
	http.HandleFunc("/functions/", FunctionRouter) // GET /functions/{id}, GET /functions/{id}/versions/{versionId}
	http.HandleFunc("/deployments/", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "POST" {
			DeployFunctionHandler(w, r)
		} else if r.Method == "DELETE" {
			DeleteDeploymentHandler(w, r)
		} else {
			WriteErrorResponse(w, http.StatusMethodNotAllowed, "Method not allowed")
		}
	}) // POST /deployments/functions/{functionId}/versions/{versionId}, DELETE /deployments/functions/{functionId}/versions/{versionId}

	// Start the server
	fmt.Printf("Server starting on port %s\n", port)
	fmt.Printf("Available endpoints:\n")
	fmt.Printf("  GET  /hello                                    - Hello world endpoint\n")
	fmt.Printf("  GET  /health                                   - Health check\n")
	fmt.Printf("  POST /functions                                - Create function (requires Bearer token)\n")
	fmt.Printf("  GET  /functions                                - List all functions (requires Bearer token)\n")
	fmt.Printf("  GET  /functions/{id}                          - Get function by ID (requires Bearer token)\n")
	fmt.Printf("  GET  /functions/{id}/versions/{versionId}     - Get function details (requires Bearer token)\n")
	fmt.Printf("  DELETE /functions/{id}/versions/{versionId}   - Delete function permanently (requires Bearer token)\n")
	fmt.Printf("  POST /deployments/functions/{id}/versions/{versionId} - Deploy function (requires Bearer token)\n")
	fmt.Printf("  DELETE /deployments/functions/{id}/versions/{versionId} - Deactivate function (requires Bearer token)\n")
	fmt.Printf("\nExample create function request:\n")
	fmt.Printf("  curl -X POST http://localhost%s/functions \\\n", port)
	fmt.Printf("    -H \"Authorization: Bearer your-token\" \\\n")
	fmt.Printf("    -H \"Content-Type: application/json\" \\\n")
	fmt.Printf("    -d '{\"name\":\"test-function\",\"tags\":[],\"health\":{\"uri\":\"/health\",\"port\":8000,\"protocol\":\"HTTP\",\"expectedStatusCode\":200,\"timeout\":\"PT10S\"},\"inferenceUrl\":\"/echo\",\"inferencePort\":8000,\"containerImage\":\"...\"}'\n")

	log.Fatal(http.ListenAndServe(port, nil))
}
