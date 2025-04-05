"""
Employee Management API Endpoints

This module provides API endpoints for managing employees in the system.
"""
from flask import Blueprint, request, jsonify, current_app, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.src.models.models import Employee, User, db, AuditLog
from backend.src.utils.auth import admin_required, hr_required
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from backend.src.utils.decorators import api_route_wrapper, audit_decorator
from backend.src.utils.errors import BadRequestError

# Create the blueprint
employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/', methods=['GET'])
@jwt_required()
def get_employees():
    """
    Get a list of employees with optional filtering
    
    Query parameters:
    - department: Filter by department
    - status: Filter by status (active, inactive, on_leave)
    - role: Filter by role
    - search: Search in names and email
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    """
    try:
        # Get query parameters
        department = request.args.get('department')
        status = request.args.get('status')
        role = request.args.get('role')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)  # Limit to 100 max
        
        # Start with base query
        query = Employee.query
        
        # Apply filters
        if department:
            query = query.filter(Employee.department == department)
        
        if status:
            query = query.filter(Employee.status == status)
            
        if role:
            query = query.filter(Employee.role == role)
            
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Employee.first_name.ilike(search_term)) | 
                (Employee.last_name.ilike(search_term)) |
                (Employee.email.ilike(search_term))
            )
        
        # Execute query with pagination
        paginated_employees = query.order_by(Employee.last_name).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format response
        result = {
            "employees": [emp.to_dict() for emp in paginated_employees.items],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": paginated_employees.total,
                "pages": paginated_employees.pages
            }
        }
        
        # Log this access
        current_user_id = get_jwt_identity()
        log = AuditLog(
            user_id=current_user_id,
            action="retrieved_employees",
            details=f"Retrieved employee list with filters: {request.args}"
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving employees: {str(e)}")
        return jsonify({"error": "Failed to retrieve employees"}), 500

@employees_bp.route('/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    """Get detailed information about a specific employee"""
    try:
        employee = Employee.query.get(employee_id)
        
        if not employee:
            return jsonify({"error": "Employee not found"}), 404
            
        # Log this access
        current_user_id = get_jwt_identity()
        log = AuditLog(
            user_id=current_user_id,
            action="retrieved_employee",
            target=str(employee_id),
            details=f"Retrieved employee details for ID {employee_id}"
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({"employee": employee.to_dict()}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving employee {employee_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve employee details"}), 500

@employees_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required  # Only admins can create employees
def create_employee():
    """Create a new employee record"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'phone_number']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "error": "Missing required fields", 
                "missing": missing_fields
            }), 400
            
        # Create or get user by phone number
        user = User.query.filter_by(phone_number=data['phone_number']).first()
        
        if not user:
            # Create new user if doesn't exist
            user = User(
                phone_number=data['phone_number'],
                department=data.get('department'),
                location=data.get('location')
            )
            db.session.add(user)
            db.session.flush()  # Get ID without committing
        
        # Create employee record
        employee = Employee(
            user_id=user.id,
            employee_id=data.get('employee_id'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email'),
            department=data.get('department'),
            role=data.get('role'),
            manager_id=data.get('manager_id'),
            status=data.get('status', 'active'),
            join_date=datetime.strptime(data['join_date'], '%Y-%m-%d').date() if 'join_date' in data else None
        )
        
        db.session.add(employee)
        
        # Log this action
        current_user_id = get_jwt_identity()
        log = AuditLog(
            user_id=current_user_id,
            action="created_employee",
            target=f"{employee.first_name} {employee.last_name}",
            details=f"Created new employee record with phone {data['phone_number']}"
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            "message": "Employee created successfully",
            "employee": employee.to_dict()
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f"Database integrity error: {str(e)}")
        return jsonify({"error": "Employee with this information already exists"}), 409
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating employee: {str(e)}")
        return jsonify({"error": "Failed to create employee"}), 500

@employees_bp.route('/<int:employee_id>', methods=['PUT'])
@jwt_required()
@hr_required  # HR or higher role required
def update_employee(employee_id):
    """Update an existing employee record"""
    try:
        employee = Employee.query.get(employee_id)
        
        if not employee:
            return jsonify({"error": "Employee not found"}), 404
            
        data = request.get_json()
        
        # Update user fields if they exist
        if employee.user and 'phone_number' in data:
            employee.user.phone_number = data['phone_number']
            
        # Update employee fields
        updateable_fields = [
            'employee_id', 'first_name', 'last_name', 'email', 
            'department', 'role', 'manager_id', 'status'
        ]
        
        for field in updateable_fields:
            if field in data:
                setattr(employee, field, data[field])
                
        # Handle date separately
        if 'join_date' in data and data['join_date']:
            employee.join_date = datetime.strptime(data['join_date'], '%Y-%m-%d').date()
            
        # Log this action
        current_user_id = get_jwt_identity()
        log = AuditLog(
            user_id=current_user_id,
            action="updated_employee",
            target=str(employee_id),
            details=f"Updated employee record for {employee.first_name} {employee.last_name}"
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            "message": "Employee updated successfully",
            "employee": employee.to_dict()
        }), 200
        
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f"Database integrity error: {str(e)}")
        return jsonify({"error": "Update would violate data integrity"}), 409
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating employee {employee_id}: {str(e)}")
        return jsonify({"error": "Failed to update employee"}), 500

@employees_bp.route('/<int:employee_id>', methods=['DELETE'])
@jwt_required()
@admin_required  # Only admins can delete employees
def delete_employee(employee_id):
    """
    Soft delete an employee by changing status to 'inactive'
    
    Note: We don't actually delete the record to maintain data integrity
    and audit trail.
    """
    try:
        employee = Employee.query.get(employee_id)
        
        if not employee:
            return jsonify({"error": "Employee not found"}), 404
            
        # Soft delete by changing status
        employee.status = 'inactive'
        
        # Log this action
        current_user_id = get_jwt_identity()
        log = AuditLog(
            user_id=current_user_id,
            action="deleted_employee",
            target=str(employee_id),
            details=f"Soft-deleted employee {employee.first_name} {employee.last_name}"
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            "message": "Employee successfully deactivated",
            "employee_id": employee_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting employee {employee_id}: {str(e)}")
        return jsonify({"error": "Failed to delete employee"}), 500

@employees_bp.route('/import', methods=['POST'])
@api_route_wrapper
@audit_decorator("import", "employee_data")
def import_employees():
    """
    Import employee data in bulk.
    
    Request Body:
    {
        "employees": [
            {
                "phone_number": "+1234567890",
                "name": "John Doe",
                "department": "Engineering",
                "location": "Mumbai"
            },
            ...
        ],
        "skip_existing": true/false
    }
    
    Returns:
        JSON with import statistics
    """
    try:
        # Get database connection
        db = current_app.extensions['sqlalchemy'].db
        
        # Get request data
        data = request.get_json()
        
        if not data or 'employees' not in data:
            raise BadRequestError("Missing required field: employees")
            
        employee_data = data.get('employees', [])
        skip_existing = data.get('skip_existing', True)
        
        if not isinstance(employee_data, list):
            raise BadRequestError("Employees must be a list")
            
        if len(employee_data) == 0:
            raise BadRequestError("Employees list cannot be empty")
            
        # Track import statistics
        imported = 0
        skipped = 0
        failed = 0
        failures = []
        
        # Process each employee
        for emp in employee_data:
            try:
                # Validate required fields
                if 'phone_number' not in emp:
                    skipped += 1
                    failures.append({
                        "index": employee_data.index(emp),
                        "reason": "Missing phone_number field",
                        "employee": emp
                    })
                    continue
                    
                # Clean phone number
                phone = emp['phone_number']
                if phone.startswith('whatsapp:'):
                    phone = phone[9:]
                    
                # Check if employee exists
                existing = db.session.query(User).filter_by(phone_number=phone).first()
                
                if existing and skip_existing:
                    skipped += 1
                    continue
                    
                if existing:
                    # Update existing employee
                    if 'department' in emp:
                        existing.department = emp['department']
                    if 'location' in emp:
                        existing.location = emp['location']
                    
                    db.session.commit()
                    imported += 1
                else:
                    # Create new employee
                    access_code = generate_access_code()
                    
                    new_user = User(
                        phone_number=phone,
                        access_code=access_code,
                        department=emp.get('department'),
                        location=emp.get('location')
                    )
                    
                    db.session.add(new_user)
                    db.session.commit()
                    imported += 1
                    
            except Exception as e:
                failed += 1
                failures.append({
                    "index": employee_data.index(emp),
                    "reason": str(e),
                    "employee": emp
                })
                db.session.rollback()
                
        # Return import statistics
        return {
            "status": "success",
            "imported": imported,
            "skipped": skipped,
            "failed": failed,
            "failures": failures if failed > 0 else None
        }
                
    except BadRequestError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error importing employees: {str(e)}")
        raise

@employees_bp.route('/export', methods=['GET'])
@api_route_wrapper
@audit_decorator("export", "employee_data")
def export_employees():
    """
    Export employee data.
    
    Query Parameters:
        department (str): Filter by department
        location (str): Filter by location
        format (str): Export format (json, csv)
        
    Returns:
        JSON with employee data or a CSV file download
    """
    try:
        # Get database connection
        db = current_app.extensions['sqlalchemy'].db
        
        # Get query parameters
        department = request.args.get('department')
        location = request.args.get('location')
        export_format = request.args.get('format', 'json')
        
        # Validate format
        if export_format not in ['json', 'csv']:
            raise BadRequestError("Invalid format. Must be 'json' or 'csv'")
            
        # Build query
        query = db.session.query(User)
        
        if department:
            query = query.filter(User.department == department)
            
        if location:
            query = query.filter(User.location == location)
            
        # Execute query
        employees = query.all()
        
        # Format results
        employee_data = []
        for emp in employees:
            employee_data.append({
                "id": emp.id,
                "phone_number": emp.phone_number,
                "department": emp.department,
                "location": emp.location,
                "created_at": emp.created_at.isoformat() if emp.created_at else None
            })
            
        # Return results in requested format
        if export_format == 'json':
            return {"employees": employee_data}
        else:
            # CSV format
            csv_data = "id,phone_number,department,location,created_at\n"
            for emp in employee_data:
                csv_data += f"{emp['id']},{emp['phone_number']},{emp['department'] or ''},{emp['location'] or ''},{emp['created_at'] or ''}\n"
                
            response = make_response(csv_data)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename=employees.csv'
            return response
            
    except BadRequestError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error exporting employees: {str(e)}")
        raise

@employees_bp.route('/departments', methods=['GET'])
@api_route_wrapper
@audit_decorator("access", "department_list")
def get_departments():
    """
    Get a list of all departments.
    
    Returns:
        JSON with department list
    """
    try:
        # Get database connection
        db = current_app.extensions['sqlalchemy'].db
        
        # Query for unique departments
        departments = db.session.query(User.department).filter(User.department.isnot(None)).distinct().all()
        
        # Format results
        department_list = [dept[0] for dept in departments]
        
        return {"departments": department_list}
            
    except Exception as e:
        current_app.logger.error(f"Error getting departments: {str(e)}")
        raise

@employees_bp.route('/locations', methods=['GET'])
@api_route_wrapper
@audit_decorator("access", "location_list")
def get_locations():
    """
    Get a list of all locations.
    
    Returns:
        JSON with location list
    """
    try:
        # Get database connection
        db = current_app.extensions['sqlalchemy'].db
        
        # Query for unique locations
        locations = db.session.query(User.location).filter(User.location.isnot(None)).distinct().all()
        
        # Format results
        location_list = [loc[0] for loc in locations]
        
        return {"locations": location_list}
            
    except Exception as e:
        current_app.logger.error(f"Error getting locations: {str(e)}")
        raise 