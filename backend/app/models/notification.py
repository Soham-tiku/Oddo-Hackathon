"""Notification model – one row per in‑app / websocket notification."""
from ..extensions import db
from datetime import datetime, timezone


class Notification(db.Model):
    __tablename__ = "notifications"

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer,
                          db.ForeignKey("users.id", ondelete="CASCADE"),
                          nullable=False)
    message   = db.Column(db.String(255), nullable=False)
    is_read   = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # convenience repr
    def __repr__(self) -> str:           # pragma: no cover
        return f"<Notification {self.id} user={self.user_id}>"
