#!/bin/bash
# dev_setup.sh - Development environment setup script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[STATUS]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        print_warning "Node.js is not installed. Some features may not work properly."
    else
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    fi
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        print_warning "Python 3 is not installed. Some features may not work properly."
    else
        PYTHON_VERSION=$(python3 --version)
        print_success "$PYTHON_VERSION found"
    fi
    
    # Check if pnpm is installed
    if ! command -v pnpm &> /dev/null; then
        print_warning "pnpm is not installed. Consider installing it for better monorepo support."
    else
        PNPM_VERSION=$(pnpm --version)
        print_success "pnpm $PNPM_VERSION found"
    fi
    
    print_success "Prerequisites check completed"
}

# Function to set up Docker environment
setup_docker_environment() {
    print_status "Setting up Docker environment..."
    
    # Create necessary directories
    mkdir -p init_scripts volumes/{postgres,qdrant,neo4j,redis}
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    # Build Docker images
    print_status "Building Docker images..."
    if docker-compose -f docker-compose.dev.yml build; then
        print_success "Docker images built successfully"
    else
        print_error "Failed to build Docker images"
        exit 1
    fi
    
    print_success "Docker environment setup completed"
}

# Function to start development environment
start_dev_environment() {
    print_status "Starting development environment..."
    
    # Start all services
    if docker-compose -f docker-compose.dev.yml up -d; then
        print_success "Development environment started successfully"
    else
        print_error "Failed to start development environment"
        exit 1
    fi
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check service status
    print_status "Checking service status..."
    docker-compose -f docker-compose.dev.yml ps
    
    print_success "Development environment is running"
}

# Function to set up database
setup_database() {
    print_status "Setting up database..."
    
    # Run database setup script
    if [ -f "./database_setup.sh" ]; then
        chmod +x ./database_setup.sh
        ./database_setup.sh
    else
        print_warning "Database setup script not found. Skipping database setup."
    fi
    
    print_success "Database setup completed"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing project dependencies..."
    
    # Install Node.js dependencies
    if command -v pnpm &> /dev/null; then
        if pnpm install; then
            print_success "Node.js dependencies installed with pnpm"
        else
            print_error "Failed to install Node.js dependencies with pnpm"
        fi
    elif command -v npm &> /dev/null; then
        if npm install; then
            print_success "Node.js dependencies installed with npm"
        else
            print_error "Failed to install Node.js dependencies with npm"
        fi
    else
        print_warning "No Node.js package manager found. Skipping Node.js dependencies."
    fi
    
    # Install Python dependencies
    if command -v pip3 &> /dev/null; then
        if pip3 install -r requirements.txt; then
            print_success "Python dependencies installed"
        else
            print_error "Failed to install Python dependencies"
        fi
    else
        print_warning "pip3 not found. Skipping Python dependencies."
    fi
    
    print_success "Dependency installation completed"
}

# Function to run initial setup
initial_setup() {
    print_status "Running initial project setup..."
    
    # Create necessary directories
    mkdir -p logs tmp data/{raw,processed,cache} backups
    
    # Set up environment variables
    if [ ! -f .env ]; then
        print_status "Creating .env file from example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_success ".env file created from example"
        else
            print_warning ".env.example not found. Creating minimal .env file..."
            cat > .env << EOF
# OpenDiscourse Environment Variables
DATABASE_URL=postgresql://opendiscourse:opendiscourse@localhost:5432/opendiscourse
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
NEO4J_URL=bolt://localhost:7687

# API Keys (replace with actual values)
OPENAI_API_KEY=your_openai_api_key_here
GOVINFO_API_KEY=your_govinfo_api_key_here
CONGRESS_API_KEY=your_congress_api_key_here

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
EOF
            print_success "Minimal .env file created"
        fi
    else
        print_status ".env file already exists"
    fi
    
    print_success "Initial setup completed"
}

# Function to show development commands
show_dev_commands() {
    echo ""
    echo "==========================================="
    echo "    Development Commands"
    echo "==========================================="
    echo ""
    echo "Start development environment:"
    echo "  docker-compose -f docker-compose.dev.yml up -d"
    echo ""
    echo "Stop development environment:"
    echo "  docker-compose -f docker-compose.dev.yml down"
    echo ""
    echo "View logs:"
    echo "  docker-compose -f docker-compose.dev.yml logs -f"
    echo ""
    echo "Access services:"
    echo "  PostgreSQL: localhost:5432"
    echo "  pgAdmin: http://localhost:5050"
    echo "  Qdrant: http://localhost:6333"
    echo "  Neo4j: http://localhost:7474"
    echo "  Redis: localhost:6379"
    echo "  API Server: http://localhost:8000"
    echo "  Web Client: http://localhost:3000"
    echo ""
    echo "Run tests:"
    echo "  pnpm test"
    echo ""
    echo "Build packages:"
    echo "  pnpm build"
    echo ""
    echo "Format code:"
    echo "  pnpm format"
    echo ""
    echo "Lint code:"
    echo "  pnpm lint"
    echo ""
}

# Function to show troubleshooting tips
show_troubleshooting() {
    echo ""
    echo "==========================================="
    echo "    Troubleshooting Tips"
    echo "==========================================="
    echo ""
    echo "Common issues and solutions:"
    echo ""
    echo "1. Docker permission denied:"
    echo "   - Add your user to the docker group: sudo usermod -aG docker $USER"
    echo "   - Log out and back in for changes to take effect"
    echo ""
    echo "2. Port conflicts:"
    echo "   - Check which services are using ports: sudo lsof -i :5432"
    echo "   - Stop conflicting services or change ports in docker-compose.dev.yml"
    echo ""
    echo "3. Database connection issues:"
    echo "   - Ensure PostgreSQL container is running: docker-compose -f docker-compose.dev.yml ps"
    echo "   - Check database logs: docker-compose -f docker-compose.dev.yml logs postgres"
    echo ""
    echo "4. Dependency installation issues:"
    echo "   - Clear node_modules: rm -rf node_modules && pnpm install"
    echo "   - Clear Python cache: pip cache purge"
    echo ""
    echo "5. Service won't start:"
    echo "   - Check service logs: docker-compose -f docker-compose.dev.yml logs <service_name>"
    echo "   - Rebuild images: docker-compose -f docker-compose.dev.yml build --no-cache"
    echo ""
}

# Main function
main() {
    print_status "Starting OpenDiscourse Development Environment Setup"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Run initial setup
    initial_setup
    
    # Set up Docker environment
    setup_docker_environment
    
    # Install dependencies
    install_dependencies
    
    # Set up database
    setup_database
    
    # Start development environment
    start_dev_environment
    
    # Show development commands
    show_dev_commands
    
    # Show troubleshooting tips
    show_troubleshooting
    
    print_success "Development environment setup completed successfully!"
    echo ""
    print_warning "Next steps:"
    echo "1. Review the .env file and update with your API keys"
    echo "2. Start developing by modifying files in the packages/ directory"
    echo "3. Access services using the URLs shown above"
    echo "4. Run tests with: pnpm test"
    echo ""
    print_success "Happy coding with OpenDiscourse!"
}

# Run main function
main