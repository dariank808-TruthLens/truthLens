"""Couchbase migration and initialization script."""
from typing import List
from .couchbase_client import CouchbaseClient, CouchbaseQuery
from .couchbase_config import CouchbaseConfig


def create_indexes() -> bool:
    """Create N1QL indexes for common queries.
    
    Returns:
        True if all indexes created successfully, False otherwise
    """
    indexes = [
        # Index on document type (prefix)
        f"""
        CREATE INDEX IF NOT EXISTS idx_doc_type 
        ON {CouchbaseConfig.BUCKET_NAME}(META().id)
        """,
        
        # Index on user uploads
        f"""
        CREATE INDEX IF NOT EXISTS idx_upload_user 
        ON {CouchbaseConfig.BUCKET_NAME}(user_id)
        WHERE META().id LIKE 'upload::%'
        """,
        
        # Index on analysis by upload
        f"""
        CREATE INDEX IF NOT EXISTS idx_analysis_upload 
        ON {CouchbaseConfig.BUCKET_NAME}(upload_id)
        WHERE META().id LIKE 'analysis::%'
        """,
        
        # Index on analysis status
        f"""
        CREATE INDEX IF NOT EXISTS idx_analysis_status 
        ON {CouchbaseConfig.BUCKET_NAME}(status)
        WHERE META().id LIKE 'analysis::%'
        """,
    ]
    
    cluster = CouchbaseClient.get_cluster()
    
    for idx_sql in indexes:
        try:
            cluster.query(idx_sql)
            print(f"✓ Index created: {idx_sql.split()[-3]}")
        except Exception as e:
            print(f"✗ Index creation failed: {e}")
            return False
    
    return True


def setup_couchbase() -> bool:
    """Complete Couchbase setup: connect and create indexes.
    
    Returns:
        True if setup successful, False otherwise
    """
    print("\n=== Couchbase Setup ===")
    print(f"Configuration: {CouchbaseConfig.to_dict()}")
    
    if not CouchbaseConfig.USE_COUCHBASE:
        print("ℹ Couchbase disabled (USE_COUCHBASE=false)")
        return True
    
    try:
        # Connect to Couchbase
        CouchbaseClient.connect()
        
        # Create indexes
        if not create_indexes():
            print("✗ Index creation failed")
            return False
        
        print("\n✓ Couchbase setup complete!")
        return True
        
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        return False


def teardown_couchbase() -> None:
    """Cleanup Couchbase connection."""
    print("\n=== Couchbase Teardown ===")
    CouchbaseClient.disconnect()


if __name__ == "__main__":
    # CLI usage: python -m backend.logic.couchbase_migration
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        success = setup_couchbase()
        sys.exit(0 if success else 1)
    elif len(sys.argv) > 1 and sys.argv[1] == "teardown":
        teardown_couchbase()
        sys.exit(0)
    else:
        print("Usage:")
        print("  python -m backend.logic.couchbase_migration setup")
        print("  python -m backend.logic.couchbase_migration teardown")
