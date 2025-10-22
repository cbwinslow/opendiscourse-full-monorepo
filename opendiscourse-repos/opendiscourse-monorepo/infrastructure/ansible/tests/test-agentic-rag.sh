#!/bin/bash

# Test Agentic RAG Service Deployment

# Variables
ANSIBLE_PLAYBOOK="ansible/playbooks/test-agentic-rag.yml"
INVENTORY="ansible/inventory/test/agentic-rag"

# Function to run a test
run_test() {
    local test_name=$1
    local command=$2
    local expected_output=$3

    echo "Running test: $test_name"
    output=$(eval $command)
    if [[ "$output" == *"$expected_output"* ]]; then
        echo "Test $test_name passed."
    else
        echo "Test $test_name failed. Expected: $expected_output, Got: $output"
        exit 1
    fi
}

# Test 1: Service Installation
run_test "Service Installation" "ansible-playbook -i $INVENTORY $ANSIBLE_PLAYBOOK --tags install" "changed=0.*failed=0"

# Test 2: Service Configuration
run_test "Service Configuration" "ansible-playbook -i $INVENTORY $ANSIBLE_PLAYBOOK --tags configure" "changed=0.*failed=0"

# Test 3: Service Startup
run_test "Service Startup" "ansible-playbook -i $INVENTORY $ANSIBLE_PLAYBOOK --tags start" "changed=0.*failed=0"

# Test 4: Service Health
run_test "Service Health" "ansible-playbook -i $INVENTORY $ANSIBLE_PLAYBOOK --tags health" "healthy"

# Test 5: Service Logs
run_test "Service Logs" "ansible-playbook -i $INVENTORY $ANSIBLE_PLAYBOOK --tags logs" "log file exists"

# Test 6: Service Scaling
run_test "Service Scaling" "ansible-playbook -i $INVENTORY $ANSIBLE_PLAYBOOK --tags scale" "scaled successfully"

# Test 7: Service Teardown
run_test "Service Teardown" "ansible-playbook -i $INVENTORY $ANSIBLE_PLAYBOOK --tags teardown" "changed=0.*failed=0"

echo "All tests passed."