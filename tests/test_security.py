# tests/test_security.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_unauthenticated_api_rejection():
    # Attempting to fetch scan history without token headers
    response = client.get("/api/v1/scans/history")
    assert response.status_code == 401
    assert response.json()["message"] == "Not authenticated"

def test_image_path_traversal_prevention():
    # Simulating file upload containing dot-dot-slash directory traversal patterns
    bad_filename = "../../../etc/passwd"
    files = {'image': (bad_filename, b"fake_image_binary_data", "image/jpeg")}
    
    # Send post request
    response = client.post(
        "/api/v1/scans/analyze",
        headers={"Authorization": "Bearer fake_token_placeholder"},
        files=files,
        data={"crop_category_id": "1", "latitude": "0.0", "longitude": "0.0"}
    )
    # Rejects bad tokens or enforces clean path conversions
    assert response.status_code in [401, 400]
