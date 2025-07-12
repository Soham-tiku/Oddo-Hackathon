"""Questions blueprint – handles /api/questions endpoints."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models.question import Question
from ..schemas.question import QuestionSchema
from ..utils import sanitize_html, error_response
from ..services.notifications import create_notification

questions_bp = Blueprint("questions", __name__, url_prefix="/questions")

qschema       = QuestionSchema()
qschema_many  = QuestionSchema(many=True)

# --------------------------------------------------------------------- #
# POST /api/questions  (create a question)
# --------------------------------------------------------------------- #
@questions_bp.post("/")                     # ←  trailing “/” not empty string
@jwt_required()
def create_question():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    data["content"] = sanitize_html(data.get("content", ""))
    errors = qschema.validate(data)
    if errors:
        return error_response(errors, 400)

    try:
        q = Question(title=data["title"], content=data["content"], user_id=user_id)
        db.session.add(q)
        db.session.commit()

        create_notification(user_id, f"New question posted: {q.title[:50]}")
        return qschema.jsonify(q), 201
    except Exception:
        db.session.rollback()
        return error_response("Failed to create question", 500)

# --------------------------------------------------------------------- #
# GET /api/questions  (list with pagination)
# --------------------------------------------------------------------- #
@questions_bp.get("/")                      # ←  trailing “/”
def list_questions():
    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    items = (
        Question.query.order_by(Question.created_at.desc())
        .paginate(page, per_page, False)
        .items
    )
    return qschema_many.jsonify(items), 200

# --------------------------------------------------------------------- #
# GET /api/questions/<id>
# --------------------------------------------------------------------- #
@questions_bp.get("/<int:q_id>")
def get_question(q_id):
    q = Question.query.get_or_404(q_id)
    return qschema.jsonify(q), 200
