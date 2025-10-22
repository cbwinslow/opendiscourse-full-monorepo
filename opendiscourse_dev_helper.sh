#!/bin/bash
# opendiscourse_dev_helper.sh - Development helper script for OpenDiscourse project

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

# Function to check if we're in the right directory
check_project_root() {
    if [ ! -f "PROJECT_SUMMARY.md" ] || [ ! -d "packages" ]; then
        print_error "This script must be run from the OpenDiscourse project root directory"
        print_error "Current directory: $(pwd)"
        exit 1
    fi
}

# Function to show project overview
show_project_overview() {
    clear
    echo "==========================================="
    echo "    OpenDiscourse Development Helper"
    echo "==========================================="
    echo ""
    echo "Project Structure:"
    echo "├── apps/                    # Applications"
    echo "│   ├── api-server/         # Main API server"
    echo "│   ├── web-client/         # Main web client"
    echo "│   └── web-client-next/    # Next.js web client"
    echo "├── packages/               # Core packages"
    echo "│   ├── api/                # API services"
    echo "│   ├── data-collector/     # Data collection tools"
    echo "│   ├── rag-engine/         # RAG engine components"
    echo "│   └── web/                # Web frontend components"
    echo "├── tools/                  # Development tools"
    echo "└── external-sources/       # External reference implementations"
    echo ""
    echo "Key Documentation:"
    echo "├── PROJECT_SUMMARY.md      # Project overview"
    echo "├── KNOWLEDGE_BASE.md       # AI context and guidance"
    echo "├── FEATURES.md            # Feature roadmap"
    echo "├── TODO.md                # Current tasks and cleanup"
    echo "└── AGENT_SETUP_GUIDE.md    # Agent setup instructions"
    echo ""
}

# Function to list available services
list_services() {
    print_status "Available services in the project:"
    echo ""
    
    if [ -d "apps/api-server" ]; then
        echo "1. API Server - Main backend service"
        echo "   Location: apps/api-server/"
        echo "   Purpose: Provides REST API for data access"
        echo ""
    fi
    
    if [ -d "apps/web-client" ]; then
        echo "2. Web Client - Main web interface"
        echo "   Location: apps/web-client/"
        echo "   Purpose: User interface for browsing data"
        echo ""
    fi
    
    if [ -d "apps/web-client-next" ]; then
        echo "3. Web Client (Next.js) - Modern web interface"
        echo "   Location: apps/web-client-next/"
        echo "   Purpose: Enhanced web interface with Next.js"
        echo ""
    fi
    
    if [ -d "packages/data-collector" ]; then
        echo "4. Data Collector - Government data collection"
        echo "   Location: packages/data-collector/"
        echo "   Purpose: Collects data from government sources"
        echo ""
    fi
    
    if [ -d "packages/rag-engine" ]; then
        echo "5. RAG Engine - AI-powered analysis"
        echo "   Location: packages/rag-engine/"
        echo "   Purpose: Retrieval Augmented Generation system"
        echo ""
    fi
}

# Function to show development commands
show_commands() {
    echo "==========================================="
    echo "    Development Commands"
    echo "==========================================="
    echo ""
    echo "Setup & Installation:"
    echo "  npm install            # Install Node.js dependencies"
    echo "  pip install -r requirements.txt  # Install Python dependencies"
    echo ""
    echo "Development:"
    echo "  npm run dev            # Run all services in development mode"
    echo "  npm run build          # Build all packages"
    echo "  npm run test           # Run tests"
    echo ""
    echo "Docker:"
    echo "  docker-compose up      # Start services with Docker"
    echo "  docker-compose down    # Stop Docker services"
    echo ""
    echo "Database:"
    echo "  python tools/scripts/main/setup/init_db.py  # Initialize database"
    echo ""
    echo "Data Collection:"
    echo "  python packages/data-collector/sources/congress_gov_collector.py"
    echo "  python packages/data-collector/sources/govinfo_collector.py"
    echo "  python packages/data-collector/sources/openstates_collector.py"
    echo ""
}

