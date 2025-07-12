from ..extensions import db, socketio
from ..models.notification import Notification


def create_notification(*, user_id: int, message: str) -> Notification:
    """Persist and emit a notification (called from blueprints/services)."""
    if not (isinstance(user_id, int) and user_id > 0):
        raise ValueError("user_id must be a positive integer")
    if not (isinstance(message, str) and message.strip()):
        raise ValueError("message must be a non‑empty string (≤255 chars)")
    if len(message) > 255:
        message = message[:255]

    notif = Notification(user_id=user_id, message=message.strip())
    db.session.add(notif)
    db.session.commit()

    # WebSocket broadcast
    socketio.emit(
        "notification",
        {
            "id": notif.id,
            "message": notif.message,
            "is_read": notif.is_read,
            "created_at": notif.created_at.isoformat(),
        },
        namespace="/notifications",
    )
    return notif
