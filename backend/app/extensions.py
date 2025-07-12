"""Central place to instantiate global Flask extensions."""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO

# ORM / auth / rate‑limit
db      = SQLAlchemy()
jwt     = JWTManager()
limiter = Limiter(key_func=get_remote_address)

# WebSocket (used by notifications blueprint/service)
socketio = SocketIO(cors_allowed_origins="*")