# Function to show cleanup recommendations
show_cleanup() {
    print_warning "Cleanup Recommendations:"
    echo ""
    echo "1. Review backup directories:"
    echo "   - local_work_backup/"
    echo "   - local_backup/"
    echo "   (Remove if content is preserved elsewhere)"
    echo ""
    echo "2. Consolidate documentation:"
    echo "   - packages/docs/misc/"
    echo "   - Move files to more specific documentation directories"
    echo ""
    echo "3. Remove Python cache files:"
    echo "   - find . -type d -name \"__pycache__\" -exec rm -rf {} +"
    echo "   - find . -name \"*.pyc\" -delete"
    echo ""
    echo "4. Remove temporary files:"
    echo "   - find . -name \"*.tmp\" -delete"
    echo "   - find . -name \"*.bak\" -delete"
    echo ""
    print_warning "Always backup important data before running actual deletions!"
}

# Function to show AI assistance information
show_ai_assistance() {
    echo "==========================================="
    echo "    AI Assistance Information"
    echo "==========================================="
    echo ""
    echo "This project is designed to work well with AI assistants:"
    echo ""
    echo "Key Context Files:"
    echo "├── KNOWLEDGE_BASE.md       # Comprehensive project context"
    echo "├── AGENT_SETUP_GUIDE.md    # Setup instructions for agents"
    echo "├── PROJECT_SUMMARY.md      # High-level project overview"
    echo "└── FEATURES.md            # Feature roadmap and specifications"
    echo ""
    echo "When working with AI assistants:"
    echo "1. Point them to KNOWLEDGE_BASE.md for comprehensive context"
    echo "2. Reference AGENT_SETUP_GUIDE.md for development setup"
    echo "3. Use PROJECT_SUMMARY.md for high-level understanding"
    echo "4. Consult FEATURES.md for development direction"
    echo ""
}

# Function to show next steps
show_next_steps() {
    echo "==========================================="
    echo "    Recommended Next Steps"
    echo "==========================================="
    echo ""
    echo "1. Review Documentation:"
    echo "   - Read PROJECT_SUMMARY.md for project overview"
    echo "   - Study KNOWLEDGE_BASE.md for comprehensive context"
    echo "   - Examine FEATURES.md for development roadmap"
    echo ""
    echo "2. Explore Core Components:"
    echo "   - Investigate packages/data-collector/ for data collection"
    echo "   - Review packages/rag-engine/ for AI integration"
    echo "   - Examine apps/api-server/ for backend services"
    echo ""
    echo "3. Set Up Development Environment:"
    echo "   - Install dependencies (npm install, pip install -r requirements.txt)"
    echo "   - Configure environment variables"
    echo "   - Set up database (see tools/scripts/main/setup/)"
    echo ""
    echo "4. Run Services:"
    echo "   - Start with npm run dev to launch all services"
    echo "   - Access web interface at http://localhost:3000"
    echo "   - Access API at http://localhost:8000"
    echo ""
}

# Main menu function
show_menu() {
    echo "==========================================="
    echo "    OpenDiscourse Development Helper"
    echo "==========================================="
    echo ""
    echo "Select an option:"
    echo "1. Show project overview"
    echo "2. List available services"
    echo "3. Show development commands"
    echo "4. Show cleanup recommendations"
    echo "5. Show AI assistance information"
    echo "6. Show recommended next steps"
    echo "7. Exit"
    echo ""
    read -p "Enter your choice (1-7): " choice
    echo ""
    
    case $choice in
        1)
            show_project_overview
            ;;
        2)
            list_services
            ;;
        3)
            show_commands
            ;;
        4)
            show_cleanup
            ;;
        5)
            show_ai_assistance
            ;;
        6)
            show_next_steps
            ;;
        7)
            print_success "Goodbye! Happy coding with OpenDiscourse!"
            exit 0
            ;;
        *)
            print_error "Invalid option. Please select 1-7."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

# Main execution
main() {
    check_project_root
    show_menu
}

# Run main function
main