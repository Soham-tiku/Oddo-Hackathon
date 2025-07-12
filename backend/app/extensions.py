from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
limiter = Limiter(
    app=None,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
cors = CORS()

# JWT Configuration
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {"msg": "Token has expired"}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {"msg": "Invalid token"}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {"msg": "Authorization token is required"}, 401
