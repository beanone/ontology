#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print step headers
print_step() {
    echo -e "\n${YELLOW}=== $1 ===${NC}"
}

# Function to check command status
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1 successful${NC}"
    else
        echo -e "${RED}✗ $1 failed${NC}"
        exit 1
    fi
}

# Ensure we're in the virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_step "Activating virtual environment"
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        echo -e "${RED}Error: Virtual environment not found. Please create it first:${NC}"
        echo "python -m venv .venv"
        echo "source .venv/bin/activate"
        exit 1
    fi
fi

# Run ruff format
print_step "Running code formatting"
ruff format .
check_status "Code formatting"

# Run ruff checks
print_step "Running code linting"
ruff check .
check_status "Code linting"

# Run type checking with mypy
print_step "Running type checking"
mypy ontology tests
check_status "Type checking"

# Run tests with coverage
print_step "Running tests with coverage"
pytest --cov=ontology --cov-report=term-missing --cov-report=html tests/
check_status "Test coverage"

# Display coverage report location
if [ -d "htmlcov" ]; then
    echo -e "\n${GREEN}Coverage report generated in htmlcov/index.html${NC}"
fi

echo -e "\n${GREEN}All checks completed successfully!${NC}"