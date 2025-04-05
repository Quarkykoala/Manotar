#!/usr/bin/env python
"""
Run all tests

This script runs all tests (backend, frontend, and integration) with coverage reporting.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Determine project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run all tests with coverage')
    parser.add_argument('--skip-backend', action='store_true', help='Skip backend tests')
    parser.add_argument('--skip-frontend', action='store_true', help='Skip frontend tests')
    parser.add_argument('--skip-integration', action='store_true', help='Skip integration tests')
    parser.add_argument('--xml', action='store_true', help='Generate XML coverage reports')
    parser.add_argument('--html', action='store_true', help='Generate HTML coverage reports')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    return parser.parse_args()

def run_backend_tests(args):
    """Run backend tests"""
    script_path = PROJECT_ROOT / "scripts" / "test" / "run_backend_tests.py"
    
    cmd = [sys.executable, str(script_path)]
    
    if args.xml:
        cmd.append('--xml')
    
    if args.html:
        cmd.append('--html')
    
    if args.verbose:
        cmd.append('--verbose')
    
    print("\n📋 Running backend tests...")
    result = subprocess.run(cmd)
    
    return result.returncode

def run_frontend_tests(args):
    """Run frontend tests"""
    script_path = PROJECT_ROOT / "scripts" / "test" / "run_frontend_tests.py"
    
    cmd = [sys.executable, str(script_path)]
    
    if args.verbose:
        cmd.append('--verbose')
    
    print("\n📋 Running frontend tests...")
    result = subprocess.run(cmd)
    
    return result.returncode

def run_integration_tests(args):
    """Run integration tests"""
    script_path = PROJECT_ROOT / "scripts" / "test" / "run_integration_tests.py"
    
    cmd = [sys.executable, str(script_path)]
    
    if args.verbose:
        cmd.append('--verbose')
    
    print("\n📋 Running integration tests...")
    result = subprocess.run(cmd)
    
    return result.returncode

def main():
    """Main entry point"""
    args = parse_args()
    
    # Create reports directory
    if args.html:
        os.makedirs('coverage_reports', exist_ok=True)
    
    # Track overall success
    success = True
    
    # Run backend tests
    if not args.skip_backend:
        backend_result = run_backend_tests(args)
        if backend_result != 0:
            success = False
            print("❌ Backend tests failed")
        else:
            print("✅ Backend tests passed")
    
    # Run frontend tests
    if not args.skip_frontend:
        frontend_result = run_frontend_tests(args)
        if frontend_result != 0:
            success = False
            print("❌ Frontend tests failed")
        else:
            print("✅ Frontend tests passed")
    
    # Run integration tests
    if not args.skip_integration:
        integration_result = run_integration_tests(args)
        if integration_result != 0:
            success = False
            print("❌ Integration tests failed")
        else:
            print("✅ Integration tests passed")
    
    # Print overall result
    print("\n" + "=" * 40)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 40)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 