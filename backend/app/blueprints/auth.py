from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import check_password_hash
from ..extensions import db, limiter
from ..models.user import User
import re
import traceback

bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Register new user."""
    try:
        data = request.get_json() or {}
        # Required fields
        for field in ('username', 'email', 'password'):
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']

        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        is_valid, msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': msg}), 400

        # Unique constraints
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 409

        # Create & commit
        user = User(username=username, email=email, role='user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(
            identity=user.id,
            additional_claims={'role': user.role, 'username': user.username}
        )
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201

    except Exception:
        db.session.rollback()
        print("❌ Registration Error:")
        traceback.print_exc()
        return jsonify({'error': 'Registration failed'}), 500

@bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Login user."""
    try:
        data = request.get_json() or {}
        identifier = (data.get('identifier') or '').strip()
        password = data.get('password') or ''

        if not identifier or not password:
            return jsonify({'error': 'Email/username and password required'}), 400

        user = User.query.filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()

        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        if getattr(user, 'is_active', True) is False:
            return jsonify({'error': 'Account is deactivated'}), 401

        access_token = create_access_token(
            identity=user.id,
            additional_claims={'role': user.role, 'username': user.username}
        )
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200

    except Exception:
        print("❌ Login Error:")
        traceback.print_exc()
        return jsonify({'error': 'Login failed'}), 500

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh token."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or getattr(user, 'is_active', True) is False:
        return jsonify({'error': 'User not found or inactive'}), 404

    new_access_token = create_access_token(
        identity=user.id,
        additional_claims={'role': user.role, 'username': user.username}
    )
    return jsonify({'access_token': new_access_token}), 200

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user."""
    return jsonify({'message': 'Logout successful'}), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()}), 200
