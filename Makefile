.DEFAULT_GOAL := build
.PHONY: build publish package coverage test lint docs venv quicktest freeze clean docs check-format fix-format ui ui-clean e2e-up e2e-down e2e-test
DEFAULT_PY_VERSION = 310

SHELL = bash


# Pin dependencies
freeze:
	tox -e deps.freeze

# Run linters
lint:
	tox -e linters

# Run linters and unit tests against all python versions
test: ui-clean lint
	tox

# Run unit tests against default python version
quicktest: ui-clean
	tox -e py${DEFAULT_PY_VERSION}

# Generate code coverage report
coverage-report:
	tox --recreate -e coverage-report
	@echo -e "\n\nNavigate to HTML coverage report  file://${PWD}/htmlcov/index.html" ;

# Clean up temporary files, coverage reports and virtual environments
clean: ui-clean
	tox -e coverage-erase
	rm -rf .tox .venv dist htmlcov .coverage.*

# Build the package sdist and wheel
build: clean ui
	tox -e build

# Call the UI script
ui:
	./scripts/install-dashboard.sh

# Remove ui build directory
ui-clean:
	rm -rf ./nv/svc/farm/services/dashboard/build

# Start application
start:
	tox -e start -- ${svc}

# Publish to PyPi
publish: build
	tox -e publish

# Generate docs
docs:
	tox --recreate -e docs
	@echo -e "\n\nNavigate to documentation file://${PWD}/.tox/docs/tmp/html/index.html" ;

# Start live docs server
docs-server:
	tox -e docs-server

# Check code formatting using Black and module imports using Isort
# refer to pyproject.toml for tool.black and tool.isort settings.
check-format:
	tox -e check-format

# Inplace code format fix
fix-format:
	tox -e fix-format

# Helper entrypoint for local development
venv:
	tox -e py${DEFAULT_PY_VERSION}
	@echo -e "\n\nPlease run the following command to work in the new virtual environment:" ; \
	echo -e "\n  source .tox/py${DEFAULT_PY_VERSION}/bin/activate\n"

# E2E testing
e2e-up:
	docker compose up --build -d
	@echo "Waiting for services to be healthy..."
	@sleep 5
	@for i in 1 2 3 4 5 6; do \
		docker compose exec -T farm python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8222/health')" >/dev/null 2>&1 && break || \
		(echo "Attempt $$i/6 failed, retrying in 5 sec..." && sleep 5); \
	done
	@echo "Farm is running at http://localhost:8222"
	@echo "Dashboard at http://localhost:8222/queue/management/dashboard/"

e2e-down:
	docker compose down

e2e-test:
	@if [ -f "${HOME}/.nvm/nvm.sh" ]; then . "${HOME}/.nvm/nvm.sh"; fi && cd dashboard-ui && npx playwright install chromium && npx playwright test
