from pydantic import BaseModel, EmailStr, Field, ConfigDict, ValidationError, model_validator
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    first_name: str = Field(max_length=50, example="John")
    last_name: str = Field(max_length=50, example="Doe")