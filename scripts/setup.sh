#!/bin/bash
#
# Afrobeats.no Agent System - Setup Script
#
# This script automates the setup process for development environments,
# handling dependencies, virtual environments, and configuration.

set -e
trap 'echo "Error: Command failed at line $LINENO. Exiting..."; exit 1' ERR

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}    Afrobeats.no Agent System Setup        ${NC}"
echo -e "${BLUE}============================================${NC}"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [[ $python_major -lt 3 || ($python_major -eq 3 && $python_minor -lt 8) ]]; then
    echo -e "${RED}Error: Python 3.8+ is required. Found version $python_version${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $python_version detected${NC}"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Set up pre-commit hooks
echo -e "${BLUE}Setting up pre-commit hooks...${NC}"
if [ -f ".pre-commit-config.yaml" ]; then
    pip install pre-commit
    pre-commit install
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
else
    echo -e "${YELLOW}No pre-commit configuration found, skipping${NC}"
fi

# Set up environment file
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Setting up environment file...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Created .env file from example. Please edit with your API keys.${NC}"
    else
        echo -e "${RED}No .env.example file found. Please create a .env file manually.${NC}"
    fi
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi

# Check for web directory and set up if needed
if [ -d "web" ]; then
    echo -e "${BLUE}Setting up web frontend...${NC}"

    # Check if Node.js is installed
    if command -v node &> /dev/null; then
        node_version=$(node --version | cut -d'v' -f2)
        echo -e "${GREEN}✓ Node.js $node_version detected${NC}"

        # Check if npm is installed
        if command -v npm &> /dev/null; then
            cd web
            echo -e "${BLUE}Installing frontend dependencies...${NC}"
            npm install
            echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
            cd ..
        else
            echo -e "${YELLOW}npm not found. Skipping frontend setup.${NC}"
        fi
    else
        echo -e "${YELLOW}Node.js not found. Skipping frontend setup.${NC}"
    fi
fi

# Create cache directory if it doesn't exist
if [ ! -d "cache" ]; then
    echo -e "${BLUE}Creating cache directory...${NC}"
    mkdir -p cache
    echo -e "${GREEN}✓ Cache directory created${NC}"
fi

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}    Setup completed successfully!           ${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Edit .env file with your API keys"
echo -e "  2. Run backend server: ./run_app.sh backend"
echo -e "  3. Run frontend server: ./run_app.sh frontend"
echo -e "  4. Or run both: ./run_app.sh start"
echo -e "${BLUE}Documentation: README.md${NC}"