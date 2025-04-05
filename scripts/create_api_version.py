#!/usr/bin/env python
"""
Script to create a new API version in the Manobal API.

This script will:
1. Create the directory structure for a new API version
2. Copy and update the OpenAPI specification
3. Create template files for the new version
4. Update the API versioning documentation
"""

import os
import sys
import shutil
import re
from datetime import datetime

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def create_directory_structure(version):
    """
    Create the directory structure for a new API version.
    
    Args:
        version: Version number (e.g., 2 for v2)
    """
    print(f"Creating directory structure for API v{version}...")
    
    # Create API directory
    api_dir = f"backend/src/api/v{version}"
    os.makedirs(api_dir, exist_ok=True)
    
    # Create docs directory
    docs_dir = f"docs/api/v{version}"
    os.makedirs(docs_dir, exist_ok=True)
    
    print(f"Created directories: {api_dir} and {docs_dir}")

def copy_openapi_spec(version):
    """
    Copy and update the OpenAPI specification for the new version.
    
    Args:
        version: Version number (e.g., 2 for v2)
    """
    print(f"Creating OpenAPI specification for API v{version}...")
    
    # Source and destination paths
    src_path = f"docs/api/v{version-1}/openapi.yaml"
    dst_path = f"docs/api/v{version}/openapi.yaml"
    
    # Check if the source exists
    if not os.path.exists(src_path):
        print(f"Error: Source OpenAPI spec not found at {src_path}")
        return
    
    # Copy the file
    shutil.copy2(src_path, dst_path)
    
    # Update the version number in the file
    with open(dst_path, 'r') as f:
        content = f.read()
    
    # Update version
    content = re.sub(r'version: ["\']?v\d+["\']?', f'version: "v{version}"', content)
    content = re.sub(r'title: ["\']?Manobal API v\d+["\']?', f'title: "Manobal API v{version}"', content)
    
    # Update server URLs
    content = re.sub(r'url: https://api\.manobal\.com/api/v\d+', f'url: https://api.manobal.com/api/v{version}', content)
    content = re.sub(r'url: http://localhost:5000/api/v\d+', f'url: http://localhost:5000/api/v{version}', content)
    
    # Write the updated content
    with open(dst_path, 'w') as f:
        f.write(content)
    
    print(f"Created OpenAPI specification: {dst_path}")

def create_template_files(version):
    """
    Create template files for the new API version.
    
    Args:
        version: Version number (e.g., 2 for v2)
    """
    print(f"Creating template files for API v{version}...")
    
    # Create __init__.py
    init_path = f"backend/src/api/v{version}/__init__.py"
    with open(init_path, 'w') as f:
        f.write(f'''"""
This file marks the v{version} API directory as a Python package.
"""

from flask import Blueprint

# Create the v{version} API blueprint
v{version}_bp = Blueprint('v{version}', __name__, url_prefix='/api/v{version}')

# Global routes
@v{version}_bp.route('/version', methods=['GET'])
def version():
    """Return the current API version information"""
    return {{
        "version": "{version}.0.0",
        "name": "Manobal API",
        "status": "stable",
        "deprecated": False,
        "documentation": "/docs/api/v{version}"
    }}
''')
    
    # Create API documentation
    docs_path = f"docs/api/v{version}.md"
    with open(docs_path, 'w') as f:
        f.write(f'''# Manobal API v{version} Documentation

This document provides information about Manobal's v{version} API endpoints, request formats, response formats, and error handling.

## Base URL

The base URL for all v{version} API endpoints is:

```
https://api.manobal.com/api/v{version}
```

For local development, use:

```
http://localhost:5000/api/v{version}
```

## Authentication

All API endpoints (except the webhook) require authentication using JWT (JSON Web Token).

**To authenticate:**

1. Obtain a JWT token by calling the `/api/v{version}/auth/login` endpoint
2. Include the token in the `Authorization` header of all requests:

```
Authorization: Bearer <your_jwt_token>
```

## Response Format

All successful responses follow a standard format:

```json
{{
  "key1": "value1",
  "key2": "value2",
  "_metadata": {{
    "timestamp": "2023-06-15T10:30:45.123Z",
    "request_id": "ab12cd34ef56",
    "execution_time_ms": 42.5
  }}
}}
```

All error responses follow a standard format:

```json
{{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "status": 400,
  "details": {{ /* Optional additional error details */ }}
}}
```

## API Version Headers

All responses include the following headers:

- `X-API-Version`: The version of the API that handled the request (e.g., "v{version}")
- `X-API-Deprecated`: Whether this API version is deprecated ("true" or "false")

## Endpoints

For detailed endpoint documentation, see the OpenAPI specification:

- [OpenAPI Specification](/docs/api/v{version}/openapi.yaml)
''')
    
    # Create a README in the docs/api/vX directory
    readme_path = f"docs/api/v{version}/README.md"
    with open(readme_path, 'w') as f:
        f.write(f'''# Manobal API v{version} Documentation

This directory contains documentation for version {version} of the Manobal API.

## Contents

- `openapi.yaml` - OpenAPI 3.0.3 specification for the v{version} API
- Additional endpoint documentation

## Changes from v{version-1}

List the major changes from the previous API version:

1. [Add changes here]
2. [Add changes here]
3. [Add changes here]

## Migration Guide

If you're migrating from v{version-1} to v{version}, follow these steps:

1. [Add migration steps here]
2. [Add migration steps here]
3. [Add migration steps here]
''')
    
    print("Created template files")

