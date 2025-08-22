#!/bin/bash

# EduBot Setup Script
# This script helps you set up the EduBot application quickly

set -e

echo "🚀 Setting up EduBot - Chatbot Hỗ trợ Giáo viên Soạn giảng"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_step "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 16+ first."
        exit 1
    fi
    
    print_status "All requirements are satisfied!"
}

# Setup environment files
setup_environment() {
    print_step "Setting up environment files..."
    
    # Backend environment
    if [ ! -f "backend/.env" ]; then
        print_status "Creating backend .env file..."
        cp backend/env.example backend/.env
        
        print_warning "Please edit backend/.env and add your OpenAI API key!"
        print_warning "OPENAI_API_KEY=your-api-key-here"
    else
        print_status "Backend .env already exists."
    fi
}

# Start database
start_database() {
    print_step "Starting MongoDB database..."
    
    cd database
    docker-compose up -d
    cd ..
    
    print_status "Waiting for MongoDB to be ready..."
    sleep 10
    
    print_status "MongoDB is ready!"
    print_status "MongoDB Express UI: http://localhost:8081"
}

# Setup backend
setup_backend() {
    print_step "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    cd ..
    print_status "Backend setup completed!"
}

# Setup agents
setup_agents() {
    print_step "Setting up AI agents..."
    
    cd agent
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment for agents..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing agent dependencies..."
    pip install -r requirements.txt
    
    cd ..
    print_status "Agents setup completed!"
}

# Setup frontend
setup_frontend() {
    print_step "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    cd ..
    print_status "Frontend setup completed!"
}

# Start all services
start_services() {
    print_step "Starting all services..."
    
    # Start backend
    print_status "Starting backend (port 8000)..."
    cd backend
    source venv/bin/activate
    python -m app.main &
    BACKEND_PID=$!
    cd ..
    
    sleep 5
    
    # Start main agent
    print_status "Starting main agent (port 8001)..."
    cd agent
    source venv/bin/activate
    python main_agent.py &
    MAIN_AGENT_PID=$!
    cd ..
    
    sleep 3
    
    # Start external agent
    print_status "Starting external agent (port 8002)..."
    cd agent
    source venv/bin/activate
    python external_agent.py &
    EXTERNAL_AGENT_PID=$!
    cd ..
    
    sleep 3
    
    # Start frontend
    print_status "Starting frontend (port 3000)..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # Store PIDs for cleanup
    echo $BACKEND_PID > .backend.pid
    echo $MAIN_AGENT_PID > .main_agent.pid
    echo $EXTERNAL_AGENT_PID > .external_agent.pid
    echo $FRONTEND_PID > .frontend.pid
    
    print_status "All services are starting..."
    sleep 10
}

# Display final information
show_info() {
    echo ""
    echo "🎉 EduBot setup completed!"
    echo "=========================="
    echo ""
    echo "📱 Application URLs:"
    echo "   Frontend:        http://localhost:3000"
    echo "   Backend API:     http://localhost:8000/docs"
    echo "   Main Agent:      http://localhost:8001/docs"
    echo "   External Agent:  http://localhost:8002/docs"
    echo "   MongoDB Express: http://localhost:8081"
    echo ""
    echo "🔧 Next steps:"
    echo "   1. Edit backend/.env and add your OpenAI API key"
    echo "   2. Visit http://localhost:3000 to use the application"
    echo "   3. Check the documentation in docs/README.md"
    echo ""
    echo "🛑 To stop all services, run: ./scripts/stop.sh"
    echo ""
}

# Main execution
main() {
    check_requirements
    setup_environment
    start_database
    setup_backend
    setup_agents
    setup_frontend
    start_services
    show_info
}

# Handle script interruption
cleanup() {
    print_warning "Setup interrupted. Cleaning up..."
    if [ -f ".backend.pid" ]; then
        kill $(cat .backend.pid) 2>/dev/null || true
        rm .backend.pid
    fi
    if [ -f ".main_agent.pid" ]; then
        kill $(cat .main_agent.pid) 2>/dev/null || true
        rm .main_agent.pid
    fi
    if [ -f ".external_agent.pid" ]; then
        kill $(cat .external_agent.pid) 2>/dev/null || true
        rm .external_agent.pid
    fi
    if [ -f ".frontend.pid" ]; then
        kill $(cat .frontend.pid) 2>/dev/null || true
        rm .frontend.pid
    fi
    exit 1
}

trap cleanup SIGINT SIGTERM

# Check if running from correct directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the project root directory."
    exit 1
fi

# Run main function
main
