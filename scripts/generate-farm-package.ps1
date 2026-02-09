$ErrorActionPreference = "Stop"

# Helper function to run commands and throw errors on failure
function Run-Command {
    param (
        [string]$Command
    )
    Write-Host "Running: $Command"
    
    # Run the command and display its output in real-time
    $process = Start-Process -FilePath "powershell.exe" -ArgumentList "-Command $Command" `
                -NoNewWindow -Wait -PassThru
    
    # Check exit code
    if ($process.ExitCode -ne 0) {
        throw "Command failed: '$Command' (Exit Code: $($process.ExitCode))"
    }
}

# Clean previous build directories
Remove-Item -Recurse -Force "farm-install" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue

# Create new install directory
New-Item -ItemType Directory -Path "farm-install" | Out-Null

# Run build and packaging commands
Run-Command "python -m ensurepip"
Run-Command "python -m pip install --upgrade pip"
Run-Command "python -m pip install poetry"
Run-Command "python -m pip install poetry-plugin-export"
Run-Command "poetry --version"

# allow poetry-plugin-export command to fail silently since we only need with poetry < 2.0.0
poetry self add poetry-plugin-export

Run-Command "poetry build --format=wheel --output=farm-install --no-interaction"
Run-Command "poetry export --format=requirements.txt --output=requirements.txt --without-hashes"
Run-Command "pip download --dest farm-install\dependencies -r requirements.txt"
Run-Command "Compress-Archive -Path farm-install\* -DestinationPath farm-package.zip"

Write-Host "Successfully generated farm package"
exit 0
