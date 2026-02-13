"""Tests for GraphQL resolvers."""
import pytest
import asyncio
from backend.logic import store
from backend.graphql.graphql_resolvers import Query, Mutation
from backend.graphql.graphql_types import (
    CreateUserInput, CreateUploadInput, FileInput, UploadSettingsInput
)


@pytest.fixture(autouse=True)
def clear_stores():
    """Clear stores before and after each test."""
    for s in [store._users, store._uploads, store._analyses]:
        s.clear()
    yield
    for s in [store._users, store._uploads, store._analyses]:
        s.clear()


class TestQueryResolver:
    """Test GraphQL Query resolvers."""

    def test_query_user_exists(self):
        """Query.user() returns user when it exists."""
        # Setup: save a user
        user_id = "user::test123"
        store.save_user(user_id, {
            "id": user_id,
            "account_id": "acc123",
            "name": "Alice",
            "email": "alice@example.com",
            "wallet_address": "0x123",
            "created_at": "2026-02-13T10:00:00Z",
        })
        
        # Test
        query = Query()
        result = query.user(user_id)
        
        assert result is not None
        assert result.id == user_id
        assert result.name == "Alice"
        assert result.email == "alice@example.com"

    def test_query_user_not_found(self):
        """Query.user() returns None when user doesn't exist."""
        query = Query()
        result = query.user("user::nonexistent")
        
        assert result is None

    def test_query_upload_exists(self):
        """Query.upload() returns upload when it exists."""
        upload_id = "upload::test123"
        store.save_upload(upload_id, {
            "id": upload_id,
            "user_id": "user::123",
            "created_at": "2026-02-13T10:00:00Z",
            "status": "pending",
            "files": [],
            "settings": {
                "fact_check": True,
                "logical_fallacy_check": False,
                "ai_generation_check": True,
            },
            "analysis_id": None,
        })
        
        query = Query()
        result = query.upload(upload_id)
        
        assert result is not None
        assert result.id == upload_id
        assert result.status == "pending"

    def test_query_analysis_exists(self):
        """Query.analysis() returns analysis when it exists."""
        analysis_id = "analysis::test123"
        store.save_analysis(analysis_id, {
            "id": analysis_id,
            "upload_id": "upload::123",
            "status": "ready",
            "started_at": "2026-02-13T10:00:00Z",
            "finished_at": "2026-02-13T10:05:00Z",
            "summary": {"fact_checks": 5, "fallacies": 2, "ai_score": None},
            "breakdown": {
                "fact_check_score": 0.8,
                "logical_fallacy_score": 0.7,
                "ai_generation_score": None,
                "overall_credibility_score": 0.75,
            },
            "fact_checks": [],
            "fallacies": [],
            "ai_check": None,
        })
        
        query = Query()
        result = query.analysis(analysis_id)
        
        assert result is not None
        assert result.id == analysis_id
        assert result.status == "ready"


