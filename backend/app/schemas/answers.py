from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.answer import Answer
from ..schemas.answer import AnswerSchema
from ..utils import error_response

answers_bp = Blueprint("answers", __name__)
aschema = AnswerSchema()
aschema_many = AnswerSchema(many=True)

@answers_bp.route("/questions/<int:q_id>/answers", methods=["POST"])
@jwt_required()
def post_answer(q_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    errors = aschema.validate(data)
    if errors:
        return error_response(errors, 400)
    ans = Answer(content=data["content"], question_id=q_id, user_id=user_id)
    db.session.add(ans)
    db.session.commit()
    return aschema.jsonify(ans), 201

@answers_bp.route("/questions/<int:q_id>/answers", methods=["GET"])
def list_answers(q_id):
    answers = Answer.query.filter_by(question_id=q_id).order_by(Answer.created_at.asc()).all()
    return aschema_many.jsonify(answers), 200