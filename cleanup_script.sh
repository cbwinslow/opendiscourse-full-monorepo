#!/bin/bash
# cleanup_script.sh - Script to help organize and clean up the OpenDiscourse project

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
    if [ ! -f "README.md" ] || [ ! -d "packages" ]; then
        print_error "This script must be run from the OpenDiscourse project root directory"
        print_error "Current directory: $(pwd)"
        exit 1
    fi
}

# Function to show what will be cleaned up
show_cleanup_plan() {
    echo "==========================================="
    echo "    OpenDiscourse Directory Cleanup Plan"
    echo "==========================================="
    echo ""
    print_warning "This script will help organize and clean up the project directory."
    echo ""
    echo "Files and directories that will be reviewed:"
    echo "1. ${YELLOW}local_work_backup/${NC} - Contains original work (review before removal)"
    echo "2. ${YELLOW}local_backup/${NC} - Contains original files (review before removal)"
    echo "3. ${YELLOW}_completed/${NC} - Completed task files"
    echo "4. ${YELLOW}duplicate documentation files${NC} - Consolidate in packages/docs/"
    echo "5. ${YELLOW}temporary files${NC} - Remove .tmp, .bak, etc."
    echo "6. ${YELLOW}Python cache files${NC} - Remove __pycache__, *.pyc"
    echo ""
    print_warning "⚠️  ALWAYS REVIEW FILES BEFORE DELETING!"
    echo ""
    read -p "Continue with cleanup? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleanup cancelled by user"
        exit 0
    fi
}

# Function to backup important files before cleanup
backup_important_files() {
    print_status "Backing up potentially important files..."
    
    # Create backup directory if it doesn't exist
    if [ ! -d "cleanup_backup" ]; then
        mkdir -p cleanup_backup
        print_success "Created cleanup_backup directory"
    fi
    
    # Backup key documentation that might be duplicated
    find . -name "*.md" -not -path "./cleanup_backup/*" -not -path "./node_modules/*" -not -path "./.git/*" | head -20 | while read file; do
        # Skip files already in packages/docs/
        if [[ ! "$file" =~ ^\./packages/docs/ ]]; then
            cp "$file" "cleanup_backup/$(basename "$file")" 2>/dev/null || true
        fi
    done
    
    print_success "Backed up potentially important files to cleanup_backup/"
}

