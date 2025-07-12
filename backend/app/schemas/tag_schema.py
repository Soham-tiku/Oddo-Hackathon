from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.tag import Tag

class TagSchema(SQLAlchemyAutoSchema):
    """Schema for Tag model serialization"""
    
    class Meta:
        model = Tag
        load_instance = True
        dump_only_fields = ('id', 'slug', 'usage_count', 'created_at', 'updated_at')
    
    # Additional computed fields
    question_count = fields.Method('get_question_count')
    
    def get_question_count(self, obj):
        return obj.questions.count()

class TagCreateSchema(Schema):
    """Schema for creating new tags"""
    
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={'required': 'Tag name is required'}
    )
    description = fields.Str(
        validate=validate.Length(max=500),
        allow_none=True
    )
    color = fields.Str(
        validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'),
        missing='#3B82F6',
        error_messages={'invalid': 'Color must be a valid hex color code'}
    )
    
    @validates('name')
    def validate_name(self, value):
        """Validate tag name"""
        # Clean the name
        name = value.strip()
        
        if not name:
            raise ValidationError('Tag name cannot be empty')
        
        # Check for invalid characters
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-\_\.\#\+]+$', name):
            raise ValidationError('Tag name contains invalid characters')
        
        # Check if tag already exists
        if Tag.query.filter_by(name=name).first():
            raise ValidationError('Tag already exists')

class TagUpdateSchema(Schema):
    """Schema for updating existing tags"""
    
    name = fields.Str(
        validate=validate.Length(min=1, max=50),
        allow_none=True
    )
    description = fields.Str(
        validate=validate.Length(max=500),
        allow_none=True
    )
    color = fields.Str(
        validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'),
        allow_none=True,
        error_messages={'invalid': 'Color must be a valid hex color code'}
    )
    is_active = fields.Bool(allow_none=True)
    
    @validates('name')
    def validate_name(self, value):
        """Validate tag name for updates"""
        if value is not None:
            name = value.strip()
            if not name:
                raise ValidationError('Tag name cannot be empty')
            
            import re
            if not re.match(r'^[a-zA-Z0-9\s\-\_\.\#\+]+$', name):
                raise ValidationError('Tag name contains invalid characters')

class TagSearchSchema(Schema):
    """Schema for tag search parameters"""
    
    query = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={'required': 'Search query is required'}
    )
    limit = fields.Int(
        validate=validate.Range(min=1, max=50),
        missing=10
    )
    include_inactive = fields.Bool(missing=False)
