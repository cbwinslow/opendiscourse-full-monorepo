#!/bin/bash
set -euo pipefail

# run-dev.sh - Start OpenDiscourse development environment
#
# USAGE:
#   ./run-dev.sh [--help]
#
# DESCRIPTION:
#   Starts the OpenDiscourse development environment using Docker Compose.
#   Verifies Docker and docker-compose are available before starting services.
#
# REQUIREMENTS:
#   - Docker installed and running
#   - docker-compose installed
#   - docker-compose.yml file in current directory
#
# ENVIRONMENT:
#   Uses environment variables from .env file if present
#
# EXAMPLES:
#   ./run-dev.sh
#   ./run-dev.sh --help

# Function to display help
show_help() {
    echo "run-dev.sh - Start OpenDiscourse development environment"
    echo ""
    echo "USAGE:"
    echo "  ./run-dev.sh [--help]"
    echo ""
    echo "OPTIONS:"
    echo "  --help, -h    Show this help message and exit"
    echo ""
    echo "DESCRIPTION:"
    echo "  Starts the development environment using Docker Compose"
    echo ""
    echo "REQUIREMENTS:"
    echo "  - Docker and docker-compose installed"
    echo "  - docker-compose.yml in current directory"
    exit 0
}

# Check for help flag
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    show_help
fi

# Check if Docker is installed and running
if ! command -v docker &>/dev/null; then
    echo "Error: Docker is not installed or not in PATH" >&2
    echo "Please install Docker first: https://docs.docker.com/get-docker/" >&2
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &>/dev/null; then
    echo "Error: docker-compose is not installed or not in PATH" >&2
    echo "Please install docker-compose: https://docs.docker.com/compose/install/" >&2
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &>/dev/null; then
    echo "Error: Docker daemon is not running" >&2
    echo "Please start Docker daemon first" >&2
    exit 1
fi

# Check if docker-compose.yml exists
if [[ ! -f "docker-compose.yml" ]]; then
    echo "Error: docker-compose.yml not found in current directory" >&2
    echo "Please run this script from the project root directory" >&2
    exit 1
fi

echo "Starting OpenDiscourse development environment..."
echo "Building Docker images..."

docker-compose build
echo "Starting services..."
if docker-compose up -d; then
    echo "✓ Services started successfully"
    echo ""
    echo "Service status:"
    docker-compose ps
    echo ""
    echo "Development environment is now running!"
    echo ""
    echo "Useful commands:"
    echo "  View logs:           docker-compose logs -f"
    echo "  Stop services:       docker-compose down"
    echo "  Restart services:    docker-compose restart"
    echo "  View service status: docker-compose ps"
else
    echo "✗ Failed to start services" >&2
    echo "Check the logs for more information: docker-compose logs" >&2
    exit 1
fi
