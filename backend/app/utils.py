import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
import hashlib
import secrets
import string
import re

# =============================================================================
# JWT Helper Functions
# =============================================================================

def generate_access_token(user_id, additional_claims=None):
    """Generate JWT access token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    
    if additional_claims:
        payload.update(additional_claims)
    
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

def generate_refresh_token(user_id):
    """Generate JWT refresh token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

def verify_token(token, token_type='access'):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        
        if payload.get('type') != token_type:
            return None
        
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_token_from_header():
    """Extract token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        token_type, token = auth_header.split(' ')
        if token_type.lower() != 'bearer':
            return None
        return token
    except ValueError:
        return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Add user_id to kwargs
        kwargs['current_user_id'] = payload['user_id']
        return f(*args, **kwargs)
    
    return decorated

# =============================================================================
# Password Hashing and Verification
# =============================================================================

def hash_password(password, rounds=12):
    """Hash password using bcrypt"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    salt = bcrypt.gensalt(rounds=rounds)
    return bcrypt.hashpw(password, salt).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify password against hash"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password, hashed_password)

def generate_secure_password(length=12):
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    
    # Ensure password contains at least one of each required character type
    while not all([
        any(c.islower() for c in password),
        any(c.isupper() for c in password),
        any(c.isdigit() for c in password),
        any(c in "!@#$%^&*" for c in password)
    ]):
        password = ''.join(secrets.choice(characters) for _ in range(length))
    
    return password

def validate_password_strength(password):
    """Validate password strength and return errors"""
    errors = []
    
    if len(password) < 8:
        errors.append('Password must be at least 8 characters long')
    
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        errors.append('Password must contain at least one number')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character')
    
    return errors

# =============================================================================
# Security Utilities
# =============================================================================

def generate_csrf_token():
    """Generate CSRF token"""
    return secrets.token_hex(32)

def verify_csrf_token(token, session_token):
    """Verify CSRF token"""
    return secrets.compare_digest(token, session_token)

def generate_api_key(user_id):
    """Generate API key for user"""
    timestamp = str(int(datetime.utcnow().timestamp()))
    data = f"{user_id}:{timestamp}:{secrets.token_hex(16)}"
    return hashlib.sha256(data.encode()).hexdigest()

def hash_api_key(api_key):
    """Hash API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

# =============================================================================
# Data Validation Utilities
# =============================================================================

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """Validate username format"""
    if not username or len(username) < 3 or len(username) > 80:
        return False
    
    # Only alphanumeric characters and underscores
    return re.match(r'^[a-zA-Z0-9_]+$', username) is not None

def sanitize_html(text):
    """Basic HTML sanitization"""
    import html
    return html.escape(text)

def generate_slug(text, max_length=50):
    """Generate URL-friendly slug from text"""
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Trim and limit length
    slug = slug.strip('-')[:max_length]
    
    return slug

# =============================================================================
# Rate Limiting Utilities
# =============================================================================

def get_client_ip():
    """Get client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def generate_rate_limit_key(identifier, endpoint):
    """Generate rate limit key"""
    return f"rate_limit:{identifier}:{endpoint}"

# =============================================================================
# Response Utilities
# =============================================================================

def success_response(data=None, message="Success", status_code=200):
    """Generate success response"""
    response = {
        'success': True,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code

def error_response(message="An error occurred", status_code=400, errors=None):
    """Generate error response"""
    response = {
        'success': False,
        'message': message
    }
    
    if errors:
        response['errors'] = errors
    
    return jsonify(response), status_code

def paginated_response(items, page, per_page, total, endpoint=None):
    """Generate paginated response"""
    return {
        'items': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_prev': page > 1,
            'has_next': page * per_page < total
        }
    }

# =============================================================================
# File Upload Utilities
# =============================================================================

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def secure_filename(filename):
    """Generate secure filename"""
    import os
    # Remove path components
    filename = os.path.basename(filename)
    
    # Replace spaces and special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    
    # Add timestamp to prevent conflicts
    name, ext = os.path.splitext(filename)
    timestamp = str(int(datetime.utcnow().timestamp()))
    
    return f"{name}_{timestamp}{ext}"

# =============================================================================
# Database Utilities
# =============================================================================

def get_or_create(session, model, **kwargs):
    """Get existing instance or create new one"""
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        return instance, True

def soft_delete(instance):
    """Soft delete instance by setting is_active to False"""
    instance.is_active = False
    instance.deleted_at = datetime.utcnow()
