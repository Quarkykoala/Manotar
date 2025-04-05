"""
Check-in API Endpoints (v1)

These endpoints provide access to check-in data and reports.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func
from ...models.models import CheckIn, Employee, User, db
from ...utils.auth import hr_required
from ...utils.audit_logger import log_audit_event
from ...services.check_in_flow import get_check_in_statistics

# Create a Blueprint for check-in API
check_ins_bp = Blueprint('check_ins', __name__)

@check_ins_bp.route('/', methods=['GET'])
@jwt_required()
@hr_required
def get_check_ins():
    """
    Get a list of check-ins with filtering and pagination
    
    Query parameters:
    - employee_id: Filter by employee ID (optional)
    - department: Filter by department (optional)
    - start_date: Filter by start date (YYYY-MM-DD) (optional)
    - end_date: Filter by end date (YYYY-MM-DD) (optional)
    - completed: Filter by completion status (true/false) (optional)
    - follow_up_required: Filter by follow-up flag (true/false) (optional)
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    """
    try:
        # Get query parameters
        employee_id = request.args.get('employee_id')
        department = request.args.get('department')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        completed = request.args.get('completed')
        follow_up = request.args.get('follow_up_required')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Build query
        query = CheckIn.query
        
        # Join with Employee for department filtering if needed
        if department:
            query = query.join(Employee, CheckIn.employee_id == Employee.id)
            query = query.filter(Employee.department == department)
        
        # Apply filters
        if employee_id:
            query = query.filter(CheckIn.employee_id == employee_id)
        
        # Parse dates if provided
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                query = query.filter(CheckIn.created_at >= start_date)
            except ValueError:
                return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                # Add a day to include the entire end date
                end_date = end_date + timedelta(days=1)
                query = query.filter(CheckIn.created_at < end_date)
            except ValueError:
                return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400
        
        # Filter by completion status
        if completed is not None:
            is_completed = completed.lower() == 'true'
            query = query.filter(CheckIn.is_completed == is_completed)
        
        # Filter by follow-up required
        if follow_up is not None:
            follow_up_required = follow_up.lower() == 'true'
            query = query.filter(CheckIn.follow_up_required == follow_up_required)
        
        # Order by creation date, newest first
        query = query.order_by(CheckIn.created_at.desc())
        
        # Execute query with pagination
        paginated_check_ins = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Format response
        result = {
            "check_ins": [],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": paginated_check_ins.total,
                "pages": paginated_check_ins.pages
            }
        }
        
        # Add employee details to check-ins
        for check_in in paginated_check_ins.items:
            check_in_data = check_in.to_dict()
            
            # Add employee info if available
            if check_in.employee_id:
                employee = Employee.query.get(check_in.employee_id)
                if employee:
                    check_in_data["employee"] = {
                        "id": employee.id,
                        "name": f"{employee.first_name} {employee.last_name}",
                        "department": employee.department,
                        "role": employee.role
                    }
            
            # Add user info if no employee linked
            if not check_in.employee_id and check_in.user_id:
                user = User.query.get(check_in.user_id)
                if user:
                    check_in_data["user"] = {
                        "id": user.id,
                        "phone_number": user.phone_number,
                        "department": user.department,
                        "location": user.location
                    }
            
            result["check_ins"].append(check_in_data)
        
        # Log this access
        current_user_id = get_jwt_identity()
        log_audit_event(
            user_id=current_user_id,
            action="viewed_check_ins",
            details=f"Retrieved check-in list with filters: {request.args}"
        )
        
        return jsonify(result), 200
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving check-ins: {str(e)}")
        return jsonify({"error": "Failed to retrieve check-ins"}), 500

@check_ins_bp.route('/<int:check_in_id>', methods=['GET'])
@jwt_required()
@hr_required
def get_check_in(check_in_id):
    """Get detailed information about a specific check-in"""
    try:
        check_in = CheckIn.query.get(check_in_id)
        
        if not check_in:
            return jsonify({"error": "Check-in not found"}), 404
        
        # Get check-in data
        check_in_data = check_in.to_dict()
        
        # Add employee info if available
        if check_in.employee_id:
            employee = Employee.query.get(check_in.employee_id)
            if employee:
                check_in_data["employee"] = {
                    "id": employee.id,
                    "name": f"{employee.first_name} {employee.last_name}",
                    "department": employee.department,
                    "role": employee.role,
                    "email": employee.email
                }
        
        # Add user info if no employee linked
        if not check_in.employee_id and check_in.user_id:
            user = User.query.get(check_in.user_id)
            if user:
                check_in_data["user"] = {
                    "id": user.id,
                    "phone_number": user.phone_number,
                    "department": user.department,
                    "location": user.location
                }
        
        # Log this access
        current_user_id = get_jwt_identity()
        log_audit_event(
            user_id=current_user_id,
            action="viewed_check_in_details",
            target=str(check_in_id),
            details=f"Retrieved check-in details for ID {check_in_id}"
        )
        
        return jsonify({"check_in": check_in_data}), 200
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving check-in {check_in_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve check-in details"}), 500

@check_ins_bp.route('/<int:check_in_id>/follow-up', methods=['PUT'])
@jwt_required()
@hr_required
def update_follow_up(check_in_id):
    """Update follow-up status and notes for a check-in"""
    try:
        check_in = CheckIn.query.get(check_in_id)
        
        if not check_in:
            return jsonify({"error": "Check-in not found"}), 404
        
        data = request.get_json()
        
        # Update follow-up fields
        if 'follow_up_required' in data:
            check_in.follow_up_required = data['follow_up_required']
        
        if 'follow_up_notes' in data:
            check_in.follow_up_notes = data['follow_up_notes']
        
        db.session.commit()
        
        # Log this update
        current_user_id = get_jwt_identity()
        log_audit_event(
            user_id=current_user_id,
            action="updated_check_in_follow_up",
            target=str(check_in_id),
            details=f"Updated follow-up for check-in ID {check_in_id}"
        )
        
        return jsonify({
            "message": "Check-in follow-up updated",
            "check_in": check_in.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating check-in {check_in_id}: {str(e)}")
        return jsonify({"error": "Failed to update check-in follow-up"}), 500

@check_ins_bp.route('/statistics', methods=['GET'])
@jwt_required()
@hr_required
def get_statistics():
    """
    Get check-in statistics and trends
    
    Query parameters:
    - department: Filter by department (optional)
    - start_date: Filter by start date (YYYY-MM-DD) (optional)
    - end_date: Filter by end date (YYYY-MM-DD) (optional)
    - group_by: Group results by ('day', 'week', 'month') (default: 'day')
    """
    try:
        # Get query parameters
        department = request.args.get('department')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        group_by = request.args.get('group_by', 'day')
        
        # Parse dates if provided
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400
        else:
            # Default to last 30 days
            start_date = datetime.utcnow() - timedelta(days=30)
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                # Add a day to include the entire end date
                end_date = end_date + timedelta(days=1)
            except ValueError:
                return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400
        else:
            # Default to current date
            end_date = datetime.utcnow()
        
        # Get overall statistics
        stats = get_check_in_statistics(
            department=department,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get time-series data based on group_by parameter
        time_series_data = []
        
        # Define time grouping SQL expression based on group_by
        if group_by == 'day':
            date_trunc = func.date(CheckIn.created_at)
        elif group_by == 'week':
            date_trunc = func.date(func.date_trunc('week', CheckIn.created_at))
        elif group_by == 'month':
            date_trunc = func.date(func.date_trunc('month', CheckIn.created_at))
        else:
            return jsonify({"error": "Invalid group_by parameter. Use 'day', 'week', or 'month'"}), 400
        
        # Base query for time series
        time_series_query = db.session.query(
            date_trunc.label('date'),
            func.avg(CheckIn.mood_score).label('avg_mood'),
            func.avg(CheckIn.stress_level).label('avg_stress'),
            func.count(CheckIn.id).label('check_in_count')
        ).filter(
            CheckIn.is_completed == True,
            CheckIn.created_at >= start_date,
            CheckIn.created_at < end_date
        )
        
        # Apply department filter if provided
        if department:
            time_series_query = time_series_query.join(
                Employee, CheckIn.employee_id == Employee.id
            ).filter(
                Employee.department == department
            )
        
        # Group by date and execute
        time_series_results = time_series_query.group_by('date').order_by('date').all()
        
        # Format time series data
        for row in time_series_results:
            date_str = row.date.isoformat() if row.date else None
            time_series_data.append({
                'date': date_str,
                'avg_mood': float(row.avg_mood) if row.avg_mood else None,
                'avg_stress': float(row.avg_stress) if row.avg_stress else None,
                'check_in_count': row.check_in_count
            })
        
        # Add time series to stats
        stats['time_series'] = time_series_data
        stats['group_by'] = group_by
        
        # Log this access
        current_user_id = get_jwt_identity()
        log_audit_event(
            user_id=current_user_id,
            action="viewed_check_in_statistics",
            details=f"Retrieved check-in statistics with filters: {request.args}"
        )
        
        return jsonify(stats), 200
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving check-in statistics: {str(e)}")
        return jsonify({"error": "Failed to retrieve check-in statistics"}), 500 