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
import string

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
    Get keyword statistics across all messages.
    
    Query Parameters:
        department (str, optional): Filter by department
        location (str, optional): Filter by location
        
    Returns:
        JSON with keyword statistics.
    """
    try:
        # Get database connection from app
        db = current_app.extensions['sqlalchemy'].db
        
        # Get filter parameters
        department = request.args.get('department')
        location = request.args.get('location')
        
        # Query for keyword stats
        query = db.session.query(
            KeywordStat.keyword,
            func.sum(KeywordStat.count).label('total_count')
        )
        
        # Apply filters
        if department:
            query = query.filter(KeywordStat.department == department)
        if location:
            query = query.filter(KeywordStat.location == location)
        
        # Group and order results
        result = query.group_by(KeywordStat.keyword)\
                     .order_by(desc('total_count'))\
                     .limit(20)\
                     .all()
        
        # Format response
        stats = [
            {
                'keyword': stat[0],
                'total_count': str(stat[1])  # Convert to string to ensure JSON serialization
            }
            for stat in result
        ]
        
        return stats
    except Exception as e:
        current_app.logger.error(f"Error getting keyword stats: {str(e)}")
        raise

@dashboard_bp.route('/sentiment-trends', methods=['GET'])
@api_route_wrapper
@audit_decorator("access", "sentiment_trends")
def get_sentiment_trends():
    """
    Get sentiment analysis trends over time.
    
    Query Parameters:
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format
        department (str, optional): Filter by department
        
    Returns:
        JSON with sentiment trend data.
    """
    try:
        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        department = request.args.get('department')
        
        # Generate sample data for now
        # In a real implementation, this would query a database
        today = datetime.now()
        data = []
        
        for i in range(30):
            date = today - timedelta(days=i)
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "sentiment_score": round(0.5 + random.random() * 0.5, 2)
            })
        
        return {"trends": data}
    except Exception as e:
        current_app.logger.error(f"Error in sentiment trends: {str(e)}")
        raise

@dashboard_bp.route('/department-metrics', methods=['GET'])
@api_route_wrapper
@audit_decorator("access", "department_metrics")
def get_department_metrics():
    """
    Get metrics aggregated by department.
    
    Query Parameters:
        department (str, optional): Filter for a specific department
        
    Returns:
        JSON with department metrics.
    """
    try:
        department = request.args.get('department')
        
        # Get database connection from app
        db = current_app.extensions['sqlalchemy'].db
        
        # Generate metrics based on whether a department is specified
        if department:
            # Check if department exists
            dept_exists = db.session.query(User.department).filter(
                User.department == department
            ).first()
            
            if not dept_exists:
                raise NotFoundError(f"Department '{department}' not found")
            
            # Generate sample metrics for the specified department
            return {
                "department_metrics": {
                    "name": department,
                    "average_sentiment": round(0.6 + random.random() * 0.3, 2),
                    "response_rate": random.randint(75, 95),
                    "engagement_score": random.randint(70, 90),
                    "employee_count": random.randint(10, 50)
                }
            }
        else:
            # Generate metrics for all departments
            random_data = get_random_data()
            department_metrics = []
            
            for dept in random_data['departments']:
                department_metrics.append({
                    "name": dept,
                    "average_sentiment": round(0.6 + random.random() * 0.3, 2),
                    "response_rate": random.randint(75, 95),
                    "engagement_score": random.randint(70, 90),
                    "employee_count": random.randint(10, 50)
                })
            
            return {"department_metrics": department_metrics}
    except NotFoundError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error in department metrics: {str(e)}")
        raise

@dashboard_bp.route('/risk-alerts', methods=['GET'])
@api_route_wrapper
@audit_decorator("access", "risk_alerts")
def get_risk_alerts():
    """
    Get current risk alerts based on sentiment analysis.
    
    Returns:
        JSON with risk alerts.
    """
    try:
        # Get random data for demonstration
        random_data = get_random_data()
        departments = random_data['departments']
        
        # Generate risk alerts for some departments
        alerts = []
        risk_levels = ["low", "medium", "high"]
        
        for dept in departments:
            if random.random() < 0.3:  # 30% chance to generate an alert
                alerts.append({
                    "level": random.choice(risk_levels),
                    "department": dept,
                    "description": random.choice([
                        "Declining sentiment trend detected",
                        "Unusual keyword frequency observed",
                        "High message volume with negative sentiment",
                        "Sudden drop in engagement"
                    ])
                })
        
        return {"alerts": alerts}
    except Exception as e:
        current_app.logger.error(f"Error in risk alerts: {str(e)}")
        raise

@dashboard_bp.route('/export-report', methods=['POST'])
@api_route_wrapper
@audit_decorator("export", "dashboard_report")
def export_report():
    """
    Generate and export analytics report.
    
    Request Body:
        type (str): Report type ("sentiment", "keywords", "engagement")
        format (str): Export format ("pdf", "csv", "json")
        time_period (str): Time period for the report
        
    Returns:
        JSON with export details.
    """
    try:
        data = request.get_json()
        
        # Validate request data
        if not data:
            raise BadRequestError("Missing request body")
        
        report_type = data.get('type', 'sentiment')
        report_format = data.get('format', 'pdf')
        time_period = data.get('time_period', 'month')
        
        # Validate parameters
        valid_types = ["sentiment", "keywords", "engagement", "comprehensive"]
        valid_formats = ["pdf", "csv", "json", "excel"]
        valid_periods = ["week", "month", "quarter", "year"]
        
        if report_type not in valid_types:
            raise BadRequestError(f"Invalid report type. Must be one of: {', '.join(valid_types)}")
        
        if report_format not in valid_formats:
            raise BadRequestError(f"Invalid report format. Must be one of: {', '.join(valid_formats)}")
        
        if time_period not in valid_periods:
            raise BadRequestError(f"Invalid time period. Must be one of: {', '.join(valid_periods)}")
        
        # Generate report URL with expiration
        report_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        expires_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        
        return {
            "status": "success",
            "report_id": report_id,
            "report_url": f"/api/v1/dashboard/reports/{report_id}.{report_format}",
            "report_type": report_type,
            "expires_at": expires_at
        }
    except BadRequestError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error in export report: {str(e)}")
        raise
