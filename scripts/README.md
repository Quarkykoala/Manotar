# Scripts Directory

This directory contains utility scripts for setting up, testing, deploying, and maintaining the Manobal project. The scripts have been organized into subdirectories based on their functionality to improve discoverability and maintainability.

## Directory Structure

- **backend/** - Scripts related to backend setup and operations
  - `startup.sh` - Initializes and starts the backend Flask application

- **db/** - Database initialization and management scripts
  - `create_hr_user.py` - Creates an HR admin user in the database
  - `init_db.py` - Initializes the database schema and tables
  - `update_schema.py` - Updates the database schema after model changes

- **deploy/** - Deployment and maintenance scripts
  - `clean-repo.ps1` - PowerShell script to clean up repositories
  - `cleanup.bat` - Windows batch script to clean up build artifacts and temporary files

- **frontend/** - Frontend application scripts
  - `build-themes.js` - Builds the tailwind themes for the frontend
  - `install_frontend.bat` - Installs frontend dependencies
  - `run_frontend.bat` - Runs the frontend development server
  - `test_frontend.bat` - Runs frontend tests
  - `update_node.bat` - Updates Node.js packages and dependencies

- **setup/** - Project setup and configuration scripts
  - `create_structure.bat` - Creates the initial directory structure for the project
  - `fix-structure.bat` - Fixes common project structure issues
  - `setup-project.bat` - Sets up the full project (backend and frontend)
  - `setup.bat` - Sets up the basic project environment
  - `setup_and_run.bat` - Sets up the project and runs it immediately
  - `setup_frontend.bat` - Sets up only the frontend portion of the project
  - `setup_tests.bat` - Sets up the test environment

- **test/** - Testing utilities and scripts
  - `curltest.py` - Tests HTTP endpoints using requests
  - `run_tests.bat` - Runs all backend tests
  - `run_tests_with_logs.bat` - Runs tests and captures detailed logs
  - `test_mysql_connection.py` - Tests database connectivity

## Usage

To use any of these scripts, navigate to the appropriate subdirectory or call them from the project root with the appropriate path. For example:

```bash
# To run frontend setup from the project root
scripts/frontend/install_frontend.bat

# To initialize the database
scripts/db/init_db.py
```

## Adding New Scripts

When adding new scripts to this directory, please:

1. Place them in the appropriate subdirectory based on functionality
2. Follow the existing naming conventions
3. Add proper documentation at the top of the script explaining its purpose and usage
4. Update this README if necessary 