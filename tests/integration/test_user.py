import pytest
import logging
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.models.user import User
from tests.conftest import create_fake_user, managed_db_session

logger = logging.getLogger(__name__)

def test_database_connection(db_session):
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1
    logger.info("Database connection test passed")

def test_managed_session():
    with managed_db_session() as session:
        session.execute(text("SELECT 1"))
    try:
        session.execute(text("SELECT * FROM nonexistent_table"))
    except Exception as e:
        assert "nonexistent_table" in str(e)

def test_session_handling(db_session):
    initial_count = db_session.query(User).count()
    logger.info(f"Initial user count before test_session_handling: {initial_count}")
    assert initial_count == 0, f"Expected 0 users before test, found {initial_count}"

    user1 = User(
        first_name="Test",
        last_name="User",
        email="test1@example.com",
        username="testuser1",
        password="password123"
    )
    db_session.add(user1)
    db_session.commit()
    logger.info(f"Added user1: {user1.email}")

    current_count = db_session.query(User).count()
    logger.info(f"User count after adding user1: {current_count}")
    assert current_count == 1, f"Expected 1 user after adding user1, found {current_count}"

    try:
        user2 = User(
            first_name="Test",
            last_name="User",
            email="test1@example.com",
            username="testuser2",
            password="password456"
        )
        db_session.add(user1)
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
        logger.info("IntegrityError caught and rolled back for user2.")

    found_user1 = db_session.query(User).filter_by(email="test1@example.com").first()
    assert found_user1 is not None, "User1 should still exist after rollback"
    assert found_user1.username == "testuser1"
    logger.info(f"Found user1 after rollback: {found_user1.email}")

    user3 = User(
        first_name="Test",
        last_name="User",
        email="test3@example.com",
        username="testuser3",
        password="password789"
    )
    db_session.add(user3)
    db_session.commit()
    logger.info(f"Added user3: {user3.email}")
    
    users = db_session.query(User).order_by(User.email).all()
    current_count = len(users)
    emails = {user.email for user in users}
    logger.info(f"Final user count: {current_count}, Emails: {emails}")
    
    assert current_count == 2, f"Should have exactly user1 and user3, found {current_count}"
    assert "test1@example.com" in emails, "User1 must remain"
    assert "test3@example.com" in emails, "User3 must exist"

def test_create_user_with_faker(db_session):
    user_data = create_fake_user()
    logger.info(f"Creating user with data: {user_data}")

    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.email == user_data["email"]
    logger.info(f"Successfully created user with ID: {user.id}")

def test_create_multiple_users(db_session):
    users = []
    for _ in range(3):
        user_data = create_fake_user()
        user = User(**user_data)
        users.append(user)
        db_session.add(user)
    
    db_session.commit()
    assert len(users) == 3
    logger.info(f"Successfully created {len(users)} users")

def test_query_methods(db_session, seed_users):
    user_count = db_session.query(User).count()
    assert user_count >= len(seed_users), "The user table should have at least the seeded users"

    first_user = seed_users[0]
    found = db_session.query(User).filter_by(email=first_user.email).first()
    assert found is not None, "Should find the seeded user by email"

    users_by_email = db_session.query(User).order_by(User.email).all()
    assert len(users_by_email) >= len(seed_users), "Query should return at least the seeded users"

