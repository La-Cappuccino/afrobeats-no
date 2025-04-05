#!/bin/bash
#
# Afrobeats.no Agent System - Setup and Run Script
#
# This script automates the setup and running of the Afrobeats.no Agent System,
# handling both backend and frontend components.
#
# Features:
# - Dependency installation for backend and frontend
# - Environment setup with API key configuration
# - Server management (start, stop, restart)
# - Development mode with automatic reloading
#
# Usage: ./run_app.sh [option]
#   Options:
#     start       - Start backend and frontend
#     backend     - Start only the backend server
#     frontend    - Start only the frontend server
#     stop        - Stop running servers
#     install     - Install dependencies only
#     help        - Show this help message
#
# If no option is provided, the script will prompt for actions

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Error handling
set -e
trap 'echo -e "${RED}An error occurred. Exiting...${NC}"; exit 1' ERR

# Helper functions
print_header() {
    echo -e "\n${BLUE}============================================${NC}"
    echo -e "${BLUE}         Afrobeats.no Agent System           ${NC}"
    echo -e "${BLUE}============================================${NC}\n"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 is not installed. Please install Python 3.8+ and try again.${NC}"
        exit 1
    fi

    local python_version=$(python3 --version | cut -d' ' -f2)
    local major=$(echo $python_version | cut -d. -f1)
    local minor=$(echo $python_version | cut -d. -f2)

    if [[ $major -lt 3 || ($major -eq 3 && $minor -lt 8) ]]; then
        echo -e "${RED}Python 3.8+ is required. Found version $python_version.${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Python $python_version is installed${NC}"
}

check_node() {
    if ! command -v node &> /dev/null; then
        echo -e "${RED}Node.js is not installed. Please install Node.js 16+ and try again.${NC}"
        exit 1
    fi

    local node_version=$(node --version | cut -d'v' -f2)
    local major=$(echo $node_version | cut -d. -f1)

    if [[ $major -lt 16 ]]; then
        echo -e "${RED}Node.js 16+ is required. Found version $node_version.${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Node.js $node_version is installed${NC}"
}

check_npm() {
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}npm is not installed. Please install npm and try again.${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ npm is installed${NC}"
}

install_backend_deps() {
    echo -e "${CYAN}Installing backend dependencies...${NC}"

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate || source venv/Scripts/activate

    # Install dependencies
    pip install -r requirements.txt

    echo -e "${GREEN}Backend dependencies installed.${NC}"
}

install_frontend_deps() {
    echo -e "${CYAN}Installing frontend dependencies...${NC}"

    # Check if web directory exists
    if [ ! -d "web" ]; then
        echo -e "${RED}Frontend directory not found. Skipping frontend setup.${NC}"
        return
    fi

    # Install dependencies
    cd web
    npm install
    cd ..

    echo -e "${GREEN}Frontend dependencies installed.${NC}"
}

setup_env() {
    echo -e "${CYAN}Setting up environment variables...${NC}"

    # Check if .env file exists
    if [ -f ".env" ]; then
        echo -e "${YELLOW}Found existing .env file. Do you want to recreate it? (y/n)${NC}"
        read -r recreate_env

        if [[ $recreate_env != "y" && $recreate_env != "Y" ]]; then
            echo -e "${GREEN}Using existing .env file.${NC}"
            return
        fi
    fi

    # Copy from example if it exists
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Created .env file from .env.example. Please edit it with your API keys.${NC}"
    else
        # Create .env file
        cat > .env << EOF
# API Keys
GOOGLE_API_KEY=
OPENAI_API_KEY=

# LLM Configuration
GEMINI_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.7

# OpenAI Configuration (if using)
OPENAI_MODEL=gpt-4-turbo
OPENAI_TEMPERATURE=0.7

# Server Configuration
PORT=8000
ENVIRONMENT=development
ENABLE_CACHE=true
CACHE_EXPIRY_HOURS=24

# Security
API_KEY=
ALLOWED_ORIGINS=http://localhost:3000
EOF
        echo -e "${YELLOW}Created .env file. Please edit it with your API keys.${NC}"
    fi

    # Prompt for API keys
    echo -e "${YELLOW}Do you want to enter your API keys now? (y/n)${NC}"
    read -r enter_keys

    if [[ $enter_keys == "y" || $enter_keys == "Y" ]]; then
        echo -e "${YELLOW}Enter your Google API key (leave empty to skip):${NC}"
        read -r google_key

        if [ -n "$google_key" ]; then
            sed -i.bak "s/GOOGLE_API_KEY=/GOOGLE_API_KEY=$google_key/" .env
        fi

        echo -e "${YELLOW}Enter your OpenAI API key (leave empty to skip):${NC}"
        read -r openai_key

        if [ -n "$openai_key" ]; then
            sed -i.bak "s/OPENAI_API_KEY=/OPENAI_API_KEY=$openai_key/" .env
        fi

        # Remove backup file
        rm -f .env.bak

        echo -e "${GREEN}API keys updated.${NC}"
    fi

    echo -e "${GREEN}Environment setup complete.${NC}"
}

start_backend() {
    echo -e "${CYAN}Starting backend server...${NC}"

    # Check if already running
    if lsof -i :8000 &> /dev/null; then
        echo -e "${YELLOW}Backend server is already running on port 8000.${NC}"
        echo -e "${YELLOW}Do you want to restart it? (y/n)${NC}"
        read -r restart

        if [[ $restart == "y" || $restart == "Y" ]]; then
            stop_backend
        else
            return
        fi
    fi

    # Start server in background
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    fi

    python3 api.py > server.log 2>&1 &
    echo $! > backend.pid

    echo -e "${GREEN}Backend server started on http://localhost:8000${NC}"
    echo -e "${YELLOW}Logs available in server.log${NC}"
}

