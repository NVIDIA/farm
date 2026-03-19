#!/usr/bin/env sh
set -e
set -u

echo "Starting job definition load script."

echo "JOBS_API_URL: ${JOBS_API_URL}"
echo "JOB_DEFINITIONS_DIR: ${JOB_DEFINITIONS_DIR}"

echo "\nlisting all files under ${JOB_DEFINITIONS_DIR}\n"
ls -la "${JOB_DEFINITIONS_DIR}"

# Use a while loop instead of an array for portability
find "${JOB_DEFINITIONS_DIR}" -type f -name "*.json" | while IFS= read -r file; do
    echo "\n--\nuploading job definition: ${file}\n$(cat "$file")\n"

    wget --quiet --output-document=/tmp/http_response --server-response \
        --header="accept: application/json" \
        --header="Content-Type: application/json" \
        --header="X-API-KEY: ${JOBS_API_KEY}" \
        --post-file="$file" \
        "${JOBS_API_URL}/save"

    echo "response:\n$(cat /tmp/http_response)"
done

echo "\n--\nchecking job definitions: ${JOBS_API_URL}/load"

wget --quiet --output-document=/tmp/http_response --server-response \
    --header="accept: application/json" \
    --header="Content-Type: application/json" \
    "${JOBS_API_URL}/load"

echo "response:\n$(cat /tmp/http_response)"

echo "\n\nDone."
