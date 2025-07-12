from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models.notification import Notification
from ..services.notifications import create_notification

bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@bp.get("/")
@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    page    = int(request.args.get("page", 1))
    per     = int(request.args.get("limit", 10))

    paged = (
        Notification.query.filter_by(user_id=user_id)
        .order_by(Notification.created_at.desc())
        .paginate(page=page, per_page=per, error_out=False)
    )

    return jsonify(
        status="success",
        data=[
            {
                "id": n.id,
                "message": n.message,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
            }
            for n in paged.items
        ],
        pagination=dict(page=paged.page, total_pages=paged.pages, total_items=paged.total),
    )


@bp.get("/unread_count")
@jwt_required()
def unread_count():
    user_id = get_jwt_identity()
    count   = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    return jsonify(status="success", data={"unread": count})


@bp.post("/mark_read/<int:notif_id>")
@jwt_required()
def mark_read(notif_id):
    user_id = get_jwt_identity()
    notif   = Notification.query.get_or_404(notif_id)
    if notif.user_id != user_id:
        return jsonify(status="error", error="unauthorized"), 403
    notif.is_read = True
    db.session.commit()
    return jsonify(status="success", data={"message": "marked as read"})


@bp.post("/")
@jwt_required()
def create_notif():
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify(status="error", error="message required"), 400

    notif = create_notification(user_id=user_id, message=message)
    return jsonify(status="success", data={"id": notif.id}), 201