start_frontend() {
    echo -e "${CYAN}Starting frontend server...${NC}"

    # Check if web directory exists
    if [ ! -d "web" ]; then
        echo -e "${RED}Frontend directory not found. Cannot start frontend.${NC}"
        return
    fi

    # Check if already running
    if lsof -i :3000 &> /dev/null; then
        echo -e "${YELLOW}Frontend server is already running on port 3000.${NC}"
        echo -e "${YELLOW}Do you want to restart it? (y/n)${NC}"
        read -r restart

        if [[ $restart == "y" || $restart == "Y" ]]; then
            stop_frontend
        else
            return
        fi
    fi

    # Start server in background
    cd web
    npm run dev > ../frontend.log 2>&1 &
    echo $! > ../frontend.pid
    cd ..

    echo -e "${GREEN}Frontend server started on http://localhost:3000${NC}"
    echo -e "${YELLOW}Logs available in frontend.log${NC}"
}

stop_backend() {
    echo -e "${CYAN}Stopping backend server...${NC}"

    if [ -f "backend.pid" ]; then
        kill $(cat backend.pid) 2>/dev/null || true
        rm backend.pid
        echo -e "${GREEN}Backend server stopped.${NC}"
    else
        echo -e "${YELLOW}No backend server PID file found.${NC}"
        # Try to find and kill by port
        local pid=$(lsof -t -i:8000 2>/dev/null)
        if [ -n "$pid" ]; then
            kill $pid
            echo -e "${GREEN}Backend server stopped.${NC}"
        else
            echo -e "${YELLOW}No backend server found running on port 8000.${NC}"
        fi
    fi
}

stop_frontend() {
    echo -e "${CYAN}Stopping frontend server...${NC}"

    if [ -f "frontend.pid" ]; then
        kill $(cat frontend.pid) 2>/dev/null || true
        rm frontend.pid
        echo -e "${GREEN}Frontend server stopped.${NC}"
    else
        echo -e "${YELLOW}No frontend server PID file found.${NC}"
        # Try to find and kill by port
        local pid=$(lsof -t -i:3000 2>/dev/null)
        if [ -n "$pid" ]; then
            kill $pid
            echo -e "${GREEN}Frontend server stopped.${NC}"
        else
            echo -e "${YELLOW}No frontend server found running on port 3000.${NC}"
        fi
    fi
}

show_menu() {
    print_header

    echo -e "${CYAN}Please select an option:${NC}"
    echo -e "  ${GREEN}1.${NC} Install dependencies"
    echo -e "  ${GREEN}2.${NC} Set up environment"
    echo -e "  ${GREEN}3.${NC} Start backend server only"
    echo -e "  ${GREEN}4.${NC} Start frontend server only"
    echo -e "  ${GREEN}5.${NC} Start both backend and frontend"
    echo -e "  ${GREEN}6.${NC} Stop all servers"
    echo -e "  ${GREEN}0.${NC} Exit"
    echo -e "\n${YELLOW}Choose an option:${NC}"
    read -r option

    case $option in
        1) install_deps ;;
        2) setup_env ;;
        3) start_backend ;;
        4) start_frontend ;;
        5) start_all ;;
        6) stop_all ;;
        0) exit 0 ;;
        *) echo -e "${RED}Invalid option.${NC}"; show_menu ;;
    esac

    echo -e "\n${YELLOW}Press enter to return to the menu...${NC}"
    read
    show_menu
}

install_deps() {
    check_python
    check_node
    check_npm
    install_backend_deps
    install_frontend_deps
}

start_all() {
    start_backend
    start_frontend

    echo -e "\n${GREEN}All servers started successfully!${NC}"
    echo -e "${BLUE}API server:${NC} http://localhost:8000"
    echo -e "${BLUE}API docs:${NC} http://localhost:8000/docs"
    echo -e "${BLUE}Frontend:${NC} http://localhost:3000"
}

stop_all() {
    stop_backend
    stop_frontend
    echo -e "${GREEN}All servers stopped.${NC}"
}

show_help() {
    print_header
    echo -e "Usage: ./run_app.sh [option]"
    echo -e "  Options:"
    echo -e "    ${GREEN}start${NC}     - Start backend and frontend"
    echo -e "    ${GREEN}backend${NC}   - Start only the backend server"
    echo -e "    ${GREEN}frontend${NC}  - Start only the frontend server"
    echo -e "    ${GREEN}stop${NC}      - Stop running servers"
    echo -e "    ${GREEN}install${NC}   - Install dependencies only"
    echo -e "    ${GREEN}help${NC}      - Show this help message"
    echo -e "\nIf no option is provided, the script will prompt for actions."
}

# Main execution
print_header

# Process command line arguments
if [ $# -gt 0 ]; then
    case $1 in
        start) start_all ;;
        backend) start_backend ;;
        frontend) start_frontend ;;
        stop) stop_all ;;
        install) install_deps ;;
        help) show_help ;;
        *) echo -e "${RED}Invalid option: $1${NC}"; show_help; exit 1 ;;
    esac
else
    # Show interactive menu
    show_menu
fi