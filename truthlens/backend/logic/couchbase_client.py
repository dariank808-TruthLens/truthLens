"""Couchbase SDK client and connection management."""
import asyncio
from typing import Optional, Dict, Any, List
from datetime import timedelta

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.exceptions import CouchbaseException, DocumentNotFoundException
from couchbase.options import ClusterOptions, BucketOptions

from .couchbase_config import CouchbaseConfig


class CouchbaseClient:
    """Couchbase cluster and bucket management."""
    
    _instance: Optional["CouchbaseClient"] = None
    _cluster: Optional[Cluster] = None
    _bucket = None
    
    def __new__(cls):
        """Singleton pattern for Couchbase connection."""
        if cls._instance is None:
            cls._instance = super(CouchbaseClient, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def connect(cls) -> "CouchbaseClient":
        """Establish connection to Couchbase cluster.
        
        Returns:
            CouchbaseClient instance
            
        Raises:
            CouchbaseException: If connection fails
        """
        instance = cls()
        
        if cls._cluster is not None:
            return instance  # Already connected
        
        try:
            # Create authenticator
            auth = PasswordAuthenticator(
                CouchbaseConfig.USERNAME,
                CouchbaseConfig.PASSWORD
            )
            
            # Create cluster options
            options = ClusterOptions(auth)
            options.timeout = timedelta(milliseconds=CouchbaseConfig.CONNECTION_TIMEOUT_MS)
            
            # Connect to cluster
            cls._cluster = Cluster.connect(CouchbaseConfig.HOST, options)
            
            # Open bucket
            cls._bucket = cls._cluster.bucket(CouchbaseConfig.BUCKET_NAME)
            cls._bucket.on_connect()
            
            print(f"✓ Connected to Couchbase: {CouchbaseConfig.HOST}")
            print(f"✓ Using bucket: {CouchbaseConfig.BUCKET_NAME}")
            
        except CouchbaseException as e:
            print(f"✗ Couchbase connection failed: {e}")
            raise
        
        return instance
    
    @classmethod
    def disconnect(cls) -> None:
        """Close Couchbase connection."""
        if cls._cluster is not None:
            cls._cluster.close()
            cls._cluster = None
            cls._bucket = None
            print("✓ Disconnected from Couchbase")
    
    @classmethod
    def get_bucket(cls):
        """Get the connected bucket.
        
        Raises:
            RuntimeError: If not connected
        """
        if cls._bucket is None:
            raise RuntimeError("Not connected to Couchbase. Call connect() first.")
        return cls._bucket
    
    @classmethod
    def get_cluster(cls) -> Cluster:
        """Get the connected cluster.
        
        Raises:
            RuntimeError: If not connected
        """
        if cls._cluster is None:
            raise RuntimeError("Not connected to Couchbase. Call connect() first.")
        return cls._cluster
    
    @classmethod
    def is_connected(cls) -> bool:
        """Check if connected to Couchbase."""
        return cls._cluster is not None and cls._bucket is not None


class CouchbaseQuery:
    """Helper for N1QL queries."""
    
    @staticmethod
    def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID.
        
        Args:
            doc_id: Document ID (e.g., 'user::abc123')
            
        Returns:
            Document dict if found, None otherwise
        """
        try:
            bucket = CouchbaseClient.get_bucket()
            result = bucket.get(doc_id)
            return result.content_as[dict]
        except DocumentNotFoundException:
            return None
        except CouchbaseException as e:
            print(f"Error retrieving document {doc_id}: {e}")
            return None
    
    @staticmethod
    def save_document(doc_id: str, document: Dict[str, Any]) -> bool:
        """Save document by ID (insert or update).
        
        Args:
            doc_id: Document ID
            document: Document dict
            
        Returns:
            True if successful, False otherwise
        """
        try:
            bucket = CouchbaseClient.get_bucket()
            bucket.upsert(doc_id, document)
            return True
        except CouchbaseException as e:
            print(f"Error saving document {doc_id}: {e}")
            return False
    
    @staticmethod
    def delete_document(doc_id: str) -> bool:
        """Delete document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            bucket = CouchbaseClient.get_bucket()
            bucket.remove(doc_id)
            return True
        except DocumentNotFoundException:
            return False
        except CouchbaseException as e:
            print(f"Error deleting document {doc_id}: {e}")
            return False
    
    @staticmethod
    def query(sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Execute N1QL query.
        
        Args:
            sql: N1QL query string
            params: Optional query parameters
            
        Returns:
            List of result rows (dicts)
        """
        try:
            cluster = CouchbaseClient.get_cluster()
            result = cluster.query(sql, positional_parameters=params or [])
            return [row for row in result.rows()]
        except CouchbaseException as e:
            print(f"Query error: {e}\nSQL: {sql}")
            return []
    
    @staticmethod
    def query_by_type(doc_type: str) -> List[Dict[str, Any]]:
        """Query documents by type.
        
        Args:
            doc_type: Document type (prefix, e.g., 'user', 'upload', 'analysis')
            
        Returns:
            List of matching documents
        """
        sql = f"""
        SELECT * FROM {CouchbaseConfig.BUCKET_NAME}
        WHERE META().id LIKE '{doc_type}::%'
        """
        return CouchbaseQuery.query(sql)
