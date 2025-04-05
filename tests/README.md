# Manobal Tests

This directory contains tests for the Manobal application. Tests are organized into the following directories:

## Directory Structure

- `backend/`: Unit and integration tests for backend services, models, and API endpoints
- `frontend/`: Unit tests for frontend components and utilities
- `integration/`: End-to-end tests spanning the frontend and backend
- `fixtures/`: Common test fixtures and data

## Running Tests

Use the provided test scripts for convenience:

```bash
# Run all tests
scripts/test/run_all_tests.bat  # Windows
python scripts/test/run_all_tests.py  # Unix

# Run only backend tests
scripts/test/run_backend_tests.bat  # Windows
python scripts/test/run_backend_tests.py  # Unix

# Run only frontend tests
scripts/test/run_frontend_tests.bat  # Windows
python scripts/test/run_frontend_tests.py  # Unix

# Run only integration tests
scripts/test/run_integration_tests.bat  # Windows
python scripts/test/run_integration_tests.py  # Unix
```

## Configuration

Test configuration is centralized in:

- `conftest.py`: Pytest configuration and shared fixtures
- `frontend/jest.config.js`: Jest configuration for frontend tests

## Coverage Goals

- Backend test coverage: ≥ 80%
- Frontend test coverage: ≥ 70%
- All critical user flows must be covered by integration tests

## Contributing Tests

When adding new features:

1. Create appropriate test files following naming conventions
2. Follow the Arrange-Act-Assert pattern for test structure
3. Use existing fixtures where possible
4. Ensure tests are isolated and don't depend on previous test state

## Test Documentation

See the detailed [Testing Guide](../docs/testing/testing_guide.md) for:

- Best practices for writing tests
- Mocking strategies
- Troubleshooting information
- CI/CD integration details 