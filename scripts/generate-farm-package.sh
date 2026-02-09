#!/bin/bash

set -euo pipefail

rm -rf farm-install/ dist/

mkdir farm-install

poetry build --format=wheel --output=farm-install --no-interaction

poetry self add poetry-plugin-export

poetry export --format=requirements.txt --output=requirements.txt --without-hashes

pip download --dest ./farm-install/dependencies/ -r requirements.txt

tar -czf farm-package.tar.gz farm-install/
