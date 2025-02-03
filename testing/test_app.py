import pytest
from flask import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_language_details(client):
    response = client.get('/languages/Unlambda')
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.get_data(as_text=True)
        assert "Unlambda" in data

def test_search_languages(client):
    response = client.get('/languages/search?name=test&page=1&limit=5')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'data' in data
    assert isinstance(data['data'], list)
    assert 'pagination' in data

def test_get_unique_years(client):
    response = client.get('/languages/years')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'years' in data
    assert isinstance(data['years'], list)

def test_get_unique_designers(client):
    response = client.get('/languages/designers')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'designers' in data
    assert isinstance(data['designers'], list)

def test_get_language_details_with_filters(client):
    response = client.get('/languages/details?year=2020&page=1&limit=5')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'data' in data
    assert isinstance(data['data'], list)
    assert 'pagination' in data

def test_compute_embeddings(client):
    response = client.get('/compute_embeddings')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == "Embeddings computed or loaded successfully!"

def test_get_similar_languages(client):
    payload = {"given_language": "http://example.org/ontology/esoteric_languages#Brainfuck"}
    response = client.post('/get_similar_languages', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'given_language' in data
    assert 'similar_languages' in data
    payload = {"invalid_key": "http://example.org/ontology/esoteric_languages#Brainfuck"}
    response = client.post('/get_similar_languages', json=payload)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_escape_special_characters():
    from app import escape_special_characters
    input_name = "name#value"
    escaped = escape_special_characters(input_name)
    assert escaped == "name\\#value"


def test_compare_languages():
    tester = app.test_client()
    response = tester.post('/compare_languages', json={
        'given_language': '0815',
        'similar_language': '123'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert 'comparison' in data
    assert isinstance(data['comparison'], list)
    assert len(data['comparison']) > 0



def test_get_similar_languages_missing_param(client):
    response = client.post('/get_similar_languages', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

# Test invalid language format in /get_similar_languages

def test_get_similar_languages_invalid(client):
    payload = {"given_language": "InvalidLanguageName"}
    response = client.post('/get_similar_languages', json=payload)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

# Test /compare_languages with missing data

def test_compare_languages_missing_params(client):
    response = client.post('/compare_languages', json={'given_language': 'Lisp'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

# Test /compare_languages with non-existent languages
def test_compute_embeddings_no_embeddings(client, monkeypatch):
    def mock_load_embeddings():
        return None  # Simulate missing embeddings

    monkeypatch.setattr("app.load_entity_embeddings", mock_load_embeddings)
    response = client.get('/compute_embeddings')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data

# Test edge case: search with no results

def test_search_languages_no_results(client):
    response = client.get('/languages/search?name=NoSuchLanguage&page=1&limit=5')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'data' in data
    assert isinstance(data['data'], list)
    assert len(data['data']) == 0  # Expecting no results

# Test special character escaping

def test_escape_special_characters():
    from app import escape_special_characters
    input_name = "name#value+test/path"
    escaped = escape_special_characters(input_name)
    assert escaped == "name\\#value\\+test\\/path"
