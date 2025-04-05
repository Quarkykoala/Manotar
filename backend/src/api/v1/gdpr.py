"""
GDPR-related API endpoints for the Manobal platform.

This module provides endpoints for handling GDPR requests,
data exports, and consent management.
"""

from datetime import datetime
from flask import Blueprint, jsonify, request, send_file, current_app
from backend.src.utils.auth import role_required, check_gdpr_compliance, validate_input
from backend.src.utils.decorators import api_route_wrapper, audit_decorator
from backend.src.utils.errors import ValidationError, NotFoundError
from backend.src.utils.gdpr import (
    anonymize_user_data, export_user_data, delete_user_data,
    process_gdpr_request, check_data_retention_compliance
)
from backend.src.models.models import db, AuthUser, GDPRRequest
import os

gdpr = Blueprint('gdpr', __name__)

@gdpr.route('/consent', methods=['POST'])
@api_route_wrapper
@check_gdpr_compliance
def update_consent():
    """Update user's data retention consent"""
    data = request.get_json()
    if not data or 'consent' not in data:
        raise ValidationError("Consent value is required")
    
    user_id = request.user_id  # Set by check_gdpr_compliance decorator
    user = AuthUser.query.get(user_id)
    if not user:
        raise NotFoundError("User not found")
    
    consent = bool(data['consent'])
    retention_months = data.get('retention_months', 24)
    
    user.set_data_retention_consent(consent, retention_months)
    db.session.commit()
    
    return jsonify({
        'message': 'Consent updated successfully',
        'consent': user.data_retention_consent,
        'expiry': user.data_retention_expiry.isoformat() if user.data_retention_expiry else None
    })

@gdpr.route('/request', methods=['POST'])
@api_route_wrapper
@check_gdpr_compliance
def create_gdpr_request():
    """Create a new GDPR request (export/delete/anonymize)"""
    data = request.get_json()
    if not data or 'request_type' not in data:
        raise ValidationError("Request type is required")
    
    request_type = data['request_type']
    if request_type not in ['export', 'delete', 'anonymize']:
        raise ValidationError("Invalid request type")
    
    user_id = request.user_id
    
    # Check for existing pending requests
    existing_request = GDPRRequest.query.filter_by(
        user_id=user_id,
        request_type=request_type,
        status='pending'
    ).first()
    
    if existing_request:
        return jsonify({
            'message': 'Request already pending',
            'request_id': existing_request.id,
            'status': existing_request.status,
            'due_date': existing_request.due_date.isoformat()
        })
    
    # Create new request
    gdpr_request = GDPRRequest(
        user_id=user_id,
        request_type=request_type,
        status='pending',
        notes=data.get('notes')
    )
    db.session.add(gdpr_request)
    db.session.commit()
    
    return jsonify({
        'message': 'Request created successfully',
        'request_id': gdpr_request.id,
        'status': gdpr_request.status,
        'due_date': gdpr_request.due_date.isoformat()
    })

@gdpr.route('/request/<int:request_id>', methods=['GET'])
@api_route_wrapper
@check_gdpr_compliance
def get_request_status(request_id):
    """Get the status of a GDPR request"""
    gdpr_request = GDPRRequest.query.get(request_id)
    if not gdpr_request:
        raise NotFoundError("Request not found")
    
    if gdpr_request.user_id != request.user_id:
        raise ValidationError("Access denied")
    
    return jsonify(gdpr_request.to_dict())

@gdpr.route('/request/<int:request_id>/process', methods=['POST'])
@api_route_wrapper
@role_required('admin', 'hr')
@audit_decorator
def process_request(request_id):
    """Process a GDPR request (admin/HR only)"""
    gdpr_request = GDPRRequest.query.get(request_id)
    if not gdpr_request:
        raise NotFoundError("Request not found")
    
    success = process_gdpr_request(request_id)
    
    return jsonify({
        'message': 'Request processed successfully' if success else 'Request processing failed',
        'status': gdpr_request.status
    })

@gdpr.route('/export/<path:filename>')
@api_route_wrapper
@check_gdpr_compliance
def download_export(filename):
    """Download a data export file"""
    # Verify the request belongs to the user
    user_id = request.user_id
    gdpr_request = GDPRRequest.query.filter_by(
        user_id=user_id,
        request_type='export',
        status='completed',
        data_url=f"/gdpr/exports/{filename}"
    ).first()
    
    if not gdpr_request:
        raise NotFoundError("Export not found or access denied")
    
    filepath = os.path.join(current_app.config['GDPR_EXPORTS_DIR'], filename)
    if not os.path.exists(filepath):
        raise NotFoundError("Export file not found")
    
    return send_file(
        filepath,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )

@gdpr.route('/retention/check', methods=['POST'])
@api_route_wrapper
@role_required('admin')
@audit_decorator
def check_retention():
    """Manually trigger data retention compliance check (admin only)"""
    check_data_retention_compliance()
    return jsonify({'message': 'Data retention check completed'}) 