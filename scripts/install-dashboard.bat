@echo off
setlocal

rem Determine repository root relative to this script (scripts\..)
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%\.."
set "REPO_ROOT=%CD%"

rem Source and destination paths
set "SRC=%REPO_ROOT%\dashboard-ui\dist"
set "DST=%REPO_ROOT%\nv\svc\farm\services\dashboard\build"

rem Check if dist directory exists AND is non-empty
if not exist "%SRC%" (
    echo dist directory missing — building dashboard-ui...
    goto build_ui
)
dir /b "%SRC%" 2>nul | findstr . >nul
if errorlevel 1 (
    echo dist directory empty — building dashboard-ui...
    goto build_ui
)

echo dist directory exists and is not empty — skipping build.
goto copy_files

:build_ui
echo Running npm build...
npm --prefix "%REPO_ROOT%\dashboard-ui" ci
npm --prefix "%REPO_ROOT%\dashboard-ui" run build
popd

:copy_files
rem Ensure destination exists
if not exist "%DST%" (
    mkdir "%DST%"
)

rem Prefer robocopy if available; fallback to xcopy
where robocopy >nul 2>nul
if %ERRORLEVEL%==0 (
    rem /E: include subdirs; /XO: skip older; quiet flags to reduce noise
    robocopy "%SRC%" "%DST%" /E /NFL /NDL /NJH /NJS /XO
) else (
    xcopy "%SRC%\*" "%DST%\" /E /I /Y /H
)

rem List result
dir /a "%DST%"

popd
endlocal
