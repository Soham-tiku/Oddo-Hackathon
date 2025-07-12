from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.question import Question
from ..extensions import db

bp = Blueprint("questions", __name__)

@bp.route("", methods=["GET"])
def get_questions():
    questions = Question.query.order_by(Question.created_at.desc()).all()
    return jsonify({"questions": [q.to_dict() for q in questions]}), 200

@bp.route("", methods=["POST"])
@jwt_required()
def post_question_safe():  # 💡 renamed to avoid endpoint name conflict
    try:
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            return jsonify({"error": "Title and content are required"}), 400

        user_id = get_jwt_identity()

        question = Question(title=title, content=content, user_id=user_id)
        db.session.add(question)
        db.session.commit()

        return jsonify({
            "message": "Question created",
            "question": question.to_dict()
        }), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": "Failed to create question"}), 500
