# Couchbase Setup Guide for TruthLens

## Prerequisites

1. **Couchbase Server** installed and running
   - Download: https://www.couchbase.com/downloads/server
   - Default: http://localhost:8091
   
2. **Python dependencies** installed:
   ```bash
   pip install -r backend/requirements.txt
   ```

## Quick Start

### Option 1: In-Memory Mode (Development/Testing)

By default, TruthLens uses in-memory storage for quick development:

```bash
# Keep USE_COUCHBASE=false in .env (or don't set it)
python -m backend.app.main
```

### Option 2: With Couchbase

#### Step 1: Start Couchbase Server

**On Windows:**
```powershell
# Couchbase service runs automatically after installation
# Or manually start: Services > Couchbase Server
```

**On Mac/Linux:**
```bash
# Docker (recommended)
docker run -d --name couchbase -p 8091-8094:8091-8094 -p 11210:11210 \
  -e CLUSTER_NAME=truthlens \
  -e CLUSTER_USERNAME=Administrator \
  -e CLUSTER_PASSWORD=password \
  couchbase/server:latest
```

#### Step 2: Configure Database

1. **Open Couchbase Web Console:** http://localhost:8091
2. **Login** with credentials (default: Administrator / password)
3. **Create Bucket:**
   - Click "Buckets" → "Add Bucket"
   - Name: `truthlens`
   - RAM Quota: 256 MB
   - Click "Add Bucket"
4. **Wait for bucket to be ready** (status shows "healthy")

#### Step 3: Configure Environment

Create `.env` file in project root:

```env
USE_COUCHBASE=true
COUCHBASE_HOST=couchbase://localhost
COUCHBASE_BUCKET=truthlens
COUCHBASE_USER=Administrator
COUCHBASE_PASSWORD=password
COUCHBASE_SCOPE=_default
COUCHBASE_TIMEOUT=5000
```

#### Step 4: Initialize Indexes (Optional but Recommended)

Couchbase creates indexes automatically on first run, but you can create them manually:

```bash
cd c:\Users\daria\truthLens\truthlens
python -m backend.logic.couchbase_migration setup
```

Expected output:
```
=== Couchbase Setup ===
Configuration: {'host': 'couchbase://localhost', 'bucket': 'truthlens', ...}
✓ Connected to Couchbase: couchbase://localhost
✓ Index created: idx_doc_type
✓ Index created: idx_upload_user
✓ Index created: idx_analysis_upload
✓ Index created: idx_analysis_status

✓ Couchbase setup complete!
```

#### Step 5: Start Backend with Couchbase

```bash
python -m uvicorn backend.app.main:app --reload
```

You should see:
```
=== Application Startup ===
Connecting to Couchbase...
✓ Couchbase connected
```

## Troubleshooting

### Connection Refused
```
Error: Connection refused at localhost:11210
```
**Solution:** Make sure Couchbase Server is running and the bucket exists.

### Authentication Failed
```
Error: Cannot authenticate with bucket 'truthlens'
```
**Solution:** Verify credentials in `.env` match Couchbase users (default: Administrator/password).

### Bucket Not Found
```
Error: Bucket 'truthlens' not found
```
**Solution:** Create the bucket via Couchbase Web Console (see Step 2).

### Disable Couchbase and Use In-Memory
```bash
# Set in .env or environment:
USE_COUCHBASE=false

# Or use environment variable:
export USE_COUCHBASE=false
python -m uvicorn backend.app.main:app --reload
```

## Database Schema

### Document Types

All documents use prefixed IDs for easy filtering:

**Users:** `user::{uuid}`
```json
{
  "id": "user::12345",
  "account_id": "acc123",
  "name": "Alice",
  "email": "alice@example.com",
  "wallet_address": "0x123...",
  "created_at": "2026-02-13T10:00:00Z"
}
```

**Uploads:** `upload::{uuid}`
```json
{
  "id": "upload::abc123",
  "user_id": "user::12345",
  "status": "pending|ready|error",
  "files": [...],
  "settings": {...},
  "created_at": "2026-02-13T10:00:00Z"
}
```

**Analyses:** `analysis::{uuid}`
```json
{
  "id": "analysis::xyz789",
  "upload_id": "upload::abc123",
  "status": "pending|ready|error",
  "breakdown": {
    "fact_check_score": 0.8,
    "logical_fallacy_score": 0.7,
    "ai_generation_score": 0.1,
    "overall_credibility_score": 0.75
  },
  "fact_checks": [...],
  "fallacies": [...],
  "ai_check": {...}
}
```

### Indexes

The following N1QL indexes are created for performance:

- `idx_doc_type` – Filter by document prefix (user, upload, analysis)
- `idx_upload_user` – Query uploads by user_id
- `idx_analysis_upload` – Query analyses by upload_id
- `idx_analysis_status` – Filter analyses by status

## Testing

Tests use in-memory storage by default (no Couchbase required):

```bash
python -m pytest backend/tests -v
```

To test with Couchbase:
1. Start Couchbase Server
2. Set `USE_COUCHBASE=true` in `.env`
3. Run tests:
   ```bash
   python -m pytest backend/tests -v
   ```

## Performance Tips

1. **Increase RAM quota** if handling large documents
2. **Create additional indexes** for custom queries
3. **Use projection** in queries to reduce network traffic
4. **Enable compression** for network connections (done by default)

## Next Steps

- [Wire Frontend to GraphQL API](../frontend/README.md)
- [Implement Real Analysis Backends](../backend/ANALYSIS.md)
- [Deploy to Production](../DEPLOYMENT.md)
