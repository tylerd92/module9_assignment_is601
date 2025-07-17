import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime
from app.schemas.calculation import (
    CalculationCreate,
    CalculationUpdate,
    CalculationResponse
)

def test_calculation_create_valid():
    data = {
        "type": "addition",
        "inputs": [10.5, 3.0],
        "user_id": uuid4()
    }
    calc = CalculationCreate(**data)
    assert calc.type == "addition"
    assert calc.inputs == [10.5, 3.0]
    assert calc.user_id is not None

def test_calculation_create_missing_type():
    data = {
        "inputs": [10.5, 3.0],
        "user_id": uuid4()
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(**data)
    assert "required" in str(exc_info).lower()

def test_calculation_create_missing_inputs():
    data = {
        "type": "multiplication",
        "user_id": uuid4()
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(**data)
    assert "required" in str(exc_info.value).lower()

def test_calculation_create_invalid_inputs():
    data = {
        "type": "division",
        "inputs": "not-a-list",
        "user_id": uuid4()
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(**data)
    error_message = str(exc_info.value)
    assert "input should be a valid list" in error_message.lower(), error_message

def test_calculation_create_unsupported_type():
    data = {
        "type": "square_root",
        "inputs": [25],
        "user_id": uuid4()
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(**data)

        error_message = str(exc_info.value).lower()
        assert "one of" in error_message or "not a valid" in error_message

def test_calculation_update_valid():
    data = {
        "inputs": [42.0, 7.0]
    }
    calc_update = CalculationUpdate(**data)
    assert calc_update.inputs == [42.0, 7.0]

def test_calcuiation_update_no_fields():
    calc_update = CalculationUpdate()
    assert calc_update.inputs is None

def test_calculation_response_valid():
    data = {
        "id": uuid4(),
        "user_id": uuid4(),
        "type": "subtraction",
        "inputs": [20, 5],
        "result": 15.5,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    calc_response = CalculationResponse(**data)
    assert calc_response.id is not None
    assert calc_response.user_id is not None
    assert calc_response.type == "subtraction"
    assert calc_response.inputs == [20, 5]
    assert calc_response.result == 15.5

def test_division_with_zero_as_second_input():
    data = {
        "type": "division",
        "inputs": [14, 0],
        "user_id": uuid4()
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(**data)
    error_message = str(exc_info.value).lower()
    assert "zero" in error_message or "cannot divide by zero" in error_message, error_message