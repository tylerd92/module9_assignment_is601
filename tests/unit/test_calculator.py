import pytest 
from typing import Union
from app.operations import add, subtract, multiply, divide


Number = Union[int, float]

@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (2.5, 3.5, 6.0),
    (-1, 1, 0),
    (0, 0, 0),
    (100, 200, 300),
],
ids=["positive_integers", "float_addition", "negative_case", "zero_case", "large_numbers"])
def test_add(a: Number, b: Number, expected: Number):
    result = add(a, b)
    assert result == expected, f"Expected {expected} but got {result} for add({a}, {b})"

@pytest.mark.parametrize("a, b, expected", [
    (5, 3, 2),
    (10.5, 2.5, 8.0),
    (0, 0, 0),
    (100, 50, 50),
    (1, 2, -1),
],
ids=["positive_integers", "float_subtraction", "zero_case", "large_numbers", "negative_result"]
)
def test_subtract(a: Number, b: Number, expected: Number):
    result = subtract(a, b)
    assert result == expected, f"Expected {expected} but got {result} for subtract({a}, {b})"

@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 6),
    (1.5, 2.0, 3.0),
    (0, 5, 0),
    (10, 0, 0),
    (100, 2, 200),
],
ids=["positive_integers", "float_multiplication", "zero_case", "zero_multiplication", "large_numbers"])
def test_multiply(a: Number, b: Number, expected: Number):
    result = multiply(a, b)
    assert result == expected, f"Expected {expected} but got {result} for multiply({a}, {b})"
    
@pytest.mark.parametrize("a, b, expected", [
    (6, 3, 2),
    (7.5, 2.5, 3.0),
    (0, 1, 0),
    (100, 10, 10),
    (1, 2, 0.5),
],
ids=["positive_integers", "float_division", "zero_case", "large_numbers", "fractional_result"])
def test_divide(a: Number, b: Number, expected: Number):
    result = divide(a, b)
    assert result == expected, f"Expected {expected} but got {result} for divide({a}, {b})"

def test_divide_by_zero() -> None:
    with pytest.raises(ValueError) as excinfo:
        divide(10, 0)
    
    assert "Cannot divide by zero!" in str(excinfo.value), \
        f"Expected error message 'Cannot divide by zero!', but got '{excinfo.value}'"