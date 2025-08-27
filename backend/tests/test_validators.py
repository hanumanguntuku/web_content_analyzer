import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from src.utils.validators import URLValidator, ValidationResult

def test_valid_url():
    validator = URLValidator()
    result = validator.validate_url("https://example.com")
    assert isinstance(result, ValidationResult)
    assert result.is_valid

def test_invalid_scheme():
    validator = URLValidator()
    result = validator.validate_url("ftp://example.com")
    assert not result.is_valid
    assert result.error_type == "format_error"

def test_blocked_hostname():
    validator = URLValidator()
    result = validator.validate_url("http://localhost")
    assert not result.is_valid
    assert result.error_type == "hostname_blocked"
