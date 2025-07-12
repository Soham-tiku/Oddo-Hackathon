from ..extensions import db
from datetime import datetime, timezone
from enum import Enum

class VoteType(Enum):
    UP = "up"
    DOWN = "down"

class Vote(db.Model):
    __tablename__ = "votes"

    id          = db.Column(db.Integer, primary_key=True)
    vote_type   = db.Column(db.Enum(VoteType), nullable=False)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"),      nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=True)
    answer_id   = db.Column(db.Integer, db.ForeignKey("answers.id"),   nullable=True)
    created_at  = db.Column(db.DateTime,  default=lambda: datetime.now(timezone.utc))
    updated_at  = db.Column(db.DateTime,  default=lambda: datetime.now(timezone.utc),
                            onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("user_id", "question_id", name="uq_user_question_vote"),
        db.UniqueConstraint("user_id", "answer_id",   name="uq_user_answer_vote"),
        db.CheckConstraint(
            "(question_id IS NOT NULL AND answer_id IS NULL) OR "
            "(question_id IS NULL AND answer_id IS NOT NULL)",
            name="vote_target_check",
        ),
    )

    @property
    def value(self):
        """Convert vote_type to numeric value"""
        return 1 if self.vote_type == VoteType.UP else -1
    
    @classmethod
    def get_vote_counts(cls, question_id=None, answer_id=None):
        """Get vote counts for question or answer"""
        if question_id:
            query = cls.query.filter_by(question_id=question_id)
        elif answer_id:
            query = cls.query.filter_by(answer_id=answer_id)
        else:
            return {"upvotes": 0, "downvotes": 0, "total": 0}
        
        votes = query.all()
        upvotes = sum(1 for vote in votes if vote.vote_type == VoteType.UP)
        downvotes = sum(1 for vote in votes if vote.vote_type == VoteType.DOWN)
        
        return {
            "upvotes": upvotes,
            "downvotes": downvotes,
            "total": upvotes - downvotes
        }
    
    @classmethod
    def get_vote_counts(cls, question_id=None, answer_id=None):
        """Get vote counts for question or answer"""
        if question_id:
            query = cls.query.filter_by(question_id=question_id)
        elif answer_id:
            query = cls.query.filter_by(answer_id=answer_id)
        else:
            return {"upvotes": 0, "downvotes": 0, "total": 0}
        
        votes = query.all()
        upvotes = sum(1 for vote in votes if vote.vote_type == VoteType.UP)
        downvotes = sum(1 for vote in votes if vote.vote_type == VoteType.DOWN)
        
        return {
            "upvotes": upvotes,
            "downvotes": downvotes,
            "total": upvotes - downvotes
        }
    
    @classmethod
    def get_user_vote(cls, user_id, question_id=None, answer_id=None):
        """Get user's vote for specific question or answer"""
        query = cls.query.filter_by(user_id=user_id)
        if question_id:
            query = query.filter_by(question_id=question_id)
        elif answer_id:
            query = query.filter_by(answer_id=answer_id)
        
        return query.first()
    
    def __repr__(self):
        target = f"question_id={self.question_id}" if self.question_id else f"answer_id={self.answer_id}"
        return f'<Vote user_id={self.user_id} {target} vote_type={self.vote_type.value}>'
