#!/bin/bash
set -euo pipefail

DIST_DIR="dashboard-ui/dist"

# If dist directory is missing OR empty, run the build
if [[ ! -d "$DIST_DIR" || -z "$(ls -A "$DIST_DIR" 2>/dev/null)" ]]; then
    echo "dist directory missing or empty — building dashboard-ui..."
    (
        npm --prefix ./dashboard-ui ci
        npm --prefix ./dashboard-ui run build
    )
else
    echo "dist directory exists and is not empty — skipping build."
fi

# Resolve destination directory
TARGET_DIR="$(realpath "./nv/svc/farm/services/dashboard/build")"

# Ensure destination exists
mkdir -p "$TARGET_DIR"

# Copy all built assets (including dotfiles), preserving attributes
cp -a "$DIST_DIR/." "$TARGET_DIR"/

# Show results
ls -la "$TARGET_DIR"
