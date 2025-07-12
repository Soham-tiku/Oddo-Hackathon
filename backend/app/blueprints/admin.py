from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.user import User
from ..models.question import Question
from ..models.answer import Answer
from ..models.vote import Vote
from ..services.rbac import admin_required

bp = Blueprint('admin', __name__)

@bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = User.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': users.page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get users'}), 500

@bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    """Update user role"""
    try:
        current_user_id = get_jwt_identity()
        
        # Prevent self-role modification
        if current_user_id == user_id:
            return jsonify({'error': 'Cannot modify your own role'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        new_role = data.get('role')
        
        if new_role not in ['user', 'moderator', 'admin']:
            return jsonify({'error': 'Invalid role'}), 400
        
        user.role = new_role
        db.session.commit()
        
        return jsonify({
            'message': 'User role updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update user role'}), 500

@bp.route('/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """Activate/deactivate user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Prevent self-status modification
        if current_user_id == user_id:
            return jsonify({'error': 'Cannot modify your own status'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        is_active = data.get('is_active')
        
        if is_active is None:
            return jsonify({'error': 'is_active field is required'}), 400
        
        user.is_active = bool(is_active)
        db.session.commit()
        
        status = 'activated' if is_active else 'deactivated'
        return jsonify({
            'message': f'User {status} successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update user status'}), 500

@bp.route('/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """Get platform statistics"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        total_questions = Question.query.count()
        total_answers = Answer.query.count()
        total_votes = Vote.query.count()
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'inactive': total_users - active_users
            },
            'content': {
                'questions': total_questions,
                'answers': total_answers,
                'votes': total_votes
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get stats'}), 500
