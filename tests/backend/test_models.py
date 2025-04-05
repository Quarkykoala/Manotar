import pytest
from datetime import datetime
from backend.src.models.models import User, KeywordStat

def test_user_model(app, db_session):
    with app.app_context():
        user = User(
            phone_number="+1234567890",
            access_code="ABC123XY",
            location="Mumbai",
            department="Engineering"
        )
        db_session.session.add(user)
        db_session.session.commit()

        assert user.id is not None
        assert user.phone_number == "+1234567890"
        assert user.access_code == "ABC123XY"
        assert not user.is_authenticated
        assert not user.conversation_started
        assert user.message_count == 0

def test_keyword_stat_model(app, db_session):
    with app.app_context():
        user = User(phone_number="+1234567890", access_code="ABC123XY")
        db_session.session.add(user)
        db_session.session.commit()

        keyword_stat = KeywordStat(
            user_id=user.id,
            department="Engineering",
            location="Mumbai",
            keyword="stress",
            count=5
        )
        db_session.session.add(keyword_stat)
        db_session.session.commit()

        assert keyword_stat.id is not None
        assert keyword_stat.keyword == "stress"
        assert keyword_stat.count == 5
        assert isinstance(keyword_stat.timestamp, datetime)