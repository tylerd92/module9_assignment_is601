import pytest
import uuid

from app.models.calculation import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
)

def dummy_user_id():
    return uuid.uuid4()

def test_addition_get_result():
    inputs = [5.5, 4, 9]
    addition = Addition(user_id=dummy_user_id(), inputs=inputs)
    result = addition.get_result()
    assert result == sum(inputs), f"Expected {sum(inputs)}, got {result}"

def test_subtraction_get_result():
    inputs = [14, 9]
    subtraction = Subtraction(user_id=dummy_user_id(), inputs=inputs)
    result = subtraction.get_result()
    assert result == 5, f"Expected 5, got {result}"

def test_multiplication_get_result():
    inputs = [4, 5]
    multiplication = Multiplication(user_id=dummy_user_id(), inputs=inputs)
    result = multiplication.get_result()
    assert result == 20, f"Expected 20, got {result}"

def test_division_get_result():
    inputs = [49, 7]
    division = Division(user_id=dummy_user_id(), inputs=inputs)
    result = division.get_result()
    assert result == 7, f"Expected 7, got {result}"

def test_division_by_zero():
    inputs = [24, 0, 6]
    division = Division(user_id=dummy_user_id(), inputs=inputs)
    with pytest.raises(ValueError, match="Cannot divide by zero."):
        division.get_result()

def test_invalid_inputs_for_addition():
    addition = Addition(user_id=dummy_user_id(), inputs="not-a-list")
    with pytest.raises(ValueError, match="Inputs must be a list of numbers."):
        addition.get_result()

def test_invalid_inputs_for_subtraction():
    subtraction = Subtraction(user_id=dummy_user_id(), inputs=[10])
    with pytest.raises(ValueError, match="Inputs must be a list with at least two numbers."):
        subtraction.get_result()

def test_invalid_inputs_for_division():
    division = Division(user_id=dummy_user_id(), inputs=[9])
    with pytest.raises(ValueError, match="Inputs must be a list with at least two numbers."):
        division.get_result()

def test_not_list_as_input_for_division():
    division = Division(user_id=dummy_user_id(), inputs="not-a-list")
    with pytest.raises(ValueError, match="Inputs must be a list of numbers."):
        division.get_result()

def test_short_list_for_multiplication():
    multiplication = Multiplication(user_id=dummy_user_id(), inputs=[3])
    with pytest.raises(ValueError, match="Inputs must be a list with at least two numbers."):
        multiplication.get_result()

def test_invalid_list_for_multiplication():
    multiplication = Multiplication(user_id=dummy_user_id(), inputs="test")
    with pytest.raises(ValueError, match="Inputs must be a list of numbers."):
        multiplication.get_result()

def test_calculcation_factory_addition():
    inputs = [1, 2, 3]
    calc = Calculation.create_calculation(
        calculation_type='addition',
        user_id=dummy_user_id(),
        inputs=inputs,
    )
    assert isinstance(calc, Addition), "Factory did not return an Addition instance."
    assert calc.get_result() == sum(inputs), "Incorrect addition result."

def test_calculation_factory_subtraction():
    inputs = [15, 7]
    calc = Calculation.create_calculation(
        calculation_type='subtraction',
        user_id=dummy_user_id(),
        inputs=inputs
    )
    assert isinstance(calc, Subtraction), "Factory did not return an Subtraction instance"
    assert calc.get_result() == 8, "Incorrect subtraction result."

def test_calculation_factory_multiplication():
    inputs = [6, 5]
    calc = Calculation.create_calculation(
        calculation_type='multiplication',
        user_id=dummy_user_id(),
        inputs=inputs,
    )

    assert isinstance(calc, Multiplication), "Factory did not return a Multiplication instance."
    assert calc.get_result() == 30, "Incorrect multiplication result."

def test_calculation_factory_division():
    inputs = [25, 5]
    calc = Calculation.create_calculation(
        calculation_type='division',
        user_id=dummy_user_id(),
        inputs=inputs
    )
    assert isinstance(calc, Division), "Factory did not return a Division instance."
    assert calc.get_result() == 5, "Incorrect division result."

def test_calculation_factory_invalid_type():
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        Calculation.create_calculation(
            calculation_type="power",
            user_id=dummy_user_id(),
            inputs=[2, 3]
        )