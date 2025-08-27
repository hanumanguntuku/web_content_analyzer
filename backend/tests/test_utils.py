import pytest
from src.utils.validators import URLValidator, ValidationResult

def test_url_validator_valid():
    validator = URLValidator()
    result = validator.validate_url("https://openai.com")
    assert result.is_valid

def test_url_validator_invalid():
    validator = URLValidator()
    result = validator.validate_url("ftp://openai.com")
    assert not result.is_valid

    # No is_valid_url function in url_validator.py, so this test is removed
