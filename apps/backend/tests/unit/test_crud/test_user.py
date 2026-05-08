"""
Unit Tests für app/crud/user.py
Tests für User CRUD Operations
"""
import pytest
from sqlalchemy.orm import Session
from app.crud.user import (
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
    create_user,
    authenticate_user
)
from app.schemas.user import UserCreate
from app.models.user import User


@pytest.mark.unit
class TestUserCRUD:
    """Tests für User CRUD Operationen"""

    def test_create_user(self, db: Session):
        """Test: User wird erfolgreich erstellt"""
        user_data = UserCreate(
            username="newuser",
            email="newuser@example.com",
            password="SecurePassword123!"
        )

        user = create_user(db, user_data)

        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.hashed_password != "SecurePassword123!"  # Sollte gehasht sein
        assert len(user.hashed_password) > 0

    def test_create_user_password_is_hashed(self, db: Session):
        """Test: Passwort wird beim Erstellen gehasht"""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="plainpassword"
        )

        user = create_user(db, user_data)

        # Passwort sollte nicht im Klartext gespeichert sein
        assert user.hashed_password != "plainpassword"
        assert user.hashed_password.startswith("$2b$")  # bcrypt hash format

    def test_get_user_by_username(self, db: Session, test_user: User):
        """Test: User wird per Username gefunden"""
        found_user = get_user_by_username(db, test_user.username)

        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.username == test_user.username

    def test_get_user_by_username_not_found(self, db: Session):
        """Test: Nicht existierender Username gibt None zurück"""
        found_user = get_user_by_username(db, "nonexistent")

        assert found_user is None

    def test_get_user_by_email(self, db: Session, test_user: User):
        """Test: User wird per Email gefunden"""
        found_user = get_user_by_email(db, test_user.email)

        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.email == test_user.email

    def test_get_user_by_email_not_found(self, db: Session):
        """Test: Nicht existierende Email gibt None zurück"""
        found_user = get_user_by_email(db, "nonexistent@example.com")

        assert found_user is None

    def test_get_user_by_id(self, db: Session, test_user: User):
        """Test: User wird per ID gefunden"""
        found_user = get_user_by_id(db, test_user.id)

        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.username == test_user.username

    def test_get_user_by_id_not_found(self, db: Session):
        """Test: Nicht existierende ID gibt None zurück"""
        found_user = get_user_by_id(db, 99999)

        assert found_user is None

    def test_authenticate_user_success(self, db: Session, test_user: User, test_user_data: dict):
        """Test: User wird erfolgreich authentifiziert"""
        authenticated = authenticate_user(
            db,
            test_user_data["username"],
            test_user_data["password"]
        )

        assert authenticated is not None
        assert authenticated.id == test_user.id
        assert authenticated.username == test_user.username

    def test_authenticate_user_wrong_password(self, db: Session, test_user: User):
        """Test: Falsche Passwort-Authentifizierung schlägt fehl"""
        authenticated = authenticate_user(db, test_user.username, "wrongpassword")

        assert authenticated is None

    def test_authenticate_user_wrong_username(self, db: Session):
        """Test: Falscher Username-Authentifizierung schlägt fehl"""
        authenticated = authenticate_user(db, "nonexistent", "anypassword")

        assert authenticated is None

    def test_authenticate_user_empty_credentials(self, db: Session):
        """Test: Leere Credentials schlagen fehl"""
        authenticated = authenticate_user(db, "", "")

        assert authenticated is None

    def test_multiple_users_can_exist(self, db: Session):
        """Test: Mehrere User können gleichzeitig existieren"""
        users_data = [
            UserCreate(username=f"user{i}", email=f"user{i}@example.com", password=f"password{i}")
            for i in range(5)
        ]

        created_users = [create_user(db, user_data) for user_data in users_data]

        assert len(created_users) == 5

        # Alle User sollten unique IDs haben
        user_ids = [u.id for u in created_users]
        assert len(set(user_ids)) == 5

        # Alle User sollten findbar sein
        for user in created_users:
            found = get_user_by_username(db, user.username)
            assert found is not None
            assert found.id == user.id


@pytest.mark.unit
class TestUserModel:
    """Tests für User Model Properties"""

    def test_user_has_required_fields(self, test_user: User):
        """Test: User hat alle erforderlichen Felder"""
        assert hasattr(test_user, 'id')
        assert hasattr(test_user, 'username')
        assert hasattr(test_user, 'email')
        assert hasattr(test_user, 'hashed_password')
        assert hasattr(test_user, 'is_active')
        assert hasattr(test_user, 'is_verified')

    def test_user_default_values(self, db: Session):
        """Test: User hat korrekte Default-Werte"""
        user_data = UserCreate(
            username="defaultuser",
            email="default@example.com",
            password="password"
        )
        user = create_user(db, user_data)

        # is_active sollte standardmäßig True sein (aus conftest)
        assert user.is_active is True

