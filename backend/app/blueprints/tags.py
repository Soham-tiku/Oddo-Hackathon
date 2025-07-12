from flask import Blueprint

bp = Blueprint('tags', __name__)

@bp.route('/')
def test_tags():
    return {"message": "Tags route works (placeholder)"}
