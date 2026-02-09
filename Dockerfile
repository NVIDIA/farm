# -*- coding: utf-8 -*-

## ARGs
ARG PACKAGE_ROOT=nv/

## Stage 0: Build dashboard-ui (Node)
FROM        node:20-alpine AS dashboard-builder
WORKDIR     /app
# Install only deps first for better caching
COPY        ./dashboard-ui/package.json ./dashboard-ui/package-lock.json ./
RUN         npm ci
# Copy sources and build with workspace as CWD
COPY        ./dashboard-ui ./
RUN         npm run build

## Stage 1: Build the standalone wheel and install dependencies
FROM        python:3.12.12-slim AS python-builder
ARG         PACKAGE_ROOT=nv/
# Create temporary workspace
WORKDIR     /tmp/build/

# Install build tools first
RUN         pip install --no-cache-dir --upgrade pip poetry

# Copy dependency files first for better layer caching
COPY        ./poetry.lock ./poetry.toml ./pyproject.toml ./README.md ./

# Install dependencies (cached unless poetry.lock changes)
RUN         poetry install --without dev --no-root

# Copy source code and dashboard assets
COPY        ./${PACKAGE_ROOT} ./${PACKAGE_ROOT}
COPY        --from=dashboard-builder /app/dist/ /tmp/build/nv/svc/farm/services/dashboard/build/

# Build and install the wheel
RUN         poetry install --without dev && \
            poetry build -f wheel && \
            pip install --no-cache-dir dist/*.whl

# Stage 2: Final image
FROM        python:3.12.12-slim

LABEL       MAINTAINER="nvidia"

# Create non-root user
RUN         groupadd --gid 1000 farm && \
            useradd --uid 1000 --gid farm --shell /bin/bash --create-home farm

# Copy the installed packages from python-builder
COPY        --from=python-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Switch to non-root user
USER        farm

# Use the correct entry point
ENTRYPOINT  ["python3", "-m", "nv.svc.farm.standalone"]
