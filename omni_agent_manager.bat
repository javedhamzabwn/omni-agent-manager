@echo off
setlocal EnableDelayedExpansion
title OmniAgent Manager - Universal AI Agent Control Hub
chcp 65001 >nul

:: Determine absolute directory of this script (handles spaces and trailing slashes)
set "APP_DIR=%~dp0"
if "%APP_DIR:~-1%"=="\" set "APP_DIR=%APP_DIR:~0,-1%"
set "APP_BAT=%~f0"
set "APP_PY=%APP_DIR%\omni_agent_manager.py"

:: Always ensure working directory is APP_DIR
cd /d "%APP_DIR%"

:: Bypass elevation for informational or explicit flags
if /i "%~1"=="--help" goto :launch_app
if /i "%~1"=="-h" goto :launch_app
if /i "%~1"=="--version" goto :launch_app
if /i "%~1"=="-v" goto :launch_app
if /i "%~1"=="--no-admin" (
    shift
    goto :launch_app
)
if /i "%~1"=="--elevated" (
    shift
    goto :launch_app
)

:: Check for Administrator permissions
fltmc >nul 2>&1
if %errorlevel% equ 0 goto :launch_app
net session >nul 2>&1
if %errorlevel% equ 0 goto :launch_app

echo ======================================================================
echo  [OmniAgent Manager] Administrator Elevation Required
echo ======================================================================
echo  Requesting Windows UAC permissions to configure all AI agent runtimes...
echo.

:: Launch elevated batch file directly using PowerShell Start-Process
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%APP_BAT%' -ArgumentList '--elevated %*' -WorkingDirectory '%APP_DIR%' -Verb RunAs"
if %errorlevel% equ 0 exit /b

echo [WARNING] Administrator elevation declined or cancelled.
echo Launching in standard user mode...
echo.

:launch_app
cd /d "%APP_DIR%"

:: Check if omni_agent_manager.py exists in APP_DIR
if not exist "%APP_PY%" (
    echo [ERROR] Cannot locate omni_agent_manager.py!
    echo Expected path: "%APP_PY%"
    echo Current dir:   "%CD%"
    echo.
    echo If installed via pip, you can launch globally with:
    echo     omni-agent
    echo.
    pause
    exit /b 1
)

:: Run Python script
python "%APP_PY%" %*
if %errorlevel% neq 0 (
    echo.
    echo [NOTE] OmniAgent Manager exited with code %errorlevel%.
    echo To run classic minimal terminal mode:
    echo     python "%APP_PY%" --classic
    echo Or using global pip command:
    echo     omni-agent --classic
    echo.
    pause
)
