"""
Unit Tests für app/core/security.py
Tests für Password Hashing und JWT Token Operations
"""
import pytest
from datetime import timedelta
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from app.core.config import Settings


@pytest.mark.unit
@pytest.mark.security
class TestPasswordHashing:
    """Tests für Password Hashing Funktionen"""

    def test_password_hash_is_different_from_plain(self):
        """Test: Gehashtes Passwort unterscheidet sich vom Klartext"""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_password_hash_is_unique(self):
        """Test: Gleiche Passwörter erzeugen verschiedene Hashes (wegen Salt)"""
        password = "SecurePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes sollten unterschiedlich sein wegen unterschiedlichem Salt
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test: Korrektes Passwort wird verifiziert"""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test: Falsches Passwort wird abgelehnt"""
        password = "SecurePassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        """Test: Leere Passwörter werden korrekt behandelt"""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is False

    @pytest.mark.parametrize("password", [
        "short",
        "verylongpasswordwithmanychars",  # Langes Passwort (aber unter 72 Bytes)
        "Pässwörd123!",  # Umlaute
        "密码123",  # Chinesische Zeichen
        "パスワード",  # Japanische Zeichen
    ])
    def test_password_hash_various_formats(self, password):
        """Test: Verschiedene Passwort-Formate können gehasht werden"""
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True


@pytest.mark.unit
@pytest.mark.security
class TestJWTTokens:
    """Tests für JWT Token Operations"""

    def test_create_access_token(self):
        """Test: Access Token wird erfolgreich erstellt"""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_with_custom_expiry(self):
        """Test: Token mit benutzerdefinierter Ablaufzeit"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)

        assert token is not None

        # Decode and check expiry
        payload = decode_access_token(token)
        assert payload is not None
        assert "exp" in payload

    def test_decode_valid_token(self):
        """Test: Gültiger Token wird korrekt dekodiert"""
        data = {"sub": "testuser", "user_id": 123}
        token = create_access_token(data)

        decoded = decode_access_token(token)

        assert decoded is not None
        assert decoded["sub"] == "testuser"
        assert decoded["user_id"] == 123
        assert "exp" in decoded

    def test_decode_invalid_token(self):
        """Test: Ungültiger Token gibt None zurück"""
        invalid_token = "invalid.token.here"

        decoded = decode_access_token(invalid_token)

        assert decoded is None

    def test_decode_empty_token(self):
        """Test: Leerer Token gibt None zurück"""
        decoded = decode_access_token("")
        assert decoded is None

    def test_decode_malformed_token(self):
        """Test: Fehlerhaft formatierter Token gibt None zurück"""
        malformed_tokens = [
            "notavalidtoken",
            "still.not.valid",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        ]

        for token in malformed_tokens:
            decoded = decode_access_token(token)
            assert decoded is None, f"Token should be invalid: {token}"

    def test_token_contains_expiry(self):
        """Test: Token enthält Ablaufdatum"""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        decoded = decode_access_token(token)

        assert decoded is not None
        assert "exp" in decoded
        assert isinstance(decoded["exp"], (int, float))

    def test_different_tokens_for_same_data(self):
        """Test: Gleiche Daten erzeugen unterschiedliche Tokens (wegen Timestamp)"""
        import time

        data = {"sub": "testuser"}
        token1 = create_access_token(data)
        time.sleep(1)  # 1 Sekunde Pause für unterschiedlichen exp Timestamp
        token2 = create_access_token(data)

        # Tokens sollten unterschiedlich sein wegen exp timestamp
        assert token1 != token2


@pytest.mark.unit
@pytest.mark.security
class TestSecurityConfig:
    def test_development_allows_example_secret(self):
        settings = Settings(
            _env_file=None,
            DATABASE_URL="sqlite:///./test.db",
            SECRET_KEY="your-secret-key-here-change-in-production",
            APP_ENV="development",
        )

        assert settings.SECRET_KEY == "your-secret-key-here-change-in-production"

    def test_production_rejects_example_secret(self):
        with pytest.raises(ValueError, match="SECRET_KEY"):
            Settings(
                _env_file=None,
                DATABASE_URL="sqlite:///./test.db",
                SECRET_KEY="your-secret-key-here-change-in-production",
                APP_ENV="production",
            )

    def test_production_accepts_random_secret(self):
        settings = Settings(
            _env_file=None,
            DATABASE_URL="sqlite:///./test.db",
            SECRET_KEY="a-secure-random-secret-with-at-least-32-chars",
            APP_ENV="production",
        )

        assert settings.APP_ENV == "production"
