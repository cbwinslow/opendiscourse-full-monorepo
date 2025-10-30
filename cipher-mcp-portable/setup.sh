#!/bin/bash

# Cipher MCP Server Setup Script
# This script sets up the Cipher MCP server for various AI clients

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

# Function to replace placeholders in config files
replace_placeholders() {
    local template_file=$1
    local output_file=$2
    local cipher_path=$3
    local api_key=$4
    
    if [[ ! -f "$template_file" ]]; then
        print_error "Template file not found: $template_file"
        return 1
    fi
    
    # Create output directory if it doesn't exist
    mkdir -p "$(dirname "$output_file")"
    
    # Replace placeholders
    sed "s|{CIPHER_BINARY_PATH}|$cipher_path|g" "$template_file" | \
    sed "s|{OPENROUTER_API_KEY}|$api_key|g" > "$output_file"
    
    print_success "Created: $output_file"
}

# Function to setup for specific AI client
setup_client() {
    local client_name=$1
    local config_template=$2
    local output_path=$3
    local cipher_path=$4
    local api_key=$5
    
    print_info "Setting up for $client_name..."
    
    if [[ ! -f "$config_template" ]]; then
        print_warning "Template not found for $client_name, skipping..."
        return 0
    fi
    
    replace_placeholders "$config_template" "$output_path" "$cipher_path" "$api_key"
}

# Main setup function
main() {
    print_info "Cipher MCP Server Setup Script"
    print_info "================================"
    
    # Check if running from the correct directory
    if [[ ! -d "configs" ]] || [[ ! -f "INSTALL.md" ]]; then
        print_error "Please run this script from the cipher-mcp-portable directory"
        exit 1
    fi
    
    # Get cipher binary path
    read -p "Enter the full path to cipher binary (e.g., /path/to/cipher/dist/src/app/index.cjs): " CIPHER_PATH
    
    if [[ ! -f "$CIPHER_PATH" ]]; then
        print_error "Cipher binary not found at: $CIPHER_PATH"
        exit 1
    fi
    
    # Get OpenRouter API key
    read -p "Enter your OpenRouter API key: " OPENROUTER_API_KEY
    
    if [[ -z "$OPENROUTER_API_KEY" ]]; then
        print_error "OpenRouter API key is required"
        exit 1
    fi
    
    print_info "Setting up configuration files..."
    
    # Setup for Cline (VSCode)
    setup_client "Cline" \
        "configs/cline-mcp-settings.json" \
        "/home/$(whoami)/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json" \
        "$CIPHER_PATH" \
        "$OPENROUTER_API_KEY"
    
    # Setup for Claude Desktop (macOS)
    CLAUDE_DESKTOP_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        setup_client "Claude Desktop" \
            "configs/claude-desktop-config.json" \
            "$CLAUDE_DESKTOP_CONFIG" \
            "$CIPHER_PATH" \
            "$OPENROUTER_API_KEY"
    else
        print_warning "Claude Desktop setup skipped (macOS only)"
    fi
    
    # Setup for Continue.dev
    setup_client "Continue.dev" \
        "configs/continue-dev-config.json" \
        "./my-continue-config.json" \
        "$CIPHER_PATH" \
        "$OPENROUTER_API_KEY"
    
    print_success "Setup completed successfully!"
    print_info "Next steps:"
    print_info "1. Restart your AI client"
    print_info "2. The Cipher MCP server should be available"
    print_info "3. Test the connection with: cipher_memory_search"
}

# Function to test the server
test_server() {
    print_info "Testing Cipher MCP Server..."
    
    local cipher_path=$1
    
    if [[ -z "$cipher_path" ]]; then
        read -p "Enter the full path to cipher binary: " cipher_path
    fi
    
    if [[ ! -f "$cipher_path" ]]; then
        print_error "Cipher binary not found at: $cipher_path"
        exit 1
    fi
    
    print_info "Starting server for 5 seconds..."
    timeout 5s node "$cipher_path" --mode mcp 2>&1 | head -10
    
    if [[ $? -eq 0 ]]; then
        print_success "Server started successfully!"
    else
        print_warning "Server test completed (timeout is normal)"
    fi
}

# Function to show usage
usage() {
    echo "Usage: $0 [OPTION]"
    echo "Options:"
    echo "  setup     Run the setup wizard"
    echo "  test      Test the server connection"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup   # Interactive setup"
    echo "  $0 test    # Test server connection"
}

# Main script logic
case "${1:-setup}" in
    "setup")
        main
        ;;
    "test")
        test_server "$2"
        ;;
    "help"|"-h"|"--help")
        usage
        ;;
    *)
        print_error "Unknown option: $1"
        usage
        exit 1
        ;;
esac
