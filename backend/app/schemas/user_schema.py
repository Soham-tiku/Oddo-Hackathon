from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.user import User
import re

class UserSchema(SQLAlchemyAutoSchema):
    """Schema for User model serialization"""
    
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)
        dump_only_fields = ('id', 'created_at', 'updated_at')
    
    # Additional computed fields
    total_questions = fields.Method('get_total_questions')
    total_answers = fields.Method('get_total_answers')
    total_votes = fields.Method('get_total_votes')
    
    def get_total_questions(self, obj):
        return obj.questions.count()
    
    def get_total_answers(self, obj):
        return obj.answers.count()
    
    def get_total_votes(self, obj):
        return obj.votes.count()

class LoginSchema(Schema):
    """Schema for user login validation"""
    
    identifier = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=120),
        error_messages={'required': 'Email or username is required'}
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={'required': 'Password is required'}
    )
    remember_me = fields.Bool(missing=False)

class RegisterSchema(Schema):
    """Schema for user registration validation"""
    
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=80),
        error_messages={'required': 'Username is required'}
    )
    email = fields.Email(
        required=True,
        validate=validate.Length(max=120),
        error_messages={'required': 'Email is required', 'invalid': 'Invalid email format'}
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={'required': 'Password is required'}
    )
    confirm_password = fields.Str(
        required=True,
        error_messages={'required': 'Password confirmation is required'}
    )
    
    @validates('username')
    def validate_username(self, value):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValidationError('Username can only contain letters, numbers, and underscores')
        
        # Check if username already exists
        from ..models.user import User
        if User.query.filter_by(username=value).first():
            raise ValidationError('Username already exists')
    
    @validates('email')
    def validate_email(self, value):
        """Validate email uniqueness"""
        from ..models.user import User
        if User.query.filter_by(email=value).first():
            raise ValidationError('Email already registered')
    
    @validates('password')
    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', value):
            raise ValidationError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError('Password must contain at least one special character')
    
    def validate(self, data, **kwargs):
        """Cross-field validation"""
        errors = {}
        
        if data.get('password') != data.get('confirm_password'):
            errors['confirm_password'] = ['Passwords do not match']
        
        if errors:
            raise ValidationError(errors)
        
        return data

class PasswordChangeSchema(Schema):
    """Schema for password change validation"""
    
    current_password = fields.Str(
        required=True,
        error_messages={'required': 'Current password is required'}
    )
    new_password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={'required': 'New password is required'}
    )
    confirm_new_password = fields.Str(
        required=True,
        error_messages={'required': 'Password confirmation is required'}
    )
    
    def validate(self, data, **kwargs):
        """Cross-field validation"""
        errors = {}
        
        if data.get('new_password') != data.get('confirm_new_password'):
            errors['confirm_new_password'] = ['Passwords do not match']
        
        if data.get('current_password') == data.get('new_password'):
            errors['new_password'] = ['New password must be different from current password']
        
        if errors:
            raise ValidationError(errors)
        
        return data
