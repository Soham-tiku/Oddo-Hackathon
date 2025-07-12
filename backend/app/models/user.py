from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role          = db.Column(db.String(20),  default="user")

    # ── Relationships ─────────────────────────────────────────
    questions     = db.relationship("Question",      backref="author", lazy=True)
    answers       = db.relationship("Answer",        backref="author", lazy=True)
    votes         = db.relationship("Vote",          backref="user",   lazy=True)
    notifications = db.relationship("Notification",  backref="user",   lazy=True,
                                    cascade="all, delete-orphan")

    # ── Helpers ───────────────────────────────────────────────
    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password,method='pbkdf2:sha256')

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def is_admin(self) -> bool:
        return self.role == "admin"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'reputation': self.reputation,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self) -> str:           # pragma: no cover
        return f"<User {self.username} ({self.role})>"
