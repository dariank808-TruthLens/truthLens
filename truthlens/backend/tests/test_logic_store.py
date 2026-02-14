"""Tests for backend.logic.store module."""
import pytest
from backend.logic import store


@pytest.fixture(autouse=True)
def clear_stores():
    """Clear in-memory stores before and after each test."""
    # Clear before
    store._users.clear()
    store._uploads.clear()
    store._analyses.clear()
    
    yield
    
    # Clear after
    store._users.clear()
    store._uploads.clear()
    store._analyses.clear()


class TestUserStore:
    """Test user document CRUD operations."""

    def test_save_and_get_user(self):
        """save_user and get_user work together."""
        user_id = "user::12345"
        user_doc = {
            "id": user_id,
            "name": "Alice",
            "email": "alice@example.com",
            "wallet_address": "0x123...",
        }
        
        store.save_user(user_id, user_doc)
        retrieved = store.get_user(user_id)
        
        assert retrieved == user_doc
        assert retrieved["name"] == "Alice"

    def test_get_nonexistent_user(self):
        """get_user returns None for nonexistent user."""
        result = store.get_user("user::nonexistent")
        assert result is None

    def test_delete_user(self):
        """delete_user removes a user and returns True."""
        user_id = "user::12345"
        user_doc = {"id": user_id, "name": "Bob"}
        
        store.save_user(user_id, user_doc)
        assert store.get_user(user_id) is not None
        
        deleted = store.delete_user(user_id)
        assert deleted is True
        assert store.get_user(user_id) is None

    def test_delete_nonexistent_user(self):
        """delete_user returns False for nonexistent user."""
        result = store.delete_user("user::nonexistent")
        assert result is False

    def test_update_user(self):
        """Users can be updated by saving with same ID."""
        user_id = "user::12345"
        
        store.save_user(user_id, {"id": user_id, "name": "Charlie"})
        store.save_user(user_id, {"id": user_id, "name": "Charles"})
        
        retrieved = store.get_user(user_id)
        assert retrieved["name"] == "Charles"


class TestUploadStore:
    """Test upload document CRUD operations."""

    def test_save_and_get_upload(self):
        """save_upload and get_upload work together."""
        upload_id = "upload::abc123"
        upload_doc = {
            "id": upload_id,
            "user_id": "user::123",
            "status": "pending",
            "files": [],
        }
        
        store.save_upload(upload_id, upload_doc)
        retrieved = store.get_upload(upload_id)
        
        assert retrieved == upload_doc
        assert retrieved["status"] == "pending"

    def test_get_nonexistent_upload(self):
        """get_upload returns None for nonexistent upload."""
        result = store.get_upload("upload::nonexistent")
        assert result is None

    def test_delete_upload(self):
        """delete_upload removes an upload."""
        upload_id = "upload::abc123"
        store.save_upload(upload_id, {"id": upload_id})
        
        deleted = store.delete_upload(upload_id)
        assert deleted is True
        assert store.get_upload(upload_id) is None

    def test_delete_nonexistent_upload(self):
        """delete_upload returns False for nonexistent upload."""
        result = store.delete_upload("upload::nonexistent")
        assert result is False


class TestAnalysisStore:
    """Test analysis document CRUD operations."""

    def test_save_and_get_analysis(self):
        """save_analysis and get_analysis work together."""
        analysis_id = "analysis::xyz789"
        analysis_doc = {
            "id": analysis_id,
            "upload_id": "upload::abc",
            "status": "ready",
            "breakdown": {
                "overall_credibility_score": 0.75,
            },
        }
        
        store.save_analysis(analysis_id, analysis_doc)
        retrieved = store.get_analysis(analysis_id)
        
        assert retrieved == analysis_doc
        assert retrieved["status"] == "ready"

    def test_get_nonexistent_analysis(self):
        """get_analysis returns None for nonexistent analysis."""
        result = store.get_analysis("analysis::nonexistent")
        assert result is None

    def test_delete_analysis(self):
        """delete_analysis removes an analysis."""
        analysis_id = "analysis::xyz789"
        store.save_analysis(analysis_id, {"id": analysis_id})
        
        deleted = store.delete_analysis(analysis_id)
        assert deleted is True
        assert store.get_analysis(analysis_id) is None

    def test_delete_nonexistent_analysis(self):
        """delete_analysis returns False for nonexistent analysis."""
        result = store.delete_analysis("analysis::nonexistent")
        assert result is False


class TestStoreInteraction:
    """Test interactions between different store types."""

    def test_multiple_documents(self):
        """Store can hold multiple documents of different types."""
        user_id = "user::1"
        upload_id = "upload::1"
        analysis_id = "analysis::1"
        
        store.save_user(user_id, {"id": user_id, "name": "User"})
        store.save_upload(upload_id, {"id": upload_id, "status": "pending"})
        store.save_analysis(analysis_id, {"id": analysis_id, "status": "ready"})
        
        assert store.get_user(user_id) is not None
        assert store.get_upload(upload_id) is not None
        assert store.get_analysis(analysis_id) is not None

    def test_store_isolation(self):
        """Deleting one document type doesn't affect others."""
        user_id = "user::1"
        upload_id = "upload::1"
        
        store.save_user(user_id, {"id": user_id})
        store.save_upload(upload_id, {"id": upload_id})
        
        store.delete_user(user_id)
        
        assert store.get_user(user_id) is None
        assert store.get_upload(upload_id) is not None
