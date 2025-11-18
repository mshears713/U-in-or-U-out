@echo off
REM Docker Quick Start Script for Data Alchemist (Windows)
REM This script helps you get started with Docker quickly on Windows

setlocal enabledelayedexpansion

echo ================================================================
echo      Data Alchemist - Docker Quick Start (Windows)
echo ================================================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not installed!
    echo.
    echo Please install Docker Desktop for Windows:
    echo   https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo [OK] Docker is installed
docker --version

REM Check if Docker is running
docker ps >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not running!
    echo.
    echo Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker is running

REM Check for docker-compose
where docker-compose >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Docker Compose is installed
    set COMPOSE_CMD=docker-compose
) else (
    docker compose version >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        echo [OK] Docker Compose ^(plugin^) is installed
        set COMPOSE_CMD=docker compose
    ) else (
        echo [ERROR] Docker Compose is not available!
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Creating data directory...

REM Create data directory
if not exist data mkdir data
echo [OK] Data directory ready at: .\data

echo.
echo [INFO] Building Docker image ^(this may take a few minutes^)...
echo.

REM Build the Docker image
%COMPOSE_CMD% build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to build Docker image
    pause
    exit /b 1
)

echo [OK] Docker image built successfully!

echo.
echo [INFO] Testing the installation...
echo.

REM Test the installation
%COMPOSE_CMD% run --rm data-alchemist --help >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Installation test failed
    pause
    exit /b 1
)

echo [OK] Installation test passed!

echo.
echo ================================================================
echo               Setup Complete!
echo ================================================================
echo.
echo [OK] Data Alchemist is ready to use!
echo.
echo Quick Start Commands:
echo ----------------------------------------------------------------
echo.
echo   1. Show help:
echo      %COMPOSE_CMD% run --rm data-alchemist --help
echo.
echo   2. Detect file type:
echo      %COMPOSE_CMD% run --rm data-alchemist detect /data/yourfile.csv
echo.
echo   3. Convert CSV to JSON:
echo      %COMPOSE_CMD% run --rm data-alchemist convert /data/input.csv --output /data/output.json --format json
echo.
echo   4. List available parsers:
echo      %COMPOSE_CMD% run --rm data-alchemist list-parsers
echo.
echo   5. Open development shell:
echo      %COMPOSE_CMD% --profile dev run --rm data-alchemist-dev
echo.
echo ----------------------------------------------------------------
echo.
echo [INFO] Place your files in the .\data directory to process them
echo [INFO] See DOCKER_SETUP.md for detailed documentation
echo.

pause
