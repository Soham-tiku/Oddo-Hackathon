"""Answers blueprint – nested under /api/questions/<id>/answers."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models.answer import Answer
from ..models.question import Question
from ..schemas.answer import AnswerSchema
from ..utils import sanitize_html, error_response

bp = Blueprint(
    "answers",
    __name__,
    url_prefix="/questions/<int:q_id>/answers",  # note: parent question id in prefix
)

aschema = AnswerSchema()
aschema_many = AnswerSchema(many=True)


# ───────────────────────────────────────────────────────────
# POST /api/questions/<q_id>/answers  (add answer)
# ───────────────────────────────────────────────────────────
@bp.post("")
@jwt_required()
def post_answer(q_id):
    # Ensure parent question exists
    Question.query.get_or_404(q_id)

    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    data["content"] = sanitize_html(data.get("content", ""))

    errors = aschema.validate(data)
    if errors:
        return error_response(errors, 400)

    ans = Answer(content=data["content"], question_id=q_id, user_id=user_id)
    db.session.add(ans)
    db.session.commit()
    return aschema.jsonify(ans), 201


# ───────────────────────────────────────────────────────────
# GET /api/questions/<q_id>/answers  (list answers)
# ───────────────────────────────────────────────────────────
@bp.get("")
def list_answers(q_id):
    Question.query.get_or_404(q_id)
    answers = (
        Answer.query.filter_by(question_id=q_id)
        .order_by(Answer.created_at.asc())
        .all()
    )
    return aschema_many.jsonify(answers), 200
