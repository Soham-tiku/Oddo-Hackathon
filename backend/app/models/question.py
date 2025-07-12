from ..extensions import db

question_tags = db.Table(
    "question_tags",
    db.Column("question_id", db.Integer, db.ForeignKey("questions.id"), primary_key=True),
    db.Column("tag_id",      db.Integer, db.ForeignKey("tags.id"),      primary_key=True),
)

class Question(db.Model):
    __tablename__ = "questions"

    id        = db.Column(db.Integer, primary_key=True)
    title     = db.Column(db.String(255), nullable=False)
    content   = db.Column(db.Text, nullable=False)
    user_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    answers = db.relationship("Answer", backref="question", lazy=True)
    tags    = db.relationship("Tag", secondary=question_tags, backref="questions")
    votes   = db.relationship("Vote", backref="question", lazy=True)
