from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.question import Question
from ..schemas.question import QuestionSchema
from ..utils import error_response

questions_bp = Blueprint("questions", __name__)
qschema = QuestionSchema()
qschema_many = QuestionSchema(many=True)

@questions_bp.route("/questions", methods=["POST"])
@jwt_required()
def create_question():
    user_id = get_jwt_identity()
    data = request.get_json()
    errors = qschema.validate(data)
    if errors:
        return error_response(errors, 400)
    q = Question(title=data["title"], content=data["content"], user_id=user_id)
    db.session.add(q)
    db.session.commit()
    return qschema.jsonify(q), 201

@questions_bp.route("/questions", methods=["GET"])
def list_questions():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    questions = Question.query.order_by(Question.created_at.desc()).paginate(page, per_page, False).items
    return qschema_many.jsonify(questions), 200

@questions_bp.route("/questions/<int:q_id>", methods=["GET"])
def get_question(q_id):
    q = Question.query.get_or_404(q_id)
    return qschema.jsonify(q), 200