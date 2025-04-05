#!/usr/bin/env python
"""
Run integration tests

This script runs integration tests that span the frontend-backend boundary.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Determine project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TESTS_DIR = PROJECT_ROOT / "tests" / "integration"

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run integration tests')
    parser.add_argument('--path', type=str, default=None, help='Specific test path to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    return parser.parse_args()

def run_tests(args):
    """Run Pytest integration tests"""
    # Prepare command
    cmd = [
        'python', '-m', 'pytest',
        '-xvs' if args.verbose else '-xvs',
    ]
    
    # Add test path if specified, otherwise run all integration tests
    if args.path:
        cmd.append(args.path)
    else:
        cmd.append(str(TESTS_DIR))
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(PROJECT_ROOT)
    env['INTEGRATION_TEST'] = 'true'
    
    # Run the command
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env)
    
    return result.returncode

def main():
    """Main entry point"""
    args = parse_args()
    
    # Ensure backend and frontend are set up for integration tests
    
    # Start backend in test mode (background process)
    print("Starting backend server for integration tests...")
    # This part would normally start a backend server process
    # for integration testing, but is mocked for now
    
    try:
        # Run tests
        return_code = run_tests(args)
    finally:
        # Clean up any running processes
        print("Cleaning up integration test environment...")
        # This part would normally stop the backend server
    
    # Exit with test return code
    sys.exit(return_code)

if __name__ == '__main__':
    main() 