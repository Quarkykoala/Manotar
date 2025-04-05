#!/bin/bash
# Setup Environment Variables
#
# This script copies the example environment files to their corresponding .env files
# for both the root directory, backend, and frontend, if they don't already exist.
#
# Usage: ./scripts/setup/setup_env.sh [environment]
# environment: development (default), test, or production

# Default to development environment if not specified
ENVIRONMENT=${1:-development}

echo -e "\033[32mSetting up environment variables for $ENVIRONMENT environment...\033[0m"

# Define the environment file suffix based on the environment
ENV_SUFFIX=""
if [ "$ENVIRONMENT" = "test" ]; then
    ENV_SUFFIX=".test"
elif [ "$ENVIRONMENT" = "production" ]; then
    ENV_SUFFIX=".production"
fi

# Function to copy example env file if target doesn't exist
copy_env_file() {
    SOURCE_FILE=$1
    TARGET_FILE=$2

    if [ -f "$TARGET_FILE" ]; then
        echo -e "\033[33mFile already exists: $TARGET_FILE\033[0m"
    else
        if cp "$SOURCE_FILE" "$TARGET_FILE"; then
            echo -e "\033[32mCreated: $TARGET_FILE\033[0m"
        else
            echo -e "\033[31mError creating $TARGET_FILE. Please check file permissions and try again.\033[0m"
        fi
    fi
}

# Root directory environment files
ROOT_ENV_EXAMPLE=".env.example"
ROOT_ENV_TARGET=".env$ENV_SUFFIX"
copy_env_file "$ROOT_ENV_EXAMPLE" "$ROOT_ENV_TARGET"

# Backend environment files
BACKEND_ENV_EXAMPLE="backend/.env.example"
BACKEND_ENV_TARGET="backend/.env$ENV_SUFFIX"
copy_env_file "$BACKEND_ENV_EXAMPLE" "$BACKEND_ENV_TARGET"

# Frontend environment files
FRONTEND_ENV_EXAMPLE="frontend/.env.example"
FRONTEND_ENV_TARGET="frontend/.env$ENV_SUFFIX"
copy_env_file "$FRONTEND_ENV_EXAMPLE" "$FRONTEND_ENV_TARGET"

echo -e "\033[32mEnvironment setup complete!\033[0m"
echo -e "\033[33mIMPORTANT: Make sure to update the created .env files with your actual configuration values.\033[0m" 