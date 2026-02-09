// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

package main

import (
	"fmt"
	"net/url"
	"strings"
)

// ValidationError represents a validation error
type ValidationError struct {
	Field   string `json:"field"`
	Message string `json:"message"`
}

// ValidationErrors represents multiple validation errors
type ValidationErrors struct {
	Errors []ValidationError `json:"errors"`
}

// ValidateCreateFunctionRequest validates a function creation request
func ValidateCreateFunctionRequest(req *CreateFunctionRequest) *ValidationErrors {
	var errors []ValidationError

	// Validate name
	if req.Name == "" {
		errors = append(errors, ValidationError{
			Field:   "name",
			Message: "name is required",
		})
	}

	// Validate health configuration
	if req.Health.URI == "" {
		errors = append(errors, ValidationError{
			Field:   "health.uri",
			Message: "health URI is required",
		})
	}

	if req.Health.Port <= 0 || req.Health.Port > 65535 {
		errors = append(errors, ValidationError{
			Field:   "health.port",
			Message: "health port must be between 1 and 65535",
		})
	}

	if req.Health.Protocol == "" {
		errors = append(errors, ValidationError{
			Field:   "health.protocol",
			Message: "health protocol is required",
		})
	}

	if req.Health.ExpectedStatusCode <= 0 {
		errors = append(errors, ValidationError{
			Field:   "health.expectedStatusCode",
			Message: "health expected status code must be positive",
		})
	}

	// Validate inference configuration
	if req.InferenceURL == "" {
		errors = append(errors, ValidationError{
			Field:   "inferenceUrl",
			Message: "inference URL is required",
		})
	}

	if req.InferencePort <= 0 || req.InferencePort > 65535 {
		errors = append(errors, ValidationError{
			Field:   "inferencePort",
			Message: "inference port must be between 1 and 65535",
		})
	}

	// Validate that either container or helm configuration is provided
	hasContainer := req.ContainerImage != ""
	hasHelm := req.HelmChart != ""

	if !hasContainer && !hasHelm {
		errors = append(errors, ValidationError{
			Field:   "containerImage/helmChart",
			Message: "either containerImage or helmChart must be provided",
		})
	}

	if hasContainer && hasHelm {
		errors = append(errors, ValidationError{
			Field:   "containerImage/helmChart",
			Message: "cannot provide both containerImage and helmChart",
		})
	}

	// Validate container image format if provided
	if hasContainer {
		if !strings.Contains(req.ContainerImage, "/") {
			errors = append(errors, ValidationError{
				Field:   "containerImage",
				Message: "container image must be in format registry/repository:tag",
			})
		}
	}

	// Validate helm chart URL if provided
	if hasHelm {
		if _, err := url.Parse(req.HelmChart); err != nil {
			errors = append(errors, ValidationError{
				Field:   "helmChart",
				Message: "helm chart must be a valid URL",
			})
		}

		if req.HelmChartServiceName == "" {
			errors = append(errors, ValidationError{
				Field:   "helmChartServiceName",
				Message: "helm chart service name is required when using helm chart",
			})
		}
	}

	if len(errors) > 0 {
		return &ValidationErrors{Errors: errors}
	}

	return nil
}

// ValidateDeployFunctionRequest validates a DeployFunctionRequest
func ValidateDeployFunctionRequest(req *DeployFunctionRequest) *ValidationErrors {
	var errors []ValidationError

	// Check if deployment specifications are provided
	if len(req.DeploymentSpecifications) == 0 {
		errors = append(errors, ValidationError{
			Field:   "deploymentSpecifications",
			Message: "at least one deployment specification is required",
		})
	}

	// Validate each deployment specification
	for i, spec := range req.DeploymentSpecifications {
		prefix := fmt.Sprintf("deploymentSpecifications[%d]", i)

		if spec.InstanceType == "" {
			errors = append(errors, ValidationError{
				Field:   prefix + ".instanceType",
				Message: "instance type is required",
			})
		}

		if spec.GPU == "" {
			errors = append(errors, ValidationError{
				Field:   prefix + ".gpu",
				Message: "GPU is required",
			})
		}

		if spec.MaxInstances <= 0 {
			errors = append(errors, ValidationError{
				Field:   prefix + ".maxInstances",
				Message: "max instances must be greater than 0",
			})
		}

		if spec.MinInstances <= 0 {
			errors = append(errors, ValidationError{
				Field:   prefix + ".minInstances",
				Message: "min instances must be greater than 0",
			})
		}

		if spec.MaxRequestConcurrency <= 0 {
			errors = append(errors, ValidationError{
				Field:   prefix + ".maxRequestConcurrency",
				Message: "max request concurrency must be greater than 0",
			})
		}

		// Check that min instances <= max instances
		if spec.MinInstances > spec.MaxInstances {
			errors = append(errors, ValidationError{
				Field:   prefix + ".minInstances",
				Message: "min instances cannot be greater than max instances",
			})
		}
	}

	if len(errors) > 0 {
		return &ValidationErrors{Errors: errors}
	}

	return nil
}

// FormatValidationErrors formats validation errors for HTTP response
func FormatValidationErrors(errors *ValidationErrors) string {
	if errors == nil || len(errors.Errors) == 0 {
		return ""
	}

	var messages []string
	for _, err := range errors.Errors {
		messages = append(messages, fmt.Sprintf("%s: %s", err.Field, err.Message))
	}

	return strings.Join(messages, "; ")
}
