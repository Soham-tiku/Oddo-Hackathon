from ..extensions import db

class Answer(db.Model):
    __tablename__ = "answers"

    id          = db.Column(db.Integer, primary_key=True)
    content     = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"),     nullable=False)
    created_at  = db.Column(db.DateTime, server_default=db.func.now())

    votes = db.relationship("Vote", backref="answer", lazy=True)
