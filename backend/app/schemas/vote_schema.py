from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.vote import Vote, VoteType

class VoteSchema(SQLAlchemyAutoSchema):
    """Schema for Vote model serialization"""
    
    class Meta:
        model = Vote
        load_instance = True
        dump_only_fields = ('id', 'created_at', 'updated_at')
    
    # Convert enum to string for JSON
    vote_type = fields.Enum(VoteType, by_value=True)
    
    # Additional computed fields
    target_type = fields.Method('get_target_type')
    target_id = fields.Method('get_target_id')
    
    def get_target_type(self, obj):
        return 'question' if obj.question_id else 'answer'
    
    def get_target_id(self, obj):
        return obj.question_id if obj.question_id else obj.answer_id

class VoteCreateSchema(Schema):
    """Schema for creating votes"""
    
    question_id = fields.Int(
        allow_none=True,
        validate=validate.Range(min=1),
        error_messages={'invalid': 'Question ID must be a positive integer'}
    )
    answer_id = fields.Int(
        allow_none=True,
        validate=validate.Range(min=1),
        error_messages={'invalid': 'Answer ID must be a positive integer'}
    )
    vote_type = fields.Str(
        required=True,
        validate=validate.OneOf(['up', 'down']),
        error_messages={
            'required': 'Vote type is required',
            'invalid': 'Vote type must be either "up" or "down"'
        }
    )
    
    def validate(self, data, **kwargs):
        """Cross-field validation"""
        errors = {}
        
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')
        
        # Ensure exactly one target is specified
        if not question_id and not answer_id:
            errors['_schema'] = ['Either question_id or answer_id must be provided']
        elif question_id and answer_id:
            errors['_schema'] = ['Cannot vote on both question and answer simultaneously']
        
        if errors:
            raise ValidationError(errors)
        
        return data
    
    @validates('question_id')
    def validate_question_id(self, value):
        """Validate question exists"""
        if value is not None:
            from ..models.question import Question
            if not Question.query.get(value):
                raise ValidationError('Question not found')
    
    @validates('answer_id')
    def validate_answer_id(self, value):
        """Validate answer exists"""
        if value is not None:
            from ..models.answer import Answer
            if not Answer.query.get(value):
                raise ValidationError('Answer not found')

class VoteStatsSchema(Schema):
    """Schema for vote statistics"""
    
    upvotes = fields.Int(dump_only=True)
    downvotes = fields.Int(dump_only=True)
    total = fields.Int(dump_only=True)
    user_vote = fields.Str(
        allow_none=True,
        validate=validate.OneOf(['up', 'down']),
        dump_only=True
    )
