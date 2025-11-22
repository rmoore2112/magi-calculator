#!/bin/bash

# MAGI Calculator - Startup Script
# This script ensures the uv environment is set up and starts the application

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}MAGI Calculator - Starting Application${NC}"
echo -e "${BLUE}======================================================================${NC}"

# Check if uv is installed
if ! command -v uv &> /dev/null && [ ! -f "$HOME/.local/bin/uv" ]; then
    echo -e "${RED}Error: uv is not installed${NC}"
    echo -e "${YELLOW}Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Use uv from ~/.local/bin if not in PATH
if ! command -v uv &> /dev/null; then
    export PATH="$HOME/.local/bin:$PATH"
fi

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: pyproject.toml not found${NC}"
    echo -e "${YELLOW}Please run this script from the magi-calculator directory${NC}"
    exit 1
fi

# Check if data files exist
if [ ! -d "data" ] || [ -z "$(ls -A data/*.csv 2>/dev/null)" ]; then
    echo -e "${YELLOW}Warning: No CSV files found in data/ directory${NC}"
    echo -e "${YELLOW}Please place your CSV files in the data/ directory before running${NC}"
    exit 1
fi

echo -e "\n${GREEN}✓${NC} Found data files:"
ls -1 data/*.csv | sed 's/^/  /'

# Sync dependencies
echo -e "\n${YELLOW}Syncing dependencies...${NC}"
uv sync

echo -e "${GREEN}✓${NC} Dependencies synced"

# Kill any prior instances
echo -e "\n${YELLOW}Checking for prior instances...${NC}"
PIDS=$(pgrep -f "python.*src\.main" 2>/dev/null || true)
if [ ! -z "$PIDS" ]; then
    echo -e "${YELLOW}Found running instance(s), stopping them...${NC}"
    echo "$PIDS" | xargs kill 2>/dev/null || true
    sleep 1
    # Force kill if still running
    PIDS=$(pgrep -f "python.*src\.main" 2>/dev/null || true)
    if [ ! -z "$PIDS" ]; then
        echo "$PIDS" | xargs kill -9 2>/dev/null || true
    fi
    echo -e "${GREEN}✓${NC} Prior instances stopped"
else
    echo -e "${GREEN}✓${NC} No prior instances found"
fi

# Start the application
echo -e "\n${GREEN}======================================================================${NC}"
echo -e "${GREEN}Starting MAGI Calculator Web Application${NC}"
echo -e "${GREEN}======================================================================${NC}"
echo -e "\n${BLUE}Open your browser and navigate to:${NC}"
echo -e "${BLUE}  → http://127.0.0.1:5001${NC}"
echo -e "\n${YELLOW}Press CTRL+C to stop the server${NC}"
echo -e "${GREEN}======================================================================${NC}\n"

# Run the application as a module
uv run python -m src.main
