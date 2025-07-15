import pytest
import logging
import uuid
import os
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.models.user import User
from tests.conftest import create_fake_user, managed_db_session
from tests.integration.test_fastapi_calculator import client
from app.config import settings

logger = logging.getLogger(__name__)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

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

def test_transaction_rollback(db_session):
    initial_count = db_session.query(User).count()

    try:
        user_data = create_fake_user()
        user = User(**user_data)
        db_session.add(user)
        db_session.execute(text("SELECT * FROM nonexistent_table"))
        db_session.commit()
    except Exception:
        db_session.rollback()

    final_count = db_session.query(User).count()
    assert final_count == initial_count, "The new use should not have been committed"

def test_update_with_refresh(db_session, test_user):
    original_email = test_user.email
    original_update_time = test_user.updated_at

    new_email = f"new_{original_email}"
    test_user.email = new_email
    db_session.commit()
    db_session.refresh(test_user)

    assert test_user.email == new_email, "Email should have been updated"
    assert test_user.updated_at > original_update_time, "Updated time should be newer"
    logger.info(f"Successfully updated user {test_user.id}")

@pytest.mark.slow
def test_bulk_operation(db_session):
    users_data = [create_fake_user() for _ in range(10)]
    users = [User(**data) for data in users_data]
    db_session.bulk_save_objects(users)
    db_session.commit()

    count = db_session.query(User).count()
    assert count >= 10, "At least 10 users should now be in the database"
    logger.info(f"Successfully performed bulk operation with {len(users)} users")

def test_unique_email_constraint(db_session):
    first_user_data = create_fake_user()
    first_user = User(**first_user_data)
    db_session.add(first_user)
    db_session.commit()

    second_user_data = create_fake_user()
    second_user_data["email"] = first_user_data["email"]
    second_user = User(**second_user_data)
    db_session.add(second_user)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_unique_username_constraint(db_session):
    first_user_data = create_fake_user()
    first_user = User(**first_user_data)
    db_session.add(first_user)
    db_session.commit()

    second_user_data = create_fake_user()
    second_user_data["username"] = first_user_data["username"]
    second_user = User(**second_user_data)
    db_session.add(second_user)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_user_persistence_after_constraint(db_session):
    initial_user_data = {
        "first_name": "First",
        "last_name": "User",
        "email": "first@example.com",
        "username": "firstuser",
        "password": "password123"
    }
    initial_user = User(**initial_user_data)
    db_session.add(initial_user)
    db_session.commit()
    saved_id = initial_user.id

    try:
        duplicate_user = User(
            first_name="Second",
            last_name="User",
            email="first@example.com",
            username="seconduser",
            password="password456"
        )
        db_session.add(duplicate_user)
        db_session.commit()
        assert False, "Should have raised IntegrityError"
    except IntegrityError:
        db_session.rollback()

    found_user = db_session.query(User).filter_by(id=saved_id).first()
    assert found_user is not None, "Original user should exist"
    assert found_user.id == saved_id, "Should find original user by ID"
    assert found_user.email == "first@example.com", "Email should be unchanged"
    assert found_user.username == "firstuser", "Username should be unchanged"

def test_error_handling():
    with pytest.raises(Exception) as exc_info:
        with managed_db_session() as session:
            session.execute(text("INVALID SQL"))
    assert "INVALID SQL" in str(exc_info.value)

