# Manobal Testing Framework

This directory contains all tests for the Manobal platform, organized according to the monorepo pattern.

## Directory Structure

- `tests/backend/` - Backend tests for API, models, and services
- `tests/frontend/` - Frontend tests for components, pages, and hooks
- `tests/integration/` - Tests that span the frontend-backend boundary
- `tests/fixtures/` - Test data and fixtures shared across tests

## Running Tests

To run all tests:

```bash
pytest
```

To run only backend tests:

```bash
pytest tests/backend
```

To run only frontend tests:

```bash
pytest tests/frontend
```

To run only integration tests:

```bash
pytest tests/integration
```

## Test Coverage

Test coverage is automatically generated when running tests and can be found in:
- Terminal output
- `coverage.xml` file (for integration with CI/CD tools)

## Adding New Tests

1. Place your test in the appropriate directory (`backend/`, `frontend/`, or `integration/`)
2. Use the appropriate fixtures from `conftest.py`
3. Name your test file with the prefix `test_` (e.g., `test_user_service.py`)
4. Name your test functions with the prefix `test_` (e.g., `test_user_creation()`)

## Test Fixtures

Common fixtures are defined in the root `conftest.py` file. Module-specific fixtures should be defined in a `conftest.py` file in the corresponding test subdirectory. 