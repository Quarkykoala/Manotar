# Manobal Testing Guide

This document provides comprehensive guidance for testing the Manobal application, including backend, frontend, and integration testing.

## Testing Infrastructure

Manobal implements a robust testing infrastructure with the following components:

1. **Backend Testing**: Pytest-based unit and integration tests for Flask API endpoints, models, and services
2. **Frontend Testing**: Jest and React Testing Library for UI components and utilities
3. **Integration Testing**: End-to-end tests that span the frontend-backend boundary
4. **CI/CD Integration**: Automated test execution via GitHub Actions

## Test Coverage Goals

- Backend test coverage: ≥ 80%
- Frontend test coverage: ≥ 70%
- All critical user flows must be covered by integration tests

## Running Tests

### Quick Start

For convenience, we provide several scripts to run tests:

```bash
# Run all tests
scripts/test/run_all_tests.bat      # Windows
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

### Backend Tests (Pytest)

Backend tests use Pytest and are located in the `tests/backend` directory. They include:

- Unit tests for models
- Unit tests for API endpoints
- Unit tests for services (sentiment analysis, check-in flow)
- Functional tests for authentication and authorization

To run backend tests manually:

```bash
cd backend
pytest tests/backend -v
```

For test coverage:

```bash
pytest tests/backend --cov=backend --cov-report=term --cov-report=html
```

### Frontend Tests (Jest)

Frontend tests use Jest and React Testing Library and are located in `frontend/components/__tests__`, `frontend/utils/__tests__`, etc.

To run frontend tests manually:

```bash
cd frontend
npm test
```

For test coverage:

```bash
cd frontend
npm test -- --coverage
```

### Integration Tests

Integration tests verify the interaction between frontend and backend components. These tests are located in `tests/integration`.

## Writing Tests

### Backend Test Conventions

1. **File naming**: Test files should be named `test_*.py`
2. **Test class naming**: Test classes should be named `Test*`
3. **Test method naming**: Test methods should be named `test_*`
4. **Fixtures**: Common fixtures are defined in `tests/conftest.py`

Example backend test:

```python
import pytest
from backend.src.models.models import Employee

class TestEmployeeModel:
    def test_create_employee(self, db_session):
        # Arrange
        employee_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "department": "Engineering"
        }
        
        # Act
        employee = Employee(**employee_data)
        db_session.add(employee)
        db_session.commit()
        
        # Assert
        assert employee.id is not None
        assert employee.name == "John Doe"
        assert employee.email == "john@example.com"
```

### Frontend Test Conventions

1. **File naming**: Test files should be named `*.test.tsx` or `*.test.ts`
2. **Test organization**: Group related tests within `describe` blocks
3. **Test structure**: Follow Arrange-Act-Assert pattern

Example frontend test:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { ExportButton } from '../ExportButton';

describe('ExportButton', () => {
  it('renders correctly with Excel type', () => {
    // Arrange & Act
    render(<ExportButton data={[]} filename="test" type="excel" />);
    
    // Assert
    expect(screen.getByText('Export EXCEL')).toBeInTheDocument();
  });
  
  it('calls exportToExcel when clicked', () => {
    // Arrange
    const mockExport = jest.fn();
    jest.mock('@/utils/export', () => ({
      exportToExcel: mockExport
    }));
    render(<ExportButton data={[]} filename="test" type="excel" />);
    
    // Act
    fireEvent.click(screen.getByRole('button'));
    
    // Assert
    expect(mockExport).toHaveBeenCalled();
  });
});
```

## Test Database Setup

Backend tests use an in-memory SQLite database by default. The database is created fresh for each test session and populated with test data through fixtures.

If you need to test with a specific database:

1. Set the `TEST_DATABASE_URL` environment variable
2. Run tests with the `--real-db` flag

```bash
TEST_DATABASE_URL=postgresql://user:pass@localhost/test_db pytest
```

## Mocking External Services

For tests involving external services like Twilio or sentiment analysis APIs:

1. Use the `unittest.mock` library to patch external services
2. Create mock implementations in `tests/mocks/`
3. Use fixture parameters to control behavior

Example:

```python
@pytest.fixture
def mock_twilio(monkeypatch):
    class MockTwilioClient:
        def __init__(self, *args, **kwargs):
            pass
            
        def messages(self):
            return MockMessages()
    
    class MockMessages:
        def create(self, body, from_, to):
            return {"sid": "test_sid", "body": body}
    
    monkeypatch.setattr('twilio.rest.Client', MockTwilioClient)
    return MockTwilioClient
```

## CI/CD Integration

Tests are automatically run on GitHub Actions for every push and pull request. The workflow configuration is in `.github/workflows/test.yml`.

The CI process:

1. Sets up Python and Node.js environments
2. Installs dependencies
3. Runs backend tests with coverage
4. Runs frontend tests with coverage
5. Runs linting checks
6. Reports coverage statistics to Codecov

## Troubleshooting Tests

### Common Issues

1. **Database connection errors**: Ensure the test database exists and credentials are correct
2. **Missing dependencies**: Run `pip install -r requirements-test.txt` for backend and `npm install` for frontend
3. **Test isolation problems**: Check for tests modifying global state

### Debug Logging

Enable debug logging for tests:

```bash
pytest --log-cli-level=DEBUG
```

## Accessibility Testing

In addition to functional tests, we also perform:

1. **Automated accessibility testing** using Jest-Axe
2. **Manual accessibility testing** with screen readers
3. **Compliance checks** against WCAG 2.1 AA standards

## Performance Testing

For performance-sensitive components:

1. **Load testing**: Using Locust for API endpoints
2. **Rendering performance**: Using React Profiler

## Extending the Test Suite

When adding new features:

1. Write tests before implementing the feature (TDD)
2. Ensure all user flows are covered
3. Add both positive and negative test cases
4. Measure coverage to identify gaps

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) 