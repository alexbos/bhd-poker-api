import pytest
from vpoker_flask import app
import random
import string
import time

@pytest.fixture(autouse=True)
def delay_after_test():
    yield  # This will run the test function
    time.sleep(1.5)  # After the test, sleep for 1.5 seconds

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_connectable(client):
    response = client.get('/')
    assert response.status_code == 200
    # assert response.is_json
    # json_data = response.get_json()
    # assert 'key' in json_data
    # assert json_data['key'] == 'expected value'

def test_analyze_hand(client):
    # Prepare the test data
    hand_string = 'ackc8h4sth'
    
    # Expected response structure
    expected_keys = {"expected_val", "flush", "four_kind", "full_house", "pair_jqka", "royal_flush", "straight", "straight_flush", "three_kind", "two_pair"}
    
    # Send a POST request to the /analyze-hand endpoint
    response = client.post('/analyze-hand', json={'hand': hand_string})
    
    # Check that the status code is 200 (OK)
    assert response.status_code == 200
    
    # Check that the response is JSON
    assert response.is_json
    
    # Get the JSON data from the response
    json_data = response.get_json()
    
    # Check that the JSON data includes the expected hand key
    assert "AcKcXXXXXX" in json_data
    
    # Retrieve the hand data
    hand_data = json_data["AcKcXXXXXX"]
    
    # Check that the hand data includes all expected keys
    assert expected_keys == set(hand_data.keys())

def test_analyze_hand_error(client):
    # Prepare the invalid test data
    invalid_hand_string = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=20))
    
    # Expected error response
    expected_response = {"error": "Invalid card string."}
    
    # Send a POST request to the /analyze-hand endpoint with the invalid hand string
    response = client.post('/analyze-hand', json={'hand': invalid_hand_string})
    
    # Check that the status code indicates client error (you might need to adjust this based on your API's behavior)
    assert response.status_code == 400
    
    # Check that the response is JSON
    assert response.is_json
    
    # Get the JSON data from the response
    json_data = response.get_json()
    
    # Check that the JSON data matches the expected error response
    assert json_data == expected_response
