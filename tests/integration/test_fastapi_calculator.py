import pytest
import logging
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_add_api(client):
    response = client.post('/add', json={'a': 10, 'b': 5})

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    assert response.json()['result'] == 15, f"Expected result 15, got {response.json()['result']}"

def test_subtract_api(client):
    response = client.post('/subtract', json={'a': 10, 'b': 5})

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    assert response.json()['result'] == 5, f"Expected result 5, got {response.json()['result']}"

def test_multiply_api(client):
    response = client.post('/multiply', json={'a': 10, 'b': 5})

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    assert response.json()['result'] == 50, f"Expected result 50, got {response.json()['result']}"

def test_divide_api(client):
    response = client.post('/divide', json={'a': 10, 'b': 2})

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    assert response.json()['result'] == 5, f"Expected result 5, got {response.json()['result']}"

def test_divide_by_zero_api(client):
    response = client.post('/divide', json={'a': 10, 'b': 0})

    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"

    assert 'error' in response.json(), "Response JSON does not contain 'error' field"

    assert "Cannot divide by zero!" in response.json()['error'], \
        f"Expected error message 'Cannot divide by zero!', got '{response.json()['error']}'"
    
def test_logging(client, caplog):
    # Set logging level to capture INFO logs
    caplog.set_level(logging.INFO)
    
    response = client.post('/add', json={'a': 10, 'b': 5})

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    assert "10 + 5" in caplog.text, "Log does not contain expected message for addition"

    response = client.post('/subtract', json={'a': 10, 'b': 5})

    assert "10 - 5" in caplog.text, "Log does not contain expected message for subtraction"