def update_api_docs(version):
    """
    Update the API versioning documentation.
    
    Args:
        version: Version number (e.g., 2 for v2)
    """
    print("Updating API versioning documentation...")
    
    # Update the API README.md
    readme_path = "docs/api/README.md"
    
    if not os.path.exists(readme_path):
        print(f"Error: API README not found at {readme_path}")
        return
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Add the new version to the Available Versions table
    version_table_match = re.search(r'## Available Versions\s+\|[^|]+\|[^|]+\|\s+\|[-:]+\|[-:]+\|(?:\s+\|[^|]+\|[^|]+\|)*', content)
    if version_table_match:
        table = version_table_match.group(0)
        today = datetime.now().strftime("%Y-%m-%d")
        new_row = f"\n| v{version} | [API v{version} Documentation](/docs/api/v{version}.md) | {today} |"
        
        # Replace the table with the updated one
        updated_table = table + new_row
        content = content.replace(table, updated_table)
    
    # Write the updated content
    with open(readme_path, 'w') as f:
        f.write(content)
    
    print(f"Updated API versioning documentation: {readme_path}")

def update_api_init(version):
    """
    Update the API __init__.py to register the new version.
    
    Args:
        version: Version number (e.g., 2 for v2)
    """
    print("Updating API initialization...")
    
    # Update the API __init__.py
    init_path = "backend/src/api/__init__.py"
    
    if not os.path.exists(init_path):
        print(f"Error: API __init__.py not found at {init_path}")
        return
    
    with open(init_path, 'r') as f:
        content = f.read()
    
    # Add the import for the new version
    import_match = re.search(r'from backend.src.api.v\d+ import v\d+_bp', content)
    if import_match:
        import_line = import_match.group(0)
        new_import = f"from backend.src.api.v{version} import v{version}_bp"
        
        # Add the new import after the existing one
        content = content.replace(import_line, f"{import_line}\n{new_import}")
    
    # Add the registration for the new version
    register_match = re.search(r'api_bp\.register_blueprint\(v\d+_bp\)', content)
    if register_match:
        register_line = register_match.group(0)
        new_register = f"api_bp.register_blueprint(v{version}_bp)"
        
        # Add the new registration after the existing one
        content = content.replace(register_line, f"{register_line}\n    {new_register}")
    
    # Write the updated content
    with open(init_path, 'w') as f:
        f.write(content)
    
    print(f"Updated API initialization: {init_path}")

def main():
    """Main function to create a new API version"""
    print("Manobal API Version Creator")
    print("===========================")
    
    # Get the version number
    if len(sys.argv) < 2:
        version = input("Enter the new API version number (e.g., 2 for v2): ")
    else:
        version = sys.argv[1]
    
    try:
        version = int(version)
    except ValueError:
        print("Error: Version must be a number")
        return
    
    # Check if the version is valid
    if version <= 1:
        print("Error: Version must be greater than 1")
        return
    
    # Check if the previous version exists
    prev_version = version - 1
    if not os.path.exists(f"backend/src/api/v{prev_version}"):
        print(f"Error: Previous version v{prev_version} not found")
        return
    
    # Check if the version already exists
    if os.path.exists(f"backend/src/api/v{version}"):
        print(f"Error: Version v{version} already exists")
        return
    
    # Create the new version
    create_directory_structure(version)
    copy_openapi_spec(version)
    create_template_files(version)
    update_api_docs(version)
    update_api_init(version)
    
    print(f"\nAPI v{version} created successfully!")
    print("\nNext steps:")
    print(f"1. Implement the API endpoints in backend/src/api/v{version}/")
    print(f"2. Update the OpenAPI specification in docs/api/v{version}/openapi.yaml")
    print(f"3. Complete the migration guide in docs/api/v{version}/README.md")
    print(f"4. Run the API route validation script: python scripts/test_api_routes.py")

if __name__ == '__main__':
    main() 