from ..extensions import db
from datetime import datetime
from sqlalchemy import func

question_tags = db.Table(
    "question_tags",
    db.Column("question_id", db.Integer, db.ForeignKey("questions.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
    db.Column("created_at", db.DateTime, default=datetime.utcnow)
)

class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Enhanced timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Engagement metrics
    view_count = db.Column(db.Integer, default=0)
    vote_count = db.Column(db.Integer, default=0)
    answer_count = db.Column(db.Integer, default=0)
    
    # Status fields
    is_active = db.Column(db.Boolean, default=True)
    is_closed = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    
    # SEO and search
    slug = db.Column(db.String(300), unique=True, index=True)
    meta_description = db.Column(db.String(160))
    
    # Moderation
    is_moderated = db.Column(db.Boolean, default=False)
    moderated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    moderated_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    answers = db.relationship("Answer", backref="question", lazy=True, 
                            cascade="all, delete-orphan")
    tags = db.relationship("Tag", secondary=question_tags, 
                          backref=db.backref("questions", lazy="dynamic"))
    votes = db.relationship("Vote", backref="question", lazy=True,
                           cascade="all, delete-orphan")
    
    # Moderator relationship
    moderator = db.relationship("User", foreign_keys=[moderated_by], 
                              backref="moderated_questions")
    
    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user_id = user_id
        self.slug = self.generate_slug(title)
    
    def generate_slug(self, title):
        """Generate URL-friendly slug from title"""
        import re
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')[:100]  # Limit length
        
        # Ensure uniqueness
        base_slug = slug
        counter = 1
        while Question.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        db.session.commit()
    
    def update_vote_count(self):
        """Update vote count based on actual votes"""
        from .vote import Vote, VoteType
        upvotes = Vote.query.filter_by(question_id=self.id, vote_type=VoteType.UP).count()
        downvotes = Vote.query.filter_by(question_id=self.id, vote_type=VoteType.DOWN).count()
        self.vote_count = upvotes - downvotes
        db.session.commit()
    
    def update_answer_count(self):
        """Update answer count"""
        self.answer_count = self.answers.count()
        db.session.commit()
    
    def add_tag(self, tag):
        """Add a tag to the question"""
        if not self.has_tag(tag):
            self.tags.append(tag)
            tag.increment_usage()
    
    def remove_tag(self, tag):
        """Remove a tag from the question"""
        if self.has_tag(tag):
            self.tags.remove(tag)
            tag.decrement_usage()
    
    def has_tag(self, tag):
        """Check if question has a specific tag"""
        return tag in self.tags
    
    def get_tag_names(self):
        """Get list of tag names for this question"""
        return [tag.name for tag in self.tags]
    
    def get_accepted_answer(self):
        """Get the accepted answer for this question"""
        return self.answers.filter_by(is_accepted=True).first()
    
    def close_question(self, moderator_id=None):
        """Close the question"""
        self.is_closed = True
        if moderator_id:
            self.moderated_by = moderator_id
            self.moderated_at = datetime.utcnow()
    
    def reopen_question(self, moderator_id=None):
        """Reopen the question"""
        self.is_closed = False
        if moderator_id:
            self.moderated_by = moderator_id
            self.moderated_at = datetime.utcnow()
    
    @classmethod
    def get_popular_questions(cls, limit=10):
        """Get popular questions by vote count"""
        return cls.query.filter_by(is_active=True)\
                      .order_by(cls.vote_count.desc())\
                      .limit(limit).all()
    
    @classmethod
    def get_recent_questions(cls, limit=10):
        """Get recent questions"""
        return cls.query.filter_by(is_active=True)\
                      .order_by(cls.created_at.desc())\
                      .limit(limit).all()
    
    @classmethod
    def get_unanswered_questions(cls, limit=10):
        """Get questions without answers"""
        return cls.query.filter_by(is_active=True, answer_count=0)\
                      .order_by(cls.created_at.desc())\
                      .limit(limit).all()
    
    @classmethod
    def search_questions(cls, query, limit=20):
        """Search questions by title and content"""
        return cls.query.filter(
            cls.is_active == True,
            db.or_(
                cls.title.ilike(f'%{query}%'),
                cls.content.ilike(f'%{query}%')
            )
        ).order_by(cls.vote_count.desc()).limit(limit).all()
    
    def to_dict(self):
        """Convert question to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'view_count': self.view_count,
            'vote_count': self.vote_count,
            'answer_count': self.answer_count,
            'is_active': self.is_active,
            'is_closed': self.is_closed,
            'is_featured': self.is_featured,
            'slug': self.slug,
            'tags': [tag.name for tag in self.tags],
            'author': self.author.username if self.author else None
        }
    
    def __repr__(self):
        return f'<Question {self.id}: {self.title[:50]}...>'