def test_authenticate_success(db_session):
    # Create and add a user with a hashed password
    password = "securepassword"
    user = User(
        first_name="Auth",
        last_name="Tester",
        email="authuser@example.com",
        username="authuser",
        password=User.hash_password(password),
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Authenticate with correct username
    result = User.authenticate(db_session, "authuser", password)
    assert result is not None
    assert "access_token" in result
    assert result["user"]["email"] == "authuser@example.com"

    # Authenticate with correct email
    result_email = User.authenticate(db_session, "authuser@example.com", password)
    assert result_email is not None
    assert result_email["user"]["username"] == "authuser"

def test_authenticate_wrong_password(db_session):
    password = "rightpassword"
    user = User(
        first_name="Wrong",
        last_name="Password",
        email="wrongpass@example.com",
        username="wrongpassuser",
        password=User.hash_password(password),
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()

    # Wrong password
    result = User.authenticate(db_session, "wrongpassuser", "incorrectpassword")
    assert result is None

def test_authenticate_nonexistent_user(db_session):
    # No user in DB with this username/email
    result = User.authenticate(db_session, "nonexistent", "any_password")
    assert result is None

def test_authenticate_inactive_user(db_session):
    # User is inactive but should still be authenticated (since is_active is not checked in authenticate)
    password = "inactivepassword"
    user = User(
        first_name="Inactive",
        last_name="User",
        email="inactive@example.com",
        username="inactiveuser",
        password=User.hash_password(password),
        is_active=False,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()

    result = User.authenticate(db_session, "inactiveuser", password)
    assert result is not None
    assert result["user"]["email"] == "inactive@example.com"

def test_authenticate_updates_last_login(db_session):
    password = "lastloginpass"
    user = User(
        first_name="Last",
        last_name="Login",
        email="lastlogin@example.com",
        username="lastloginuser",
        password=User.hash_password(password),
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    old_last_login = user.last_login

    User.authenticate(db_session, "lastloginuser", password)
    db_session.refresh(user)
    assert user.last_login is not None
    if old_last_login is not None:
        assert user.last_login > old_last_login
        
def test_verify_token_valid(db_session):
    # Create a user and generate a valid token
    user = User(
        first_name="Token",
        last_name="Verifier",
        email="tokenverifier@example.com",
        username="tokenverifier",
        password=User.hash_password("testpassword"),
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = User.create_access_token({"sub": str(user.id)})
    result = User.verify_token(token)
    assert result == user.id

def test_verify_token_invalid_signature():
    # Token with wrong secret
    payload = {"sub": str(uuid.uuid4())}
    wrong_secret = "wrong-secret"
    token = jwt.encode(payload, wrong_secret, algorithm="HS256")
    result = User.verify_token(token)
    assert result is None

def test_verify_token_expired():
    # Token with past expiration
    user_id = str(uuid.uuid4())
    expire = datetime.utcnow() - timedelta(minutes=1)
    payload = {"sub": user_id, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    result = User.verify_token(token)
    assert result is None

def test_verify_token_no_sub():
    # Token missing 'sub' field
    payload = {"exp": datetime.utcnow() + timedelta(minutes=5)}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    result = User.verify_token(token)
    assert result is None

def test_verify_token_invalid_uuid():
    # Token with invalid UUID in 'sub'
    payload = {"sub": "not-a-uuid", "exp": datetime.utcnow() + timedelta(minutes=5)}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    result = User.verify_token(token)
    assert result is None

def test_verify_token_malformed_token():
    # Completely invalid token string
    result = User.verify_token("not.a.jwt.token")
    assert result is None

def test_register_success(db_session):
    user_data = {
        "first_name": "Reg",
        "last_name": "User",
        "email": "reguser@example.com",
        "username": "reguser",
        "password": "SecurePass123"
    }
    user = User.register(db_session, user_data)
    assert user.id is not None
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]
    assert user.is_active is True
    assert user.is_verified is False
    # Password should be hashed
    assert user.password != user_data["password"]
    assert user.verify_password(user_data["password"])

def test_register_short_password(db_session):
    user_data = {
        "first_name": "Short",
        "last_name": "Pass",
        "email": "shortpass@example.com",
        "username": "shortpassuser",
        "password": "123"
    }
    with pytest.raises(ValueError) as exc_info:
        User.register(db_session, user_data)
    assert "Password must be at least 6 characters long" in str(exc_info.value)

def test_register_duplicate_email(db_session):
    user_data = {
        "first_name": "Dup",
        "last_name": "Email",
        "email": "dupemail@example.com",
        "username": "dupemailuser",
        "password": "Password123"
    }
    # Register first user
    User.register(db_session, user_data)
    # Try to register another user with same email
    user_data2 = {
        "first_name": "Dup2",
        "last_name": "Email2",
        "email": "dupemail@example.com",
        "username": "dupemailuser2",
        "password": "Password456"
    }
    with pytest.raises(ValueError) as exc_info:
        User.register(db_session, user_data2)
    assert "Username or email already exists" in str(exc_info.value)

def test_register_duplicate_username(db_session):
    user_data = {
        "first_name": "Dup",
        "last_name": "User",
        "email": "dupuser@example.com",
        "username": "dupuser",
        "password": "Password123"
    }
    # Register first user
    User.register(db_session, user_data)
    # Try to register another user with same username
    user_data2 = {
        "first_name": "Dup2",
        "last_name": "User2",
        "email": "dupuser2@example.com",
        "username": "dupuser",
        "password": "Password456"
    }
    with pytest.raises(ValueError) as exc_info:
        User.register(db_session, user_data2)
    assert "Username or email already exists" in str(exc_info.value)



