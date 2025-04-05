#!/usr/bin/env python
"""
Run backend tests with coverage reporting

This script runs backend Pytest tests with coverage reporting.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Determine project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
TESTS_DIR = PROJECT_ROOT / "tests" / "backend"

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run backend tests with coverage')
    parser.add_argument('--xml', action='store_true', help='Generate XML coverage report')
    parser.add_argument('--html', action='store_true', help='Generate HTML coverage report')
    parser.add_argument('--path', type=str, default=None, help='Specific test path to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    return parser.parse_args()

def run_tests(args):
    """Run Pytest with coverage"""
    # Prepare command
    cmd = [
        'python', '-m', 'pytest', 
        '-xvs' if args.verbose else '-xvs',
    ]
    
    # Add coverage options
    cmd.extend([
        '--cov=backend.src',
        '--cov-report=term',
    ])
    
    # Add XML report if requested
    if args.xml:
        cmd.append('--cov-report=xml:coverage.xml')
    
    # Add HTML report if requested
    if args.html:
        cmd.append('--cov-report=html:coverage_reports/backend')
    
    # Add test path if specified, otherwise run all backend tests
    if args.path:
        cmd.append(args.path)
    else:
        cmd.append(str(TESTS_DIR))
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(PROJECT_ROOT)
    
    # Run the command
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env)
    
    return result.returncode

def main():
    """Main entry point"""
    args = parse_args()
    
    # Create coverage directory if generating reports
    if args.html:
        os.makedirs('coverage_reports/backend', exist_ok=True)
    
    # Run tests
    return_code = run_tests(args)
    
    # Exit with test return code
    sys.exit(return_code)

if __name__ == '__main__':
    main() 