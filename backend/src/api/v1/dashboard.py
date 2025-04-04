"""
Dashboard API endpoints (v1)

These endpoints provide access to dashboard data including sentiment analysis,
department comparisons, time series data, and keyword statistics.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
from sqlalchemy import func, and_, desc, text

from ...utils.audit_logger import audit_decorator
from ...utils.error_handler import api_route_wrapper, NotFoundError, BadRequestError
from ...models.models import User, KeywordStat

# Create a Blueprint for the dashboard API
dashboard_bp = Blueprint('dashboard_api_v1', __name__)

def get_random_data():
    """Generate random data for demonstration purposes"""
    departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance']
    locations = ['New York', 'London', 'Delhi', 'Remote']
    
    return {
        'departments': departments,
        'locations': locations
    }

@dashboard_bp.route('/dashboard', methods=['GET'])
@api_route_wrapper
@audit_decorator("access", "dashboard_data")
def get_dashboard_data():
    """
    Get overall dashboard data with sentiment scores, departments, and locations.
    
    Returns:
        JSON with sentiment scores, departments, and locations.
    """
    # Get database connection from app
    db = current_app.extensions['sqlalchemy'].db
    
    try:
        # Get filter parameters
        department = request.args.get('department')
        location = request.args.get('location')
        
        # For now, return random data
        # In a real implementation, this would query the database for actual data
        random_data = get_random_data()
        
        # Query for department and location counts
        departments_query = db.session.query(
            User.department, 
            func.count(User.id).label('count')
        ).filter(User.department.isnot(None))
        
        locations_query = db.session.query(
            User.location, 
            func.count(User.id).label('count')
        ).filter(User.location.isnot(None))
        
        if department:
            departments_query = departments_query.filter(User.department == department)
            locations_query = locations_query.filter(User.department == department)
            
        if location:
            departments_query = departments_query.filter(User.location == location)
            locations_query = locations_query.filter(User.location == location)
        
        departments_data = departments_query.group_by(User.department).all()
        locations_data = locations_query.group_by(User.location).all()
        
        return {
            'sentiment_score': random.randint(60, 90),
            'trend': random.choice(['up', 'down', 'stable']),
            'risk_level': random.choice(['low', 'medium', 'high']),
            'mental_health_score': random.randint(60, 90),
            'departments': [{'name': d[0], 'count': d[1]} for d in departments_data] or \
                          [{'name': d, 'count': random.randint(5, 30)} for d in random_data['departments']],
            'locations': [{'name': l[0], 'count': l[1]} for l in locations_data] or \
                        [{'name': l, 'count': random.randint(5, 30)} for l in random_data['locations']]
        }
    except Exception as e:
        current_app.logger.error(f"Error in dashboard data: {str(e)}")
        # The error will be handled by the api_route_wrapper
        raise

@dashboard_bp.route('/department-comparison', methods=['GET'])
@api_route_wrapper
@audit_decorator("access", "department_comparison")
def get_department_comparison():
    """
    Get department comparison data.
    
    Returns:
        JSON with department comparison data.
    """
    try:
        # Get random data for demonstration
        random_data = get_random_data()
        departments = random_data['departments']
        
        return {
            'departments': [
                {
                    'name': dept,
                    'sentiment_score': random.randint(60, 90),
                    'trend': random.choice(['up', 'down', 'stable']),
                    'risk_level': random.choice(['low', 'medium', 'high'])
                }
                for dept in departments
            ]
        }
    except Exception as e:
        current_app.logger.error(f"Error in department comparison: {str(e)}")
        raise

@dashboard_bp.route('/time-series', methods=['GET'])
@api_route_wrapper
@audit_decorator("access", "time_series_data")
def get_time_series_data():
    """
    Get time series data for sentiment trends.
    
    Returns:
        JSON with time series data.
    """
    try:
        # Get filter parameters
        department = request.args.get('department')
        location = request.args.get('location')
        
        # Generate 30 days of random data
        today = datetime.now()
        data = []
        
        for i in range(30):
            date = today - timedelta(days=i)
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'sentiment_score': random.randint(60, 90),
                'message_count': random.randint(10, 100)
            })
        
        return {
            'time_series': data
        }
    except Exception as e:
        current_app.logger.error(f"Error in time series data: {str(e)}")
        raise

@dashboard_bp.route('/department/<department>/details', methods=['GET'])
@api_route_wrapper
@audit_decorator("access", "department_details_{department}")
def get_department_details(department):
    """
    Get detailed information for a specific department.
    
    Args:
        department: The department name
        
    Returns:
        JSON with department details.
    """
    try:
        # Validate department exists
        db = current_app.extensions['sqlalchemy'].db
        
        # Check if department exists
        dept_exists = db.session.query(User.department).filter(
            User.department == department
        ).first()
        
        if not dept_exists:
            # Use the department from random data for demo purposes
            random_data = get_random_data()
            if department not in random_data['departments']:
                raise NotFoundError(f"Department '{department}' not found")
        
        # Generate random data for demonstration
        return {
            'name': department,
            'sentiment_score': random.randint(60, 90),
            'trend': random.choice(['up', 'down', 'stable']),
            'risk_level': random.choice(['low', 'medium', 'high']),
            'employee_count': random.randint(5, 50),
            'top_keywords': [
                {'keyword': 'stress', 'count': random.randint(5, 20)},
                {'keyword': 'workload', 'count': random.randint(5, 15)},
                {'keyword': 'support', 'count': random.randint(5, 10)},
                {'keyword': 'collaboration', 'count': random.randint(3, 8)},
                {'keyword': 'balance', 'count': random.randint(2, 6)}
            ]
        }
    except NotFoundError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error in department details: {str(e)}")
        raise

@dashboard_bp.route('/keyword-stats', methods=['GET'])
@api_route_wrapper
@audit_decorator("access", "keyword_stats")
def get_keyword_stats():
    """
    Get keyword statistics across all departments.
    
    Returns:
        JSON with keyword statistics.
    """
    try:
        # Get filter parameters
        department = request.args.get('department')
        location = request.args.get('location')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Parse dates if provided
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise BadRequestError("Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise BadRequestError("Invalid end_date format. Use YYYY-MM-DD")
        
        # For demo purposes, return random data
        return {
            'keywords': [
                {'keyword': 'stress', 'count': random.randint(50, 200)},
                {'keyword': 'workload', 'count': random.randint(40, 150)},
                {'keyword': 'support', 'count': random.randint(30, 100)},
                {'keyword': 'collaboration', 'count': random.randint(20, 80)},
                {'keyword': 'balance', 'count': random.randint(10, 50)},
                {'keyword': 'communication', 'count': random.randint(10, 40)},
                {'keyword': 'motivation', 'count': random.randint(10, 30)},
                {'keyword': 'deadline', 'count': random.randint(5, 25)},
                {'keyword': 'recognition', 'count': random.randint(5, 20)},
                {'keyword': 'training', 'count': random.randint(5, 15)}
            ]
        }
    except BadRequestError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error in keyword stats: {str(e)}")
        raise
