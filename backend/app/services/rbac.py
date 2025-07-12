from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..models.user import User

def role_required(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                claims = get_jwt()
                user_role = claims.get('role')
                
                if user_role not in allowed_roles:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                # Additional check: verify user is still active
                user = User.query.get(current_user_id)
                if not user or not user.is_active:
                    return jsonify({'error': 'User account is inactive'}), 401
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Authorization failed'}), 500
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator specifically for admin-only routes"""
    return role_required('admin')(f)

def moderator_or_admin_required(f):
    """Decorator for moderator and admin access"""
    return role_required('moderator', 'admin')(f)

def user_or_admin_required(f):
    """Decorator for user and admin access"""
    return role_required('user', 'admin')(f)
