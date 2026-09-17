@echo off
setlocal EnableDelayedExpansion
title OmniAgent Manager - Universal AI Agent Control Hub
chcp 65001 >nul

:: Determine absolute directory of this script (handles spaces and trailing slashes)
set "APP_DIR=%~dp0"
if "%APP_DIR:~-1%"=="\" set "APP_DIR=%APP_DIR:~0,-1%"
set "APP_BAT=%~f0"
set "APP_PY=%APP_DIR%\omni_agent_manager.py"

cd /d "%APP_DIR%"

:: Check for explicit flags that affect terminal or elevation
if /i "%~1"=="--no-wt" (
    set "OMNI_NO_WT=1"
    shift
)
if /i "%~1"=="--elevated" (
    set "IS_ELEVATED=1"
    shift
)

:: Informational or headless CLI queries stay in current console
if /i "%~1"=="--help" goto :launch_app
if /i "%~1"=="-h" goto :launch_app
if /i "%~1"=="--version" goto :launch_app
if /i "%~1"=="-v" goto :launch_app
if /i "%~1"=="--export" goto :launch_app
if /i "%~1"=="--import" goto :launch_app

:: If Windows Terminal (wt.exe) is available and we're not inside it, relaunch inside Windows Terminal
if not defined WT_SESSION (
    if not "%OMNI_NO_WT%"=="1" (
        where wt.exe >nul 2>&1
        if !errorlevel! equ 0 (
            set "OMNI_NO_WT=1"
            start "" wt.exe -d "%APP_DIR%" cmd /c call omni_agent_manager.bat %*
            exit /b 0
        )
    )
)

:: Check if user explicitly requested Administrator privileges
if /i "%~1"=="--admin" goto :do_elevate
if /i "%~1"=="--elevate" goto :do_elevate
goto :launch_app

:do_elevate
shift
fltmc >nul 2>&1
if %errorlevel% equ 0 goto :launch_app
net session >nul 2>&1
if %errorlevel% equ 0 goto :launch_app

echo ======================================================================
echo  [OmniAgent Manager] Administrator Elevation Requested
echo ======================================================================
echo  Requesting Windows UAC permissions to configure all AI agent runtimes...
echo.

where wt.exe >nul 2>&1
if %errorlevel% equ 0 (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process wt.exe -ArgumentList '-d `\"%APP_DIR%`\" cmd /c call omni_agent_manager.bat --elevated %*' -Verb RunAs"
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd.exe -ArgumentList '/c cd /d `\"%APP_DIR%`\" ^&^& call omni_agent_manager.bat --elevated %*' -Verb RunAs"
)
exit /b 0

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

:: If explicit arguments passed, execute directly without menu
if not "%~1"=="" (
    python "%APP_PY%" %*
    goto :check_exit
)

:: Otherwise, display interactive launcher menu
:menu
cls
echo ======================================================================
echo   OMNIAGENT MANAGER - UNIVERSAL AI AGENT CONTROL HUB
echo ======================================================================
echo.
echo   [1] Desktop TUI Dashboard (Default - Press Enter)
echo   [2] Classic Minimal Terminal Menu (--classic)
echo   [3] Agent Folders Explorer (--folders)
echo   [4] Fleet ^& Process Radar (--radar)
echo   [5] Run MCP Health Heartbeats (--health)
echo   [6] Run as Administrator (--admin)
echo   [7] Exit
echo.
echo ======================================================================
set "CHOICE="
set /p "CHOICE=Select an option [1-7] (Default: 1): "

if "%CHOICE%"=="" goto :opt1
if "%CHOICE%"=="1" goto :opt1
if "%CHOICE%"=="2" goto :opt2
if "%CHOICE%"=="3" goto :opt3
if "%CHOICE%"=="4" goto :opt4
if "%CHOICE%"=="5" goto :opt5
if "%CHOICE%"=="6" goto :opt6
if "%CHOICE%"=="7" goto :opt7
echo [Invalid selection: %CHOICE%]
timeout /t 2 >nul
goto :menu

:opt1
python "%APP_PY%"
goto :check_exit

:opt2
python "%APP_PY%" --classic
goto :check_exit

:opt3
python "%APP_PY%" --folders
goto :check_exit

:opt4
python "%APP_PY%" --radar
echo.
pause
goto :check_exit

:opt5
python "%APP_PY%" --health
echo.
pause
goto :check_exit

:opt6
goto :do_elevate

:opt7
exit /b 0

:check_exit
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
exit /b %errorlevel%
