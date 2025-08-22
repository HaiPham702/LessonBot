#!/bin/bash

# EduBot Stop Script
# This script stops all EduBot services

set -e

echo "🛑 Stopping EduBot services..."
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Stop application services
stop_app_services() {
    print_status "Stopping application services..."
    
    # Stop frontend
    if [ -f ".frontend.pid" ]; then
        PID=$(cat .frontend.pid)
        if kill -0 $PID 2>/dev/null; then
            print_status "Stopping frontend (PID: $PID)..."
            kill $PID
        fi
        rm .frontend.pid
    fi
    
    # Stop external agent
    if [ -f ".external_agent.pid" ]; then
        PID=$(cat .external_agent.pid)
        if kill -0 $PID 2>/dev/null; then
            print_status "Stopping external agent (PID: $PID)..."
            kill $PID
        fi
        rm .external_agent.pid
    fi
    
    # Stop main agent
    if [ -f ".main_agent.pid" ]; then
        PID=$(cat .main_agent.pid)
        if kill -0 $PID 2>/dev/null; then
            print_status "Stopping main agent (PID: $PID)..."
            kill $PID
        fi
        rm .main_agent.pid
    fi
    
    # Stop backend
    if [ -f ".backend.pid" ]; then
        PID=$(cat .backend.pid)
        if kill -0 $PID 2>/dev/null; then
            print_status "Stopping backend (PID: $PID)..."
            kill $PID
        fi
        rm .backend.pid
    fi
    
    # Kill any remaining processes on the ports
    print_status "Cleaning up any remaining processes..."
    
    # Kill processes on port 3000 (frontend)
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    
    # Kill processes on port 8000 (backend)
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    
    # Kill processes on port 8001 (main agent)
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    
    # Kill processes on port 8002 (external agent)
    lsof -ti:8002 | xargs kill -9 2>/dev/null || true
}

# Stop database services
stop_database() {
    print_status "Stopping database services..."
    
    cd database
    docker-compose down
    cd ..
    
    print_status "Database services stopped."
}

# Stop Docker services (if running)
stop_docker_services() {
    if [ -f "docker-compose.yml" ]; then
        print_status "Stopping Docker services..."
        docker-compose down
        print_status "Docker services stopped."
    fi
}

# Clean up temporary files
cleanup() {
    print_status "Cleaning up temporary files..."
    
    # Remove PID files
    rm -f .backend.pid .main_agent.pid .external_agent.pid .frontend.pid
    
    # Clean up logs (if any)
    rm -f *.log
    
    print_status "Cleanup completed."
}

# Main execution
main() {
    if [ "$1" = "--docker" ]; then
        stop_docker_services
    else
        stop_app_services
        stop_database
    fi
    
    cleanup
    
    echo ""
    echo "✅ All EduBot services have been stopped."
    echo ""
    echo "To start services again:"
    echo "  Development: ./scripts/setup.sh"
    echo "  Docker:      docker-compose up -d"
    echo ""
}

# Check if running from correct directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the project root directory."
    exit 1
fi

# Show help
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "EduBot Stop Script"
    echo ""
    echo "Usage:"
    echo "  ./scripts/stop.sh           # Stop development services"
    echo "  ./scripts/stop.sh --docker  # Stop Docker services"
    echo "  ./scripts/stop.sh --help    # Show this help"
    echo ""
    exit 0
fi

# Run main function
main "$@"
