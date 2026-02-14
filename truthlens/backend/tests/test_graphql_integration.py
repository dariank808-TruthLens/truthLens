"""Integration tests for GraphQL API through HTTP."""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.logic import store


@pytest.fixture(autouse=True)
def clear_stores():
    """Clear stores before and after each test."""
    for s in [store._users, store._uploads, store._analyses]:
        s.clear()
    yield
    for s in [store._users, store._uploads, store._analyses]:
        s.clear()


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestGraphQLEndpoint:
    """Test GraphQL endpoint availability and basic queries."""

    def test_graphql_endpoint_available(self, client):
        """GraphQL endpoint is available at /graphql."""
        # GraphQL POST requests
        response = client.post(
            "/graphql",
            json={"query": "{ __typename }"}
        )
        assert response.status_code == 200

    def test_health_endpoint(self, client):
        """Root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        assert "GraphQL" in response.json()["message"]


class TestGraphQLMutations:
    """Test GraphQL mutations through HTTP."""

    def test_create_user_mutation(self, client):
        """createUser mutation creates and returns user."""
        query = """
        mutation {
            createUser(input: {
                accountId: "acc123",
                name: "Alice",
                email: "alice@example.com",
                walletAddress: "0x123abc"
            }) {
                id
                accountId
                name
                email
                walletAddress
                createdAt
            }
        }
        """
        
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert data["data"]["createUser"]["name"] == "Alice"
        assert data["data"]["createUser"]["email"] == "alice@example.com"
        assert data["data"]["createUser"]["id"] is not None

    def test_create_upload_mutation(self, client):
        """createUpload mutation creates and returns upload."""
        query = """
        mutation {
            createUpload(input: {
                files: [
                    {
                        name: "document.pdf",
                        contentType: "application/pdf",
                        size: 2048
                    }
                ]
            }) {
                id
                status
                createdAt
            }
        }
        """
        
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert data["data"]["createUpload"]["status"] == "pending"
        assert data["data"]["createUpload"]["id"] is not None


class TestGraphQLQueries:
    """Test GraphQL queries through HTTP."""

    def test_query_user(self, client):
        """user query retrieves stored user."""
        # First create a user
        create_query = """
        mutation {
            createUser(input: {accountId: "acc1", name: "User"}) {
                id
            }
        }
        """
        create_response = client.post("/graphql", json={"query": create_query})
        user_id = create_response.json()["data"]["createUser"]["id"]
        
        # Now query for it
        query = f"""
        query {{
            user(id: "{user_id}") {{
                id
                name
                createdAt
            }}
        }}
        """
        
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["user"]["id"] == user_id
        assert data["data"]["user"]["name"] == "User"

    def test_query_nonexistent_user(self, client):
        """user query returns null for nonexistent user."""
        query = """
        query {
            user(id: "user::nonexistent") {
                id
                name
            }
        }
        """
        
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["user"] is None
