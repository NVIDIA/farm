#!/bin/bash

set -euo pipefail

VERSION=$(poetry version -s)

# Convert array to space-separated string
FILENAMES_STR="${FILENAMES[*]}"
FILENAMES=($FILENAMES_STR)

for FILENAME in "${FILENAMES[@]}"; do

    echo "Publishing $FILENAME"

    if [[ "$FILENAME" == *.tar.gz ]]; then
        SUFFIXED_EXT="-linux_x86_64.tar.gz"
    elif [[ "$FILENAME" == *.zip ]]; then
        SUFFIXED_EXT="-windows_x86_64.zip"
    fi

    # Calculate checksums and store them in variables
    SHA1=$(sha1sum $FILENAME | awk '{ print $1 }')
    SHA256=$(sha256sum $FILENAME | awk '{ print $1 }')
    MD5=$(md5sum $FILENAME | awk '{ print $1 }')

    UPLOAD_FILENAME="nv-svc-farm@$VERSION-offline-wheels$SUFFIXED_EXT"

    # Use the variables in the curl request
    curl -v -f -X PUT \
        -T $FILENAME \
        -H "X-JFrog-Art-Api: $ARTIFACTORY_KEY" \
        -H "X-Checksum-Sha256: $SHA256" \
        -H "X-Checksum-Sha1: $SHA1" \
        -H "X-Checksum-Md5: $MD5" \
        -H "Content-Type: application/octet-stream" \
        "https://urm.nvidia.com/artifactory/ct-omniverse-generic/pkgs/farm/$UPLOAD_FILENAME"

done
