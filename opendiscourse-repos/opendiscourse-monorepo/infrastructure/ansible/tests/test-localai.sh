#!/bin/bash

# Set the base directory for LocalAI
LOCAL_AI_BASE_DIR="/opt/localai"

# Function to check if a service is active
is_service_active() {
    systemctl is-active --quiet "$1"
    return $?
}

# Function to check if a file exists and is not empty
file_exists_and_not_empty() {
    [[ -s "$1" ]]
    return $?
}

# Function to check if a URL is reachable
is_url_reachable() {
    curl -s -o /dev/null -w "%{http_code}" "$1" | grep -q "200"
    return $?
}

# Check if LocalAI service is installed
if ! is_service_active "local-ai"; then
    echo "LocalAI service is not installed or not active."
    exit 1
fi

# Check if configuration files exist and are not empty
CONFIG_FILES=(
    "${LOCAL_AI_BASE_DIR}/config/config.yaml"
    "${LOCAL_AI_BASE_DIR}/docker-compose.yml"
    "${LOCAL_AI_BASE_DIR}/.env"
)

for config_file in "${CONFIG_FILES[@]}"; do
    if ! file_exists_and_not_empty "$config_file"; then
        echo "Configuration file $config_file is missing or empty."
        exit 1
    fi
done

# Check if LocalAI API is responsive
API_URL="http://localhost:8080/v1/models"
if ! is_url_reachable "$API_URL"; then
    echo "LocalAI API is not responsive at $API_URL."
    exit 1
fi

# Check if logs are being generated
LOG_FILE="${LOCAL_AI_BASE_DIR}/logs/localai.log"
if ! file_exists_and_not_empty "$LOG_FILE"; then
    echo "Log file $LOG_FILE is missing or empty."
    exit 1
fi

echo "All checks passed. LocalAI service is installed and configured correctly."
exit 0