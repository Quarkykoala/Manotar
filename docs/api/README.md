# Manobal API Documentation

This directory contains documentation for the Manobal API.

## API Versioning Strategy

The Manobal API uses versioning to ensure backward compatibility while allowing for future enhancements. All API endpoints follow this pattern:

```
/api/v{version_number}/{endpoint}
```

For example:
- `/api/v1/dashboard` - Dashboard data endpoint (v1)
- `/api/v2/dashboard` - Dashboard data endpoint (v2, when available)

## Version Headers

Every API response includes version headers:

- `X-API-Version`: The current version of the API being used
- `X-API-Deprecated`: Whether the API version is deprecated (`true` or `false`)

## Available Versions

| Version | Status      | Documentation                   | Release Date |
|---------|-------------|--------------------------------|--------------|
| v1      | Current     | [API v1 Documentation](v1.md)  | April 2024   |

## Versioning Policy

1. **Backward Compatibility**: New versions maintain backward compatibility when possible
2. **Breaking Changes**: Breaking changes require a new API version
3. **Deprecation Notice**: When a version is deprecated, a 6-month sunset period begins
4. **Sunset Period**: During the sunset period, the API remains functional but returns a deprecation warning
5. **End of Life**: After the sunset period, the API version is no longer available

## Documentation Format

Each API version includes documentation in:

1. **Markdown format** - For human-readable documentation
2. **OpenAPI/Swagger format** - For machine-readable documentation and client generation

## Using the API Documentation

- [OpenAPI specification](v1/openapi.yaml) - Machine-readable API definition
- [API v1 Documentation](v1.md) - Human-readable API documentation 