# Function to remove duplicate documentation
consolidate_docs() {
    print_status "Consolidating documentation files..."
    
    # Count duplicate files before removal
    duplicate_count=$(find . -name "*.md" -not -path "./packages/docs/*" -not -path "./node_modules/*" -not -path "./.git/*" -not -path "./cleanup_backup/*" | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        print_warning "Found $duplicate_count documentation files outside packages/docs/"
        print_warning "These should be moved to appropriate locations in packages/docs/ or removed if duplicates"
        
        # Show some examples
        echo "Examples of documentation files to review:"
        find . -name "*.md" -not -path "./packages/docs/*" -not -path "./node_modules/*" -not -path "./.git/*" -not -path "./cleanup_backup/*" | head -10
        
        echo ""
        read -p "Would you like to move these files to packages/docs/misc/? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            mkdir -p packages/docs/misc/cleanup_duplicates
            find . -name "*.md" -not -path "./packages/docs/*" -not -path "./node_modules/*" -not -path "./.git/*" -not -path "./cleanup_backup/*" | while read file; do
                if [ -f "$file" ]; then
                    mv "$file" "packages/docs/misc/cleanup_duplicates/$(basename "$file")" 2>/dev/null || true
                fi
            done
            print_success "Moved documentation files to packages/docs/misc/cleanup_duplicates/"
        else
            print_status "Skipping documentation consolidation"
        fi
    else
        print_success "No duplicate documentation files found"
    fi
}

# Function to remove temporary and cache files
remove_temp_files() {
    print_status "Removing temporary and cache files..."
    
    # Python cache files
    find . -type d -name "__pycache__" -not -path "./node_modules/*" -not -path "./.git/*" | xargs rm -rf 2>/dev/null || true
    find . -name "*.pyc" -not -path "./node_modules/*" -not -path "./.git/*" | xargs rm -f 2>/dev/null || true
    find . -name "*.pyo" -not -path "./node_modules/*" -not -path "./.git/*" | xargs rm -f 2>/dev/null || true
    find . -name "*.pyd" -not -path "./node_modules/*" -not -path "./.git/*" | xargs rm -f 2>/dev/null || true
    
    # Temporary files
    find . -name "*.tmp" -not -path "./node_modules/*" -not -path "./.git/*" | xargs rm -f 2>/dev/null || true
    find . -name "*.bak" -not -path "./node_modules/*" -not -path "./.git/*" | xargs rm -f 2>/dev/null || true
    find . -name "*.log" -not -path "./node_modules/*" -not -path "./.git/*" | xargs rm -f 2>/dev/null || true
    
    # Node.js cache
    find . -name "node_modules" -type d -prune | xargs rm -rf 2>/dev/null || true
    
    # Distribution directories
    find . -name "dist" -type d -prune | xargs rm -rf 2>/dev/null || true
    find . -name "build" -type d -prune | xargs rm -rf 2>/dev/null || true
    
    print_success "Removed temporary and cache files"
}

# Function to clean up local backup directories
cleanup_local_backups() {
    print_status "Reviewing local backup directories..."
    
    if [ -d "local_work_backup" ]; then
        print_warning "local_work_backup/ directory found with $(du -sh local_work_backup | cut -f1) of data"
        echo "Contents:"
        ls -la local_work_backup/ | head -10
        echo ""
        read -p "Remove local_work_backup/ directory? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf local_work_backup/
            print_success "Removed local_work_backup/ directory"
        else
            print_status "Keeping local_work_backup/ directory"
        fi
    fi
    
    if [ -d "local_backup" ]; then
        print_warning "local_backup/ directory found with $(du -sh local_backup | cut -f1) of data"
        echo "Contents:"
        ls -la local_backup/ | head -10
        echo ""
        read -p "Remove local_backup/ directory? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf local_backup/
            print_success "Removed local_backup/ directory"
        else
            print_status "Keeping local_backup/ directory"
        fi
    fi
}

# Function to clean up completed directories
cleanup_completed_dirs() {
    print_status "Reviewing completed directories..."
    
    if [ -d "_completed" ]; then
        print_warning "_completed/ directory found"
        echo "Contents:"
        ls -la _completed/
        echo ""
        read -p "Remove _completed/ directory? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf _completed/
            print_success "Removed _completed/ directory"
        else
            print_status "Keeping _completed/ directory"
        fi
    fi
}

# Function to show final cleanup summary
show_cleanup_summary() {
    echo ""
    echo "==========================================="
    echo "    OpenDiscourse Directory Cleanup Summary"
    echo "==========================================="
    echo ""
    print_success "Cleanup process completed!"
    echo ""
    echo "What was done:"
    echo "1. ✓ Backed up potentially important files to cleanup_backup/"
    echo "2. ✓ Consolidated documentation files (if requested)"
    echo "3. ✓ Removed temporary and cache files"
    echo "4. ✓ Reviewed local backup directories (kept or removed based on user input)"
    echo "5. ✓ Reviewed completed directories (kept or removed based on user input)"
    echo ""
    print_warning "Remember to:"
    echo "- Review the cleanup_backup/ directory and remove when no longer needed"
    echo "- Check packages/docs/misc/cleanup_duplicates/ for any important files that need proper placement"
    echo "- Update any documentation or scripts that referenced moved files"
    echo ""
    print_success "Your project directory is now cleaner and more organized!"
}

# Main function
main() {
    check_project_root
    show_cleanup_plan
    backup_important_files
    consolidate_docs
    remove_temp_files
    cleanup_local_backups
    cleanup_completed_dirs
    show_cleanup_summary
}

# Run main function
main