@echo off
REM ###########################################################################
REM Data Alchemist - Automated Setup Script (Windows)
REM ###########################################################################
REM
REM This script automates the environment setup for Data Alchemist on Windows.
REM It handles virtual environment creation, dependency installation,
REM and basic verification.
REM
REM Usage:
REM   setup.bat
REM
REM Requirements:
REM   - Python 3.8 or higher
REM   - pip package manager
REM
REM ###########################################################################

setlocal enabledelayedexpansion

REM Script configuration
set PROJECT_NAME=Data Alchemist
set MIN_PYTHON_VERSION=3.8
set VENV_DIR=venv
set REQUIREMENTS_FILE=requirements.txt

REM ###########################################################################
REM Utility Functions
REM ###########################################################################

:print_header
echo ============================================================================
echo   %~1
echo ============================================================================
exit /b

:print_success
echo [92m✓[0m %~1
exit /b

:print_error
echo [91m✗[0m %~1
exit /b

:print_warning
echo [93m⚠[0m %~1
exit /b

:print_info
echo [94mℹ[0m %~1
exit /b

REM ###########################################################################
REM Python Version Check
REM ###########################################################################

:check_python_version
call :print_info "Checking Python version..."

where python >nul 2>nul
if %errorlevel% neq 0 (
    call :print_error "Python is not installed or not in PATH"
    echo   Please install Python 3.8 or higher from https://python.org
    echo   Make sure to check 'Add Python to PATH' during installation
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
call :print_info "Found Python %PYTHON_VERSION%"

REM Extract major and minor version
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if %PYTHON_MAJOR% lss 3 (
    call :print_error "Python 3.8 or higher is required"
    echo   Current version: %PYTHON_VERSION%
    exit /b 1
)

if %PYTHON_MAJOR% equ 3 if %PYTHON_MINOR% lss 8 (
    call :print_error "Python 3.8 or higher is required"
    echo   Current version: %PYTHON_VERSION%
    exit /b 1
)

call :print_success "Python version check passed"
exit /b 0

REM ###########################################################################
REM Virtual Environment Setup
REM ###########################################################################

:create_virtualenv
call :print_info "Creating virtual environment..."

if exist "%VENV_DIR%" (
    call :print_warning "Virtual environment already exists at %VENV_DIR%"
    set /p response="  Remove and recreate? (y/N): "
    if /i "!response!"=="y" (
        rmdir /s /q "%VENV_DIR%"
        call :print_info "Removed existing virtual environment"
    ) else (
        call :print_info "Using existing virtual environment"
        exit /b 0
    )
)

python -m venv "%VENV_DIR%"

if %errorlevel% equ 0 (
    call :print_success "Virtual environment created successfully"
) else (
    call :print_error "Failed to create virtual environment"
    exit /b 1
)
exit /b 0

REM ###########################################################################
REM Dependency Installation
REM ###########################################################################

:install_dependencies
call :print_info "Installing dependencies from %REQUIREMENTS_FILE%..."

REM Activate virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

REM Upgrade pip
call :print_info "Upgrading pip..."
python -m pip install --upgrade pip -q

REM Install requirements
if exist "%REQUIREMENTS_FILE%" (
    pip install -r "%REQUIREMENTS_FILE%"

    if %errorlevel% equ 0 (
        call :print_success "Dependencies installed successfully"
    ) else (
        call :print_error "Failed to install dependencies"
        exit /b 1
    )
) else (
    call :print_error "%REQUIREMENTS_FILE% not found"
    exit /b 1
)
exit /b 0

REM ###########################################################################
REM Verification
REM ###########################################################################

:verify_installation
call :print_info "Verifying installation..."

REM Check if data_alchemist module can be imported
python -c "import data_alchemist" 2>nul
if %errorlevel% equ 0 (
    call :print_success "Data Alchemist module can be imported"
) else (
    call :print_warning "Data Alchemist module import check failed (may be normal)"
)

REM Try running help command
python -m data_alchemist.cli --help >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "CLI is functional"
) else (
    call :print_warning "CLI help command failed"
)

REM Run a quick test
call :print_info "Running unit tests..."
python -m unittest discover tests/unit -q 2>nul

if %errorlevel% equ 0 (
    call :print_success "Unit tests passed"
) else (
    call :print_warning "Some unit tests failed (run 'python -m unittest discover tests' for details)"
)
exit /b 0

REM ###########################################################################
REM Post-Setup Instructions
REM ###########################################################################

:show_instructions
call :print_header "Setup Complete!"

echo.
echo To activate the virtual environment:
echo   [92m%VENV_DIR%\Scripts\activate.bat[0m
echo.
echo To deactivate the virtual environment:
echo   [92mdeactivate[0m
echo.
echo Quick start commands:
echo   [92m# Detect file type[0m
echo   python -m data_alchemist.cli detect tests\fixtures\sample.csv
echo.
echo   [92m# Convert CSV to JSON[0m
echo   python -m data_alchemist.cli convert tests\fixtures\sample.csv -o output.json -f json
echo.
echo   [92m# List available parsers[0m
echo   python -m data_alchemist.cli list-parsers
echo.
echo   [92m# Run tests[0m
echo   python -m unittest discover tests
echo.
echo Documentation:
echo   • User Guide: USER_GUIDE.md
echo   • Developer Guide: DEVELOPER_GUIDE.md
echo   • Examples: examples\ directory
echo.
exit /b 0

REM ###########################################################################
REM Main Setup Workflow
REM ###########################################################################

:main
call :print_header "%PROJECT_NAME% - Automated Setup"
echo.

REM Step 1: Check Python version
call :check_python_version
if %errorlevel% neq 0 exit /b 1
echo.

REM Step 2: Create virtual environment
call :create_virtualenv
if %errorlevel% neq 0 exit /b 1
echo.

REM Step 3: Install dependencies
call :install_dependencies
if %errorlevel% neq 0 exit /b 1
echo.

REM Step 4: Verify installation
call :verify_installation
echo.

REM Step 5: Show post-setup instructions
call :show_instructions
exit /b 0

REM Run main function
call :main
