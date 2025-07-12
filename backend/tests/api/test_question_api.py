import pytest
from flask_jwt_extended import create_access_token
from app.models import Notification, User
from app.extensions import db

def test_create_question_api(client, app):
    with app.app_context():
        # Create a user
        user = User(id=1)
        db.session.add(user)
        db.session.commit()

        # Create JWT token
        token = create_access_token(identity=1)

        # POST a new question
        response = client.post(
            "/questions",
            json={"title": "Test Question", "content": "Test Content"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        assert response.json["title"] == "Test Question"

        # Verify notification was created
        notif = Notification.query.filter_by(user_id=1).first()
        assert notif is not None
        assert notif.message == "New question posted: Test Question"
        assert notif.is_read is False