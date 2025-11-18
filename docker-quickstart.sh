#!/bin/bash
# Docker Quick Start Script for Data Alchemist
# This script helps you get started with Docker quickly

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Data Alchemist - Docker Quick Start                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed!"
    echo ""
    echo "Please install Docker first:"
    echo "  - Windows/Mac: https://www.docker.com/products/docker-desktop"
    echo "  - Linux: https://docs.docker.com/engine/install/"
    exit 1
fi

print_success "Docker is installed: $(docker --version)"

# Check if Docker is running
if ! docker ps &> /dev/null; then
    print_error "Docker is not running!"
    echo ""
    echo "Please start Docker Desktop (Windows/Mac) or Docker daemon (Linux)"
    exit 1
fi

print_success "Docker is running"

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    print_success "Docker Compose is installed: $(docker-compose --version)"
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    print_success "Docker Compose (plugin) is installed"
    COMPOSE_CMD="docker compose"
else
    print_error "Docker Compose is not available!"
    exit 1
fi

echo ""
print_info "Creating data directory..."

# Create data directory if it doesn't exist
mkdir -p data
print_success "Data directory ready at: ./data"

echo ""
print_info "Building Docker image (this may take a few minutes)..."
echo ""

# Build the Docker image
if $COMPOSE_CMD build; then
    print_success "Docker image built successfully!"
else
    print_error "Failed to build Docker image"
    exit 1
fi

echo ""
print_info "Testing the installation..."
echo ""

# Test the installation
if $COMPOSE_CMD run --rm data-alchemist --help > /dev/null 2>&1; then
    print_success "Installation test passed!"
else
    print_error "Installation test failed"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              Setup Complete!                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
print_success "Data Alchemist is ready to use!"
echo ""
echo "Quick Start Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Show help:"
echo "     ${YELLOW}${COMPOSE_CMD} run --rm data-alchemist --help${NC}"
echo ""
echo "  2. Detect file type:"
echo "     ${YELLOW}${COMPOSE_CMD} run --rm data-alchemist detect /data/yourfile.csv${NC}"
echo ""
echo "  3. Convert CSV to JSON:"
echo "     ${YELLOW}${COMPOSE_CMD} run --rm data-alchemist convert /data/input.csv --output /data/output.json --format json${NC}"
echo ""
echo "  4. List available parsers:"
echo "     ${YELLOW}${COMPOSE_CMD} run --rm data-alchemist list-parsers${NC}"
echo ""
echo "  5. Open development shell:"
echo "     ${YELLOW}${COMPOSE_CMD} --profile dev run --rm data-alchemist-dev${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_info "Place your files in the ${YELLOW}./data${NC} directory to process them"
print_info "See ${YELLOW}DOCKER_SETUP.md${NC} for detailed documentation"
echo ""