class TestMutationResolver:
    """Test GraphQL Mutation resolvers."""

    def test_create_user(self):
        """Mutation.create_user() creates and stores a user."""
        input_data = CreateUserInput(
            account_id="acc456",
            name="Bob",
            email="bob@example.com",
            wallet_address="0x456",
        )
        
        mutation = Mutation()
        result = mutation.create_user(input_data)
        
        assert result.id is not None
        assert result.account_id == "acc456"
        assert result.name == "Bob"
        assert result.email == "bob@example.com"
        assert result.wallet_address == "0x456"
        assert result.created_at is not None
        
        # Verify it was saved
        retrieved = store.get_user(str(result.id))
        assert retrieved is not None
        assert retrieved["name"] == "Bob"

    def test_create_upload_minimal(self):
        """Mutation.create_upload() creates an upload with minimal input."""
        input_data = CreateUploadInput(
            files=[
                FileInput(
                    name="document.pdf",
                    content_type="application/pdf",
                    size=1024,
                )
            ]
        )
        
        mutation = Mutation()
        result = mutation.create_upload(input_data)
        
        assert result.id is not None
        assert result.status == "pending"
        # Verify it was saved
        retrieved = store.get_upload(str(result.id))
        assert retrieved is not None
        assert retrieved["status"] == "pending"

    def test_create_upload_with_settings(self):
        """Mutation.create_upload() stores settings correctly."""
        input_data = CreateUploadInput(
            files=[FileInput(name="test.txt")],
            settings=UploadSettingsInput(
                fact_check=True,
                logical_fallacy_check=True,
                ai_generation_check=False,
            )
        )
        
        mutation = Mutation()
        result = mutation.create_upload(input_data)
        
        # Verify it was saved with correct settings
        retrieved = store.get_upload(str(result.id))
        assert retrieved["settings"]["fact_check"] is True
        assert retrieved["settings"]["logical_fallacy_check"] is True
        assert retrieved["settings"]["ai_generation_check"] is False

    def test_create_upload_inherits_user_id(self):
        """Mutation.create_upload() inherits user_id to files if not specified."""
        user_id = "user::alice"
        input_data = CreateUploadInput(
            user_id=user_id,
            files=[FileInput(name="doc.txt")]  # no user_id in file
        )
        
        mutation = Mutation()
        result = mutation.create_upload(input_data)
        
        # Verify user_id was inherited in stored file
        retrieved = store.get_upload(str(result.id))
        assert retrieved["files"][0]["user_id"] == user_id

    @pytest.mark.asyncio
    async def test_start_analysis(self):
        """Mutation.start_analysis() creates analysis and links it."""
        # Setup: create an upload
        upload_id = "upload::test"
        store.save_upload(upload_id, {
            "id": upload_id,
            "user_id": "user::123",
            "created_at": "2026-02-13T10:00:00Z",
            "status": "pending",
            "files": [],
            "settings": {"fact_check": True, "logical_fallacy_check": False, "ai_generation_check": False},
            "analysis_id": None,
        })
        
        # Test
        mutation = Mutation()
        result = await mutation.start_analysis(upload_id)
        
        assert result.id is not None
        assert result.upload_id == upload_id
        assert result.status == "ready"
        
        # Verify upload was linked
        retrieved_upload = store.get_upload(upload_id)
        assert retrieved_upload["analysis_id"] == str(result.id)
        assert retrieved_upload["status"] == "ready"

    @pytest.mark.asyncio
    async def test_start_analysis_not_found(self):
        """Mutation.start_analysis() raises exception if upload not found."""
        mutation = Mutation()
        
        with pytest.raises(Exception, match="Upload not found"):
            await mutation.start_analysis("upload::nonexistent")

    def test_clear_upload(self):
        """Mutation.clear_upload() deletes upload and related analysis."""
        # Setup
        upload_id = "upload::test"
        analysis_id = "analysis::test"
        
        store.save_upload(upload_id, {
            "id": upload_id,
            "analysis_id": analysis_id,
        })
        store.save_analysis(analysis_id, {"id": analysis_id})
        
        # Test
        mutation = Mutation()
        result = mutation.clear_upload(upload_id)
        
        assert result is True
        assert store.get_upload(upload_id) is None
        assert store.get_analysis(analysis_id) is None

    def test_clear_upload_not_found(self):
        """Mutation.clear_upload() returns False if upload not found."""
        mutation = Mutation()
        result = mutation.clear_upload("upload::nonexistent")
        
        assert result is False

    def test_clear_upload_without_analysis(self):
        """Mutation.clear_upload() works even if no analysis linked."""
        upload_id = "upload::test"
        store.save_upload(upload_id, {
            "id": upload_id,
            "analysis_id": None,
        })
        
        mutation = Mutation()
        result = mutation.clear_upload(upload_id)
        
        assert result is True
        assert store.get_upload(upload_id) is None
