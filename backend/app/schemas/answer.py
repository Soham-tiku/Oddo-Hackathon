from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.answer import Answer
from ..utils import sanitize_html

class AnswerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Answer
        load_instance = True
        include_fk = True

    content = sanitize_html