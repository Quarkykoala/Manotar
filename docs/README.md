# Manobal Documentation

This directory contains comprehensive documentation for the Manobal Mental Health Platform.

## Documentation Structure

The documentation is organized into the following directories:

- **[api/](./api/)** - API documentation, including versioning strategy and endpoint references
  - **[api/v1/](./api/v1/)** - Version 1 API documentation
  - **[api/v1/openapi.yaml](./api/v1/openapi.yaml)** - OpenAPI specification for v1 API
  - **[api/README.md](./api/README.md)** - API versioning strategy and overview
- **[architecture/](./architecture/)** - System architecture documentation
- **[setup/](./setup/)** - Setup and installation guides
- **[user-guides/](./user-guides/)** - End-user guides for the platform

## Maintaining Documentation

### API Documentation

When making changes to the API:

1. Update the appropriate version's endpoint documentation in `api/vX/` directory
2. Update the OpenAPI specification in `api/vX/openapi.yaml`
3. If adding a new endpoint, ensure it follows the versioning standard (`/api/vX/...`)
4. Run the API route validation script to verify all routes are properly versioned:
   ```
   python scripts/test_api_routes.py
   ```
5. If deprecating an endpoint, add it to the deprecation notice in the relevant version docs
6. If creating a new API version:
   - Create a new directory `api/vX/`
   - Copy and modify the OpenAPI specification from the previous version
   - Update the API version README with the new version

### Architecture Documentation

When making architectural changes:

1. Update the relevant architecture diagrams
2. Document the rationale for the change
3. Update the component interaction documentation if necessary

### Setup Documentation

When changing setup or deployment procedures:

1. Update the relevant setup guide
2. Verify the updated instructions by following them in a clean environment
3. Update any scripts or configuration examples

### Reviewing and Publishing Documentation

All documentation should be reviewed quarterly, with particular attention to:

1. API endpoints and their accuracy
2. Setup instructions and environment configurations
3. Architecture diagrams and system descriptions
4. User guides for new features

## Documentation Standards

- Use Markdown for all documentation
- Use clear, concise language appropriate for the target audience
- Include code examples where relevant
- Use diagrams to explain complex concepts
- Follow a consistent formatting style
- Include version information where applicable

## API Specification Standards

For API documentation:

1. Use OpenAPI 3.0.3 specification format
2. Document request parameters, body schemas, and response schemas
3. Include examples for requests and responses
4. Document error responses
5. Use tags to group related endpoints
6. Include security requirements

## Getting Help

If you need help with documentation:

1. For API documentation, contact the API team
2. For architecture documentation, contact the architecture team
3. For user guides, contact the product team
4. For setup guides, contact the DevOps team 