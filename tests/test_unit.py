# tests/test_unit.py
import pytest
from pydantic import ValidationError
from app.schemas.scan import ScanCreateInput
from app.services.auth import hash_password, verify_password

def test_password_hashing():
    password = "secret_farmer_pass"
    h_pass = hash_password(password)
    
    assert h_pass != password
    assert verify_password(password, h_pass) is True
    assert verify_password("wrong_pass", h_pass) is False

def test_pydantic_coordinate_validation():
    # Valid Coordinates
    valid_input = ScanCreateInput(crop_id=1, latitude=12.9716, longitude=77.5946)
    assert valid_input.latitude == 12.9716

    # Invalid latitude boundaries
    with pytest.raises(ValidationError):
        ScanCreateInput(crop_id=1, latitude=95.0, longitude=77.5946)

    # Invalid longitude boundaries
    with pytest.raises(ValidationError):
        ScanCreateInput(crop_id=1, latitude=12.9716, longitude=185.0)
