import pytest
from pydantic import ValidationError
from app.schemas.base import UserBase, PasswordMixin, UserCreate, UserLogin

def test_user_base_valid():
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "username": "johndoe",
    }

    user = UserBase(**data)
    assert user.first_name == "John"
    assert user.email == "john.doe@example.com"