import pytest
import json
from app import app, db, User, KeywordStat

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_data(test_db):
    # Create test user
    user = User(
        phone_number="+1234567890",
        access_code="TEST123",
        department="Engineering",
        location="Mumbai"
    )
    test_db.session.add(user)
    test_db.session.commit()

    # Create test keyword stats
    keywords = ["stress", "workload", "deadline"]
    for keyword in keywords:
        stat = KeywordStat(
            user_id=user.id,
            department="Engineering",
            location="Mumbai",
            keyword=keyword,
            count=5
        )
        test_db.session.add(stat)
    
    test_db.session.commit()
    
    yield user  # Return user for test use
    
    # Cleanup
    KeywordStat.query.delete()
    test_db.session.delete(user)
    test_db.session.commit()

def test_dashboard_endpoint(client):
    response = client.get('/api/dashboard')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert "total_employees" in data
    assert "at_risk_departments" in data
    assert "mental_health_score" in data
    assert "keyword_occurrences" in data
    assert "departments" in data

def test_department_comparison_endpoint(client):
    response = client.get('/api/department-comparison')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert isinstance(data, list)
    assert len(data) > 0
    assert "department" in data[0]
    assert "mental_health_score" in data[0]

def test_time_series_endpoint(client):
    response = client.get('/api/time-series')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert isinstance(data, list)
    assert len(data) > 0
    assert "date" in data[0]
    assert "mental_health_score" in data[0]

def test_department_details_endpoint(client):
    response = client.get('/api/department/Engineering/details')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data["department"] == "Engineering"
    assert "total_employees" in data
    assert "mental_health_score" in data
    assert "key_metrics" in data

def test_keyword_stats_endpoint(test_client, test_app, test_db):
    with test_app.app_context():
        # Create test user
        user = User(
            phone_number="+1234567890",
            access_code="TEST123",
            department="Engineering",
            location="Mumbai"
        )
        test_db.session.add(user)
        test_db.session.commit()

        # Create test keyword stats
        keywords = ["stress", "workload", "deadline"]
        for keyword in keywords:
            stat = KeywordStat(
                user_id=user.id,
                department="Engineering",
                location="Mumbai",
                keyword=keyword,
                count=5
            )
            test_db.session.add(stat)
        test_db.session.commit()

        # Test endpoint
        response = test_client.get('/api/keyword-stats')
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response
        assert isinstance(data, list), "Response should be a list"
        assert len(data) == len(keywords), f"Expected {len(keywords)} stats, got {len(data)}"
        
        # Create a dictionary of expected counts
        expected_counts = {keyword: 5 for keyword in keywords}
        
        # Convert response to dictionary for easier comparison
        actual_counts = {stat["keyword"]: int(stat["total_count"]) for stat in data}
        
        # Compare dictionaries
        assert actual_counts == expected_counts, \
            f"Expected counts {expected_counts}, got {actual_counts}"

def test_keyword_stats_with_filters(test_client, test_app, test_db):
    with test_app.app_context():
        # Create test user and stats
        user = User(
            phone_number="+1234567890",
            access_code="TEST123",
            department="Engineering",
            location="Mumbai"
        )
        test_db.session.add(user)
        test_db.session.commit()

        keywords = ["stress", "workload", "deadline"]
        for keyword in keywords:
            stat = KeywordStat(
                user_id=user.id,
                department="Engineering",
                location="Mumbai",
                keyword=keyword,
                count=5
            )
            test_db.session.add(stat)
        test_db.session.commit()

        # Test with department filter
        response = test_client.get('/api/keyword-stats?department=Engineering')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) > 0
        
        # Test with location filter
        response = test_client.get('/api/keyword-stats?location=Mumbai')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) > 0
        
        # Test with both filters
        response = test_client.get('/api/keyword-stats?department=Engineering&location=Mumbai')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) > 0