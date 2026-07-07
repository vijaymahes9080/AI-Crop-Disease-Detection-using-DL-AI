# tests/locustfile.py
from locust import HttpUser, task, between
import random

class FarmUser(HttpUser):
    wait_time = between(2, 5) # Mimics user wait time before actions
    token = None

    def on_start(self):
        # Register user and extract JWT token
        username = f"+91{random.randint(1000000000, 9999999999)}"
        response = self.client.post("/api/v1/auth/register", json={
            "phone_number": username,
            "name": "Locust Farmer",
            "password": "secure_locust_pass"
        })
        if response.status_code == 201:
            self.token = response.json()["access_token"]

    @task(3)
    def upload_scan(self):
        if not self.token:
            return
            
        # Send mock upload payload
        dummy_file = b"fake_jpeg_image_data_buffer_representing_a_crop_leaf"
        self.client.post(
            "/api/v1/scans/analyze",
            headers={"Authorization": f"Bearer {self.token}"},
            files={'image': ('leaf.jpg', dummy_file, 'image/jpeg')},
            data={
                "crop_category_id": "1",
                "latitude": "12.9716",
                "longitude": "77.5946"
            }
        )

    @task(1)
    def fetch_history(self):
        if not self.token:
            return
        self.client.get(
            "/api/v1/scans/history",
            headers={"Authorization": f"Bearer {self.token}"}
        )
