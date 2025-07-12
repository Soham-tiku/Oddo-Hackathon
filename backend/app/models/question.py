from ..extensions import db
from datetime import datetime


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # ── Relationships ─────────────────────────────────────────
    answers = db.relationship("Answer", backref="question", lazy=True)
    votes = db.relationship("Vote", backref="question", lazy=True)

    def to_dict(self):
        """Serialize question object to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "votes": len(self.votes),
        }

    def __repr__(self):
        return f"<Question {self.title[:30]}>"
