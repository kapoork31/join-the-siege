import pytest
from fastapi.testclient import TestClient
import sys
import os

from fastapi.testclient import TestClient

from src.fastapi_app import app
from src.data_models.tables import File as FileModel

from unittest.mock import MagicMock
from io import BytesIO

# mock none obj back from db in files table
@pytest.fixture
def mock_no_file_obj_none(mocker):
    return mocker.patch('src.fastapi_app.get_file_metadata', return_value=None)

# mock an obj back from db in files table
@pytest.fixture
def mock_file_obj(mocker):
    file_obj = FileModel(s3Path='some/path/to/file', filename="test.pdf", customerId=1)
    return mocker.patch('src.fastapi_app.get_file_metadata', return_value = file_obj)

# mock none returned from getting files bytes from s3
@pytest.fixture
def mock_s3_file_bytes_none(mocker):
    return mocker.patch('src.fastapi_app.download_file_return_bytes', return_value = None)

# mock writing to db to update item in db
@pytest.fixture
def update_file_classification(mocker):
    return mocker.patch('src.fastapi_app.update_file_classification', return_value = None)

# mock the return from reading from s3 and getting file bytes
@pytest.fixture
def mock_s3_file_bytes(mocker):
    # Load the PDF file content from the local file system
    with open('tests/test_files/bank_statement_1.pdf', "rb") as f:
        file_content = f.read()  # Read file content as bytes
    
    # Create a BytesIO object to simulate file-like behavior
    file_bytes_io = BytesIO(file_content)

    # Mock `extract_text_from_file` to return extracted text from the file bytes
    return mocker.patch('src.fastapi_app.download_file_return_bytes', return_value=file_bytes_io)

# Mock the database sessin
@pytest.fixture
def mock_db_session(mocker):
    mock_db = MagicMock()
    mocker.patch('src.fastapi_app.get_db', return_value=mock_db)
    return mock_db

# mock s3 session
@pytest.fixture
def mock_s3_client(mocker):
    mock_s3 = MagicMock()
    mocker.patch('src.fastapi_app.get_s3_client', return_value=mock_s3)
    return mock_s3

# Create a test client for FastAPI
@pytest.fixture
def client():
    return TestClient(app)

# Test case for general unexpected error handling
def test_classify_file_does_not_exist(mock_db_session, mock_s3_client, mock_no_file_obj_none, client):
    # mock file not in db
    res = client.post("/classify_file", json={"customer_id": 1, "filename": "test.pdf"})
    assert res.status_code == 404

def test_classify_file_failed_file_bytes(mock_db_session, mock_s3_client, mock_file_obj, mock_s3_file_bytes_none, client):
    res = client.post("/classify_file", json={"customer_id": 1, "filename": "test.pdf"})
    assert res.status_code == 500

# Test case for a valid file classification
def test_classify_file_valid(client, mock_db_session, mock_s3_client, mock_file_obj, mock_s3_file_bytes, update_file_classification):
    response = client.post("/classify_file", json={"customer_id": 1, "filename": "test.pdf"})

    assert response.status_code == 200
    assert response.json()['data'] == {
        "file_class": "bank_statement",
        "filename": "test.pdf",
        "customer_id": 1
    }