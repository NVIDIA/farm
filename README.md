# Getting started
## Prerequisites

This project uses **[Python](https://www.python.org/)** minimum version 3.12, **[Poetry](https://python-poetry.org/)** to manage dependencies and **[Tox](https://tox.wiki/en/stable/)** to automate and standardize testing across multiple versions of Python.

| Requirement | Description | Installation |
------------- | ----------- | ------------ |
| [Python 3.12+](https://www.python.org/) | Interpreter | [Ubuntu](https://phoenixnap.com/kb/how-to-install-python-3-ubuntu) |
| [Poetry](https://python-poetry.org/docs/) | Dependency Management / Packaging | [Pip](https://python-poetry.org/docs/#installation) |
| [Tox](https://tox.wiki/en/latest/index.html) | Standardize testing across multiple Python versions | [Pip](https://tox.wiki/en/latest/installation.html#via-pip) |
| [Make]() | Entrypoints to commands | |

## Quickstart
- Clone this repository using `git clone`
- From within the repository folder, create a virtual environment `make venv`. Note: if this command is not run before opening VS Code, VS Code will not be able to find your virtual environment and you may have to re-open it.
- Open VSCode `code .`

## Development
It is recommended that most development related commands be executed through `make` commands. This allows the CI system to use an interface rather than an implementation. For example, `make test` will internally call a `tox` target which knows how to run tests on your project allowing us to change how we run tests without modifying CI.

Most `make` targets call `tox` commands which create and maintain a virtual environment, install required dependencies and optionally install your package. This is the recommended way to do your development as it allows the tooling to do most of the work.

### Exploring Make Targets

The following is a list of commonly used `make` targets. To see the entire list refer to the `Makefile` at the root of your repository. Keep in mind that `tox` will create and manage its own virtual environment for you.

| Command           | Action                                                 |
| :---------------- | :----------------------------------------------------- |
| `start`           | Starts the application locally                         |
| `quicktest`       | Runs available testcases                               |
| `build`           | Builds Python wheel                                    |
| `clean`           | Cleans workspace / venvs                               |
| `coverage-report` | Generates a code coverage report                       |
| `docs`            | Generates documenation site                            |
| `docs-server`     | Starts a live server, previewing your docs in realtime |
| `check-format`    | Checks the format of your code                         |
| `fix-format`      | Rectifies the output of `check-format`                 |
| `e2e-up`          | Starts E2E test environment (Docker Compose)           |
| `e2e-test`        | Runs Playwright E2E tests                              |
| `e2e-down`        | Stops E2E test environment                             |

## Exploring pyproject.toml
This file contains all configuration necessary for use with packaging tools, in our case `poetry`. To see more on what this file may contain consult the [packaging guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/).

## Dependency Manipulation
The `pyproject.toml` file contains all of your projects dependencies logically grouped.
- `tool.poetry.dependencies` - dependencies to be included for your final artifact
- `tool.poetry.group.dev.dependencies` - dependencies included for development purposes only (flake8, pylint, etc)
- `tool.poetry.group.docs.dependencies` - dependencies included for generating documentation

### Adding Dependencies
Add a dependency to a group: `poetry add mdx-include --group docs`

### Removing Dependencies
Remove a dependency from a group: `poetry remove markdown-callouts --group docs`

### Updating Dependencies
Update all dependencies: `poetry update`

## Testing
We use [pytest](https://docs.pytest.org/en/8.0.x/) to run test-cases which are located in the `tests` folder at the root of the project.

### Running Tests
`make quicktest` - Creates an environment using tox, installs tests dependencies, installs your package and runs through your test-cases. Keep in mind you can still use `unittest` but some features may not be [compatible](https://docs.pytest.org/en/7.1.x/how-to/unittest.html).

## E2E Testing

End-to-end tests use [Playwright](https://playwright.dev/) to test the full application stack including the dashboard UI.

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for running Playwright locally)

### Running E2E Tests

```bash
# Start the E2E environment (Farm + MySQL in Docker)
make e2e-up

# Run Playwright tests
make e2e-test

# Stop the environment when done
make e2e-down
```

The E2E environment runs:
- **Farm** service on `http://localhost:8222`
- **Dashboard** at `http://localhost:8222/queue/management/dashboard/`
- **MySQL** database on port 3306

### Writing E2E Tests

E2E tests are located in `dashboard-ui/e2e/`. To add new tests:

1. Create a new `.spec.ts` file in `dashboard-ui/e2e/`
2. Use Playwright's test API to interact with the dashboard
3. Run `make e2e-test` to verify

Example test structure:
```typescript
import { test, expect } from "@playwright/test";

test("can perform action", async ({ page }) => {
    await page.goto("/queue/management/dashboard/");
    // ... test steps
});
```

### Debugging E2E Tests

Run Playwright in headed mode to see the browser:
```bash
cd dashboard-ui && npx playwright test --headed
```

Run a specific test file:
```bash
cd dashboard-ui && npx playwright test e2e/login.spec.ts
```

## Starting the Application
It is recommended to start your application using `make start` or by using the pre-configured launch configuration found in `./vscode/launch.json` See [Debugging with VSCode](https://code.visualstudio.com/docs/editor/debugging) for more information.

## Accessing OpenAPI Spec
With your application running using `make start` or otherwise, the OpenAPI Spec can be found by navigating to the `/docs` endpoint. For example `http://localhost:8222/docs`

## Building the Container Image
The `Dockerfile` used to build the image is located at the project's root. You can build an image using the command `docker build . -t "your-image-name:your-version"` and you can run this image by using the command `docker run -p 8222:8222 "your-image-name:your-version"`

## Versioning
The `pyproject.toml` contains all the necessary information to build your Python artifact along with its version. This version should be updated each time you wish to merge into your main branch. The build system will build, package, push, and tag your repository with this version.

## Documentation
This project is configured to produce documentation using `mkdocs` which will traverse your docstrings and generate a static HTML site.
- Start a live docs server `make docs-server` - This starts a webserver that live updates on changes in your repository for preview
- Generate static site `make docs` - This produces the static site

## VSCode
All VSCode configuration can be found in the `.vscode` directory at the root of the application. Here you can find settings, launch configurations for debugging and recommended extensions.
