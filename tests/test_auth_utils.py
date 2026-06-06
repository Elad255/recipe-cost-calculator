import pytest
from app.utils.auth import hash_password, verify_password, create_access_token, verify_access_token


class TestPasswordHashing:

    def test_hash_password_returns_different_string(self):
        password = "shakshuka123"
        hashed = hash_password(password)
        assert hashed != password

    def test_hash_password_different_each_time(self):
        password = "shakshuka123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_verify_correct_password(self):
        password = "shakshuka123"
        hashed = hash_password(password)
        result = verify_password(password, hashed)
        assert result == True

    def test_verify_wrong_password(self):
        hashed = hash_password("shakshuka123")
        result = verify_password("wrong_password", hashed)
        assert result == False


class TestJWTTokens:

    def test_create_token_returns_string(self):
        token = create_access_token(data={"sub": "chef@kitchen.com"})
        assert isinstance(token, str)

    def test_verify_valid_token(self):
        token = create_access_token(data={"sub": "chef@kitchen.com"})
        payload = verify_access_token(token)
        assert payload is not None
        assert payload["sub"] == "chef@kitchen.com"

    def test_verify_invalid_token(self):
        result = verify_access_token("this.is.a.fake.token")
        assert result is None