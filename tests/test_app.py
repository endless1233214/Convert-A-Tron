from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

def test_homepage():
    response = client.get('/')
    assert response.status_code == 200
    assert 'Convert-A-Tron' in response.text
    assert '/convert/jpg' in response.text

def test_dedicated_converter_page():
    response = client.get('/convert/docx')
    assert response.status_code == 200
    assert 'Convert DOCX files' in response.text
    assert '<option value="pdf">PDF</option>' in response.text
    assert 'accept=".docx"' in response.text

def test_unknown_converter_page():
    response = client.get('/convert/nope')
    assert response.status_code == 404

def test_capabilities_include_input_formats():
    response = client.get('/api/capabilities')
    assert response.status_code == 200
    assert 'jpg' in response.json()['input_formats']
    assert 'docx' in response.json()['input_formats']
