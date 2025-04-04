#!/bin/bash
# Environment File Cleanup
#
# This script helps clean up and standardize environment files.
# It ensures .env files follow the standardized structure defined in docs/setup/environment.md.
#
# Usage: ./scripts/deploy/env_cleanup.sh

echo -e "\033[32m========================================\033[0m"
echo -e "\033[32mEnvironment Cleanup Check\033[0m"
echo -e "\033[32m========================================\033[0m"

# Don't delete any existing .env files, just make sure they follow the pattern
# This script focuses on keeping the .env.example files consistent

# Check for .env.example files at each level
MISSING=()

if [ ! -f ".env.example" ]; then
    MISSING+=("Root .env.example")
fi

if [ ! -f "backend/.env.example" ]; then
    MISSING+=("backend/.env.example")
fi

if [ ! -f "frontend/.env.example" ]; then
    MISSING+=("frontend/.env.example")
fi

if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "\033[33mThe following example environment files are missing:\033[0m"
    for FILE in "${MISSING[@]}"; do
        echo -e "\033[33m  - $FILE\033[0m"
    done
    echo -e "\033[33mPlease create these files based on the environment variable strategy documentation.\033[0m"
fi

# Check for environment files that should not be committed
echo -e "\033[32mChecking for environment files that should not be committed...\033[0m"

# Files that should not be committed
NOT_COMMITTED=(
    ".env"
    ".env.test"
    ".env.production"
    "backend/.env"
    "backend/.env.test"
    "backend/.env.production"
    "frontend/.env"
    "frontend/.env.test"
    "frontend/.env.production"
)

SHOULD_CHECK=false
for FILE in "${NOT_COMMITTED[@]}"; do
    if [ -f "$FILE" ]; then
        if [ "$SHOULD_CHECK" = false ]; then
            echo -e "\033[33mThe following environment files exist locally but should not be committed:\033[0m"
            SHOULD_CHECK=true
        fi
        echo -e "\033[33m  - $FILE\033[0m"
    fi
done

if [ "$SHOULD_CHECK" = true ]; then
    echo -e "\033[33mRun 'git check-ignore' on these files to confirm they are ignored by Git:\033[0m"
    echo -e "\033[33m  git check-ignore [file]\033[0m"
fi

# Validate environment files against examples (check for missing variables)
echo -e "\033[32m\n========================================\033[0m"
echo -e "\033[32mValidating environment files\033[0m"
echo -e "\033[32m========================================\033[0m"

# Function to extract variable names from env file
get_env_vars() {
    local file=$1
    if [ ! -f "$file" ]; then
        return
    fi
    
    grep -v '^\s*#' "$file" | grep '=' | sed 's/=.*//' | sed 's/^[[:space:]]*//'
}

# Define file pairs for validation
declare -a FILE_PAIRS=(
    ".env.example:.env"
    ".env.example:.env.test"
    ".env.example:.env.production"
    "backend/.env.example:backend/.env"
    "backend/.env.example:backend/.env.test"
    "backend/.env.example:backend/.env.production"
    "frontend/.env.example:frontend/.env"
    "frontend/.env.example:frontend/.env.test"
    "frontend/.env.example:frontend/.env.production"
)

FOUND_ISSUES=false

for PAIR in "${FILE_PAIRS[@]}"; do
    EXAMPLE_FILE=$(echo $PAIR | cut -d: -f1)
    ACTUAL_FILE=$(echo $PAIR | cut -d: -f2)
    
    if [ -f "$EXAMPLE_FILE" ] && [ -f "$ACTUAL_FILE" ]; then
        EXAMPLE_VARS=$(get_env_vars "$EXAMPLE_FILE")
        ACTUAL_VARS=$(get_env_vars "$ACTUAL_FILE")
        
        MISSING_VARS=()
        for VAR in $EXAMPLE_VARS; do
            if ! echo "$ACTUAL_VARS" | grep -q "^$VAR$"; then
                MISSING_VARS+=("$VAR")
            fi
        done
        
        if [ ${#MISSING_VARS[@]} -gt 0 ]; then
            FOUND_ISSUES=true
            echo -e "\033[33mVariables missing in $ACTUAL_FILE (from $EXAMPLE_FILE):\033[0m"
            for VAR in "${MISSING_VARS[@]}"; do
                echo -e "\033[33m  - $VAR\033[0m"
            done
            echo ""
        fi
    fi
done

if [ "$FOUND_ISSUES" = false ]; then
    echo -e "\033[32mAll environment files contain the required variables.\033[0m"
fi

echo -e "\033[32mEnvironment cleanup check complete!\033[0m"
echo -e "\033[32m========================================\033[0m" 