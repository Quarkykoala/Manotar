#!/usr/bin/env python
"""
Run frontend tests with coverage reporting

This script runs frontend Jest tests with coverage reporting.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Determine project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run frontend tests with coverage')
    parser.add_argument('--watch', action='store_true', help='Run tests in watch mode')
    parser.add_argument('--component', type=str, default=None, help='Specific component to test')
    parser.add_argument('--updateSnapshot', action='store_true', help='Update test snapshots')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    return parser.parse_args()

def run_tests(args):
    """Run Jest with coverage"""
    # Change to frontend directory
    os.chdir(FRONTEND_DIR)
    
    # Prepare command
    cmd = ['npm', 'test']
    
    # Add options
    if args.verbose:
        cmd.append('--verbose')
    
    if args.watch:
        cmd.append('--watch')
    else:
        cmd.append('--coverage')
    
    if args.updateSnapshot:
        cmd.append('--updateSnapshot')
    
    if args.component:
        cmd.append(f'--testPathPattern={args.component}')
    
    # Run the command
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode

def main():
    """Main entry point"""
    args = parse_args()
    
    # Ensure frontend setup is complete
    if not (FRONTEND_DIR / "node_modules").exists():
        print("Installing frontend dependencies...")
        subprocess.run(['npm', 'install'], cwd=FRONTEND_DIR)
    
    # Run tests
    return_code = run_tests(args)
    
    # Exit with test return code
    sys.exit(return_code)

if __name__ == '__main__':
    main() 