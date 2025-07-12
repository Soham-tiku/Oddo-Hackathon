import pytest
from unittest.mock import patch
from app.blueprints.questions import create_question
from app.models import Question, User
from app.extensions import db
from flask import Flask

def test_create_question_creates_notification(app, client):
    with app.app_context():
        # Mock user
        user = User(id=1)
        db.session.add(user)
        db.session.commit()

        # Mock JWT identity
        with patch('flask_jwt_extended.get_jwt_identity', return_value=1):
            with patch('app.services.notifications.create_notification') as mock_notif:
                # Simulate POST request
                response = client.post(
                    "/questions",
                    json={"title": "Test Question", "content": "Test Content"},
                    headers={"Authorization": "Bearer dummy_token"}
                )
                assert response.status_code == 201
                assert mock_notif.called
                mock_notif.assert_called_with(
                    user_id=1,
                    message="New question posted: Test Question"
                )

                # Verify question was created
                question = Question.query.filter_by(user_id=1).first()
                assert question is not None
                assert question.title == "Test Question"