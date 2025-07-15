import pytest
from pydantic import ValidationError
from app.schemas.base import UserBase, PasswordMixin, UserCreate, UserLogin

def test_user_base_valid():
    data = {
        "first_name": "Jeff",
        "last_name": "Smith",
        "email": "jeff.smith@example.com",
        "username": "jsmith",
    }

    user = UserBase(**data)
    assert user.first_name == "Jeff"
    assert user.email == "jeff.smith@example.com"

def test_user_base_invalid_email():
    data = {
        "first_name": "Jeff",
        "last_name": "Smith",
        "email": "invalid-email",
        "username": "jsmith",
    }
    with pytest.raises(ValidationError):
        UserBase(**data)

def test_password_mixin_valid():
    data = {"password": "SecurePass123"}
    password_mixin = PasswordMixin(**data)
    assert password_mixin.password == "SecurePass123"

def test_password_mixin_invalid_short_password():
    data = {"password": "test"}
    with pytest.raises(ValidationError):
        PasswordMixin(**data)

def test_password_mixin_no_uppercase():
    data = {"password": "password123"}
    with pytest.raises(ValidationError, match="Password must contain at least one uppercase letter"):
        PasswordMixin(**data)

def test_password_mixin_no_lowercase():
    data = {"password": "ALLUPPERCASE4"}
    with pytest.raises(ValidationError, match="Password must contain at least one lowercase letter"):
        PasswordMixin(**data)

def test_password_mixin_no_digit():
    data = {"password": "TestNoDigits"}
    with pytest.raises(ValidationError, match="Password must contain at least one digit"):
        PasswordMixin(**data)

def test_user_create_valid():
    data = {
        "first_name": "Jeff",
        "last_name": "Smith",
        "email": "jeff.smith@example.com",
        "username": "jsmith",
        "password": "SecurePass123"
    }
    user_create = UserCreate(**data)
    assert user_create.username == "jsmith"
    assert user_create.password == "SecurePass123"

def test_user_create_invalid_password():
    data = {
        "first_name": "Jeff",
        "last_name": "Smith",
        "email": "jeff.smith@example.com",
        "username": "jsmith",
        "password": "test"
    }
    with pytest.raises(ValidationError):
        UserCreate(**data)

def test_user_login_valid():
    data = {"username": "jsmith", "password": "SecurePass123"}
    user_login = UserLogin(**data)
    assert user_login.username == "jsmith"

def test_user_login_invalid_username():
    data = {"username": "js", "password": "SecurePass123"}
    with pytest.raises(ValidationError):
        UserLogin(**data)

def test_user_login_invalid_password():
    data = {"username": "jsmith", "password": "short"}
    with pytest.raises(ValidationError):
        UserLogin(**data)