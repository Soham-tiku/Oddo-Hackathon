from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.question import Question
from ..utils import sanitize_html

class QuestionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Question
        load_instance = True
        include_fk = True

    content = fields.Method("load_content", deserialize="dump_content")

    def load_content(self, obj):
        return obj.content

    def dump_content(self, value):
        return sanitize_html(value)