#!/usr/bin/env python
"""
Script to test and verify API routes in the Manobal API.

This script will:
1. Create a test Flask application
2. Register the API blueprints
3. List all registered routes
4. Validate that routes follow the versioning standard
"""

import sys
import os
import json
from collections import defaultdict

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.app import create_app

def get_route_map(app):
    """
    Extract all registered routes from the Flask app.
    
    Args:
        app: Flask application instance
    
    Returns:
        Dictionary mapping URL rules to endpoint names and methods
    """
    routes = defaultdict(list)
    
    for rule in app.url_map.iter_rules():
        routes[rule.rule].append({
            'endpoint': rule.endpoint,
            'methods': sorted(list(rule.methods - {'HEAD', 'OPTIONS'}))
        })
    
    return routes

def validate_route_versioning(routes):
    """
    Validate that API routes follow the versioning standard.
    
    Args:
        routes: Dictionary mapping URL rules to endpoint names and methods
    
    Returns:
        Tuple of (valid_routes, invalid_routes)
    """
    api_routes = {route: data for route, data in routes.items() if route.startswith('/api')}
    
    valid_routes = {}
    invalid_routes = {}
    
    for route, data in api_routes.items():
        # Skip internal Flask routes and static files
        if any(part in route for part in ['static', 'favicon']):
            continue
            
        # Check if the route follows the versioning standard
        parts = route.split('/')
        if len(parts) >= 3 and parts[1] == 'api' and parts[2].startswith('v'):
            # This is a properly versioned route
            valid_routes[route] = data
        else:
            # This route does not follow the versioning standard
            invalid_routes[route] = data
    
    return valid_routes, invalid_routes

def group_routes_by_version(routes):
    """
    Group routes by API version.
    
    Args:
        routes: Dictionary mapping URL rules to endpoint names and methods
    
    Returns:
        Dictionary mapping API versions to routes
    """
    version_groups = defaultdict(dict)
    
    for route, data in routes.items():
        parts = route.split('/')
        if len(parts) >= 3 and parts[1] == 'api' and parts[2].startswith('v'):
            version = parts[2]
            version_groups[version][route] = data
    
    return version_groups

def print_route_summary(routes, title):
    """
    Print a summary of routes.
    
    Args:
        routes: Dictionary mapping URL rules to endpoint names and methods
        title: Title for the summary
    """
    print(f"\n{title} ({len(routes)})")
    print("=" * (len(title) + 4))
    
    for route in sorted(routes.keys()):
        for data in routes[route]:
            methods_str = ', '.join(data['methods'])
            print(f"{route} => {data['endpoint']} [{methods_str}]")

def main():
    """Main function to test and verify API routes"""
    print("Manobal API Route Validation")
    print("============================")
    
    # Create test app
    print("\nCreating test application...")
    app = create_app({'TESTING': True})
    
    # Get all routes
    with app.app_context():
        routes = get_route_map(app)
        
        # Validate route versioning
        valid_routes, invalid_routes = validate_route_versioning(routes)
        
        # Group valid routes by version
        version_groups = group_routes_by_version(valid_routes)
        
        # Print summaries
        for version, routes in version_groups.items():
            print_route_summary(routes, f"API {version} Routes")
        
        if invalid_routes:
            print_route_summary(invalid_routes, "Non-Versioned API Routes")
            print("\nWARNING: Found API routes that do not follow the versioning standard!")
            print("These routes should be updated to follow the /api/vX/... pattern.")
        else:
            print("\nAll API routes follow the versioning standard!")
            
        # Output version summary
        print("\nAPI Version Summary")
        print("=================")
        for version, routes in version_groups.items():
            print(f"{version}: {len(routes)} routes")
        
        # Write routes to JSON file for documentation
        routes_data = {
            'versions': {version: list(routes.keys()) for version, routes in version_groups.items()},
            'invalid_routes': list(invalid_routes.keys()) if invalid_routes else []
        }
        
        with open('docs/api/routes.json', 'w') as f:
            json.dump(routes_data, f, indent=2)
            
        print("\nRoute data written to docs/api/routes.json")

if __name__ == '__main__':
    main() 