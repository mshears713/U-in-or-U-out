#!/bin/bash
##############################################################################
# Data Alchemist - Automated Setup Script (Unix/Linux/macOS)
##############################################################################
#
# This script automates the environment setup for Data Alchemist.
# It handles virtual environment creation, dependency installation,
# and basic verification.
#
# Usage:
#   ./setup.sh
#
# Requirements:
#   - Python 3.8 or higher
#   - pip package manager
#
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
PROJECT_NAME="Data Alchemist"
MIN_PYTHON_VERSION="3.8"
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

##############################################################################
# Utility Functions
##############################################################################

print_header() {
    echo -e "${BLUE}============================================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

##############################################################################
# Python Version Check
##############################################################################

check_python_version() {
    print_info "Checking Python version..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        echo "  Please install Python 3.8 or higher from https://python.org"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_info "Found Python $PYTHON_VERSION"

    # Check if version is >= 3.8
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python $MIN_PYTHON_VERSION or higher is required"
        echo "  Current version: $PYTHON_VERSION"
        echo "  Please upgrade Python from https://python.org"
        exit 1
    fi

    print_success "Python version check passed"
}

##############################################################################
# Virtual Environment Setup
##############################################################################

create_virtualenv() {
    print_info "Creating virtual environment..."

    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at $VENV_DIR"
        read -p "  Remove and recreate? (y/N): " response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
            print_info "Removed existing virtual environment"
        else
            print_info "Using existing virtual environment"
            return 0
        fi
    fi

    python3 -m venv "$VENV_DIR"

    if [ $? -eq 0 ]; then
        print_success "Virtual environment created successfully"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
}

##############################################################################
# Dependency Installation
##############################################################################

install_dependencies() {
    print_info "Installing dependencies from $REQUIREMENTS_FILE..."

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Upgrade pip
    print_info "Upgrading pip..."
    python -m pip install --upgrade pip -q

    # Install requirements
    if [ -f "$REQUIREMENTS_FILE" ]; then
        pip install -r "$REQUIREMENTS_FILE"

        if [ $? -eq 0 ]; then
            print_success "Dependencies installed successfully"
        else
            print_error "Failed to install dependencies"
            exit 1
        fi
    else
        print_error "$REQUIREMENTS_FILE not found"
        exit 1
    fi
}

##############################################################################
# Verification
##############################################################################

verify_installation() {
    print_info "Verifying installation..."

    # Check if data_alchemist module can be imported
    python -c "import data_alchemist" 2>/dev/null

    if [ $? -eq 0 ]; then
        print_success "Data Alchemist module can be imported"
    else
        print_warning "Data Alchemist module import check failed (may be normal)"
    fi

    # Try running help command
    python -m data_alchemist.cli --help > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        print_success "CLI is functional"
    else
        print_warning "CLI help command failed"
    fi

    # Run a quick test
    print_info "Running unit tests..."
    python -m unittest discover tests/unit -q 2>/dev/null

    if [ $? -eq 0 ]; then
        print_success "Unit tests passed"
    else
        print_warning "Some unit tests failed (run 'python -m unittest discover tests' for details)"
    fi
}

##############################################################################
# Post-Setup Instructions
##############################################################################

show_instructions() {
    print_header "Setup Complete!"

    echo ""
    echo "To activate the virtual environment:"
    echo -e "  ${GREEN}source $VENV_DIR/bin/activate${NC}"
    echo ""
    echo "To deactivate the virtual environment:"
    echo -e "  ${GREEN}deactivate${NC}"
    echo ""
    echo "Quick start commands:"
    echo -e "  ${GREEN}# Detect file type${NC}"
    echo "  python -m data_alchemist.cli detect tests/fixtures/sample.csv"
    echo ""
    echo -e "  ${GREEN}# Convert CSV to JSON${NC}"
    echo "  python -m data_alchemist.cli convert tests/fixtures/sample.csv -o output.json -f json"
    echo ""
    echo -e "  ${GREEN}# List available parsers${NC}"
    echo "  python -m data_alchemist.cli list-parsers"
    echo ""
    echo -e "  ${GREEN}# Run tests${NC}"
    echo "  python -m unittest discover tests"
    echo ""
    echo "Documentation:"
    echo "  • User Guide: USER_GUIDE.md"
    echo "  • Developer Guide: DEVELOPER_GUIDE.md"
    echo "  • Examples: examples/ directory"
    echo ""
}

##############################################################################
# Main Setup Workflow
##############################################################################

main() {
    print_header "$PROJECT_NAME - Automated Setup"
    echo ""

    # Step 1: Check Python version
    check_python_version
    echo ""

    # Step 2: Create virtual environment
    create_virtualenv
    echo ""

    # Step 3: Install dependencies
    install_dependencies
    echo ""

    # Step 4: Verify installation
    verify_installation
    echo ""

    # Step 5: Show post-setup instructions
    show_instructions
}

# Run main function
main
