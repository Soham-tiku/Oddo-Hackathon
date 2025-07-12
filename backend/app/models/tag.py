from ..extensions import db
from datetime import datetime,timezone

# Association table for many-to-many relationship between questions and tags
question_tags = db.Table('question_tags',
    db.Column('question_id', db.Integer, db.ForeignKey('questions.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc))
)

class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    slug = db.Column(db.String(60), unique=True, nullable=False, index=True)
    color = db.Column(db.String(7), default='#3B82F6')  # Hex color for UI
    usage_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Many-to-many relationship with questions
    questions = db.relationship('Question', 
                               secondary=question_tags, 
                               back_populates='tags',
                               lazy='dynamic')
    
    # Relationship with creator
    creator = db.relationship('User', backref='created_tags', lazy=True)
    
    def __init__(self, name, description=None, created_by=None):
        self.name = name.strip()
        self.description = description
        self.slug = self.generate_slug(name)
        self.created_by = created_by
    
    @staticmethod
    def generate_slug(name):
        """Generate URL-friendly slug from tag name"""
        import re
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def increment_usage(self):
        """Increment usage count when tag is used"""
        self.usage_count += 1
        db.session.commit()
    
    def decrement_usage(self):
        """Decrement usage count when tag is removed"""
        if self.usage_count > 0:
            self.usage_count -= 1
            db.session.commit()
    
    @classmethod
    def get_popular_tags(cls, limit=10):
        """Get most popular tags by usage count"""
        return cls.query.filter_by(is_active=True)\
                      .order_by(cls.usage_count.desc())\
                      .limit(limit).all()
    
    @classmethod
    def search_tags(cls, query, limit=10):
        """Search tags by name for autocomplete"""
        return cls.query.filter(
            cls.name.ilike(f'%{query}%'),
            cls.is_active == True
        ).order_by(cls.usage_count.desc()).limit(limit).all()
    
    def to_dict(self):
        """Convert tag to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'slug': self.slug,
            'color': self.color,
            'usage_count': self.usage_count,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Tag {self.name}>'
