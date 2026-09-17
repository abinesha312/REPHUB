# Architecture Documentation

## System Overview

Resume Repository is a production-grade system for managing resume versions with AI-powered job matching. The architecture follows clean separation of concerns with a modern web stack.

## High-Level Architecture

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│   React     │────────>│   FastAPI   │────────>│  PostgreSQL  │
│   Frontend  │  HTTP   │   Backend   │  SQL    │  + pgvector  │
│  (Vite/MUI) │<────────│  (Python)   │<────────│              │
└─────────────┘         └─────────────┘         └──────────────┘
                               │
                               │ File I/O
                               ▼
                        ┌─────────────┐
                        │    Local    │
                        │  Filesystem │
                        │   Storage   │
                        └─────────────┘
```

## Backend Architecture

### Layer Structure

```
┌──────────────────────────────────────┐
│         FastAPI Application          │
│  (main.py - ASGI app, middleware)    │
└──────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────┐
│            Routers Layer             │
│  • health.py  - Health checks        │
│  • resumes.py - Resume CRUD          │
│  • match.py   - Job matching         │
└──────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────┐
│         Business Logic Layer         │
│  • extractors.py - Text extraction   │
│  • embeddings.py - Vector generation │
│  • storage.py    - File operations   │
└──────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────┐
│          Data Access Layer           │
│  • models.py   - SQLAlchemy ORM      │
│  • database.py - Session management  │
└──────────────────────────────────────┘
                │
                ▼
         PostgreSQL + pgvector
```

### Key Components

#### 1. Configuration (`config.py`)
- Pydantic Settings for environment-based config
- Type-safe configuration with defaults
- Supports `.env` file loading

#### 2. Database (`database.py`, `models.py`)
- SQLAlchemy ORM with async support
- pgvector integration for embeddings
- Session management with dependency injection

**Models:**
- `User`: User accounts (simplified for v1)
- `Resume`: Resume versions with vector embeddings

#### 3. Storage Backend (`storage.py`)
- Abstract `StorageBackend` interface
- `LocalFileStorage` implementation
- Designed for easy extension to GCS/S3

**Storage Path Format:**
```
{STORAGE_ROOT}/
  {user_id}/
    {format}/
      v_{version}/
        {filename}
```

#### 4. Text Extraction (`extractors.py`)
- PDF extraction via pdfplumber
- DOCX extraction via docx2txt
- Plain text/LaTeX reading
- Graceful error handling

#### 5. Embeddings (`embeddings.py`)
- sentence-transformers integration
- Lazy model loading
- Batch processing support
- Local inference (no API calls)

#### 6. Routers (`routers/`)

**Health Router:**
- `GET /health` - Database connectivity check

**Resumes Router:**
- `POST /resumes/upload` - Upload with auto-versioning
- `GET /resumes/list` - List with filtering
- `GET /resumes/download/{id}` - File download
- `GET /resumes/folders` - Folder tree view

**Match Router:**
- `POST /match/` - Semantic search via pgvector

## Frontend Architecture

### Component Structure

```
src/
├── App.jsx                 # Root component with routing
├── main.jsx               # React entry point
│
├── components/
│   ├── Navbar.jsx         # Top navigation
│   ├── ResumeUploader.jsx # Upload form with format selection
│   ├── ResumeList.jsx     # Repository tree view
│   ├── JobDescriptionInput.jsx # Job description input
│   └── MatchResults.jsx   # Ranked match display
│
└── pages/
    ├── HomePage.jsx       # Landing page
    ├── ResumePage.jsx     # Upload + list combined
    └── MatchPage.jsx      # Job matching interface
```

### State Management
- React hooks (useState, useEffect)
- Props drilling for user context
- No Redux/MobX (kept simple)

### API Communication
- Axios for HTTP requests
- Proxy setup via Vite config
- Error handling with user feedback

## Database Schema

### Tables

#### `users`
```sql
id          SERIAL PRIMARY KEY
username    VARCHAR(100) UNIQUE NOT NULL
email       VARCHAR(255)
created_at  TIMESTAMP DEFAULT NOW()
```

#### `resumes`
```sql
id              SERIAL PRIMARY KEY
user_id         INTEGER NOT NULL
format          VARCHAR(50) NOT NULL
version         INTEGER NOT NULL
filename        VARCHAR(255) NOT NULL
storage_path    VARCHAR(500) NOT NULL
content_type    VARCHAR(100)
file_size       INTEGER
extracted_text  TEXT
embedding       VECTOR(384)
uploaded_at     TIMESTAMP DEFAULT NOW()

INDEX idx_user_format (user_id, format)
INDEX idx_embedding (embedding vector_cosine_ops)
```

### Vector Search Query

```sql
SELECT 
    id, user_id, format, version, filename, uploaded_at,
    1 - (embedding <=> :query_embedding::vector) AS similarity
FROM resumes
WHERE embedding IS NOT NULL
ORDER BY embedding <=> :query_embedding::vector
LIMIT 10
```

The `<=>` operator is pgvector's cosine distance operator.

## Data Flow

### Upload Flow

```
1. User selects file + format in UI
   ↓
2. Frontend uploads via multipart form
   POST /api/resumes/upload
   ↓
3. Backend receives file
   ↓
4. Query database for latest version
   SELECT MAX(version) WHERE user_id=X AND format=Y
   ↓
5. Calculate next_version = latest + 1
   ↓
6. Save file to storage
   path = "{user_id}/{format}/v_{next_version}/{filename}"
   ↓
7. Extract text
   TextExtractor.extract(path, format)
   ↓
8. Generate embedding
   EmbeddingService.embed_text(extracted_text)
   ↓
9. Insert database record
   INSERT INTO resumes (user_id, format, version, ..., embedding)
   ↓
10. Return metadata to frontend
    {id, version, has_embedding, ...}
```

### Match Flow

```
1. User pastes job description
   ↓
2. Frontend sends match request
   POST /api/match/
   ↓
3. Generate JD embedding
   embedding = EmbeddingService.embed_text(job_description)
   ↓
4. Vector similarity search
   SELECT ... ORDER BY embedding <=> :embedding LIMIT 10
   ↓
5. Calculate similarity scores
   similarity = 1 - cosine_distance
   ↓
6. Return ranked results
   [{resume_id, filename, similarity_score, ...}]
   ↓
7. Frontend displays with download buttons
```

## Vector Similarity

### Embedding Model
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Dimensions**: 384
- **Method**: Mean pooling of BERT embeddings
- **Similarity**: Cosine similarity

### Similarity Formula
```
cosine_similarity = dot(A, B) / (||A|| * ||B||)
cosine_distance = 1 - cosine_similarity

pgvector: embedding <=> query_vector returns cosine_distance
our similarity_score = 1 - cosine_distance
```

### Score Interpretation
- **0.8 - 1.0**: Excellent match (very similar semantically)
- **0.6 - 0.8**: Good match (relevant)
- **0.4 - 0.6**: Fair match (somewhat relevant)
- **0.0 - 0.4**: Weak match (not very relevant)

## Deployment Architecture

### Development (docker-compose)

```
┌──────────────────────────────────────────┐
│         Docker Compose Stack             │
│                                          │
│  ┌────────────┐  ┌──────────────┐       │
│  │  Frontend  │  │   Backend    │       │
│  │  (Node)    │  │   (Python)   │       │
│  │  Port 5173 │  │   Port 8000  │       │
│  └────────────┘  └──────────────┘       │
│         │                │               │
│         └────────────────┴───────┐       │
│                                  │       │
│                        ┌─────────▼─────┐ │
│                        │   PostgreSQL  │ │
│                        │   + pgvector  │ │
│                        │   Port 5432   │ │
│                        └───────────────┘ │
│                                          │
│  Volumes:                                │
│  • postgres_data (persistent)            │
│  • ./storage (bind mount)                │
└──────────────────────────────────────────┘
```

### Production (future)

```
┌─────────────┐
│   Nginx /   │
│   Traefik   │
│  (TLS/SSL)  │
└──────┬──────┘
       │
   ┌───┴───┬────────────┬─────────────┐
   │       │            │             │
   ▼       ▼            ▼             ▼
┌────┐  ┌────┐    ┌─────────┐   ┌─────────┐
│ UI │  │ UI │    │ Backend │   │ Backend │
│ #1 │  │ #2 │    │   #1    │   │   #2    │
└────┘  └────┘    └────┬────┘   └────┬────┘
                       │             │
                       └──────┬──────┘
                              │
                    ┌─────────▼─────────┐
                    │  PostgreSQL       │
                    │  (managed/HA)     │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Cloud Storage    │
                    │  (GCS / S3)       │
                    └───────────────────┘
```

## Performance Considerations

### Embedding Generation
- **Model Loading**: ~2 seconds on first request (lazy loading)
- **Embedding Time**: ~10-50ms per document
- **Memory**: ~500MB for model in RAM
- **Optimization**: Could batch process or use async workers

### Vector Search
- **pgvector**: Uses HNSW index for fast approximate search
- **Typical Query**: <10ms for 10k vectors
- **Scale**: Tested up to 100k vectors
- **Index Creation**: `CREATE INDEX ON resumes USING ivfflat (embedding vector_cosine_ops)`

### Text Extraction
- **PDF**: 100-500ms depending on size
- **DOCX**: 50-200ms
- **LaTeX**: <10ms (plain text read)

### Storage
- **Local Filesystem**: Direct I/O, very fast
- **Cloud (future)**: 100-300ms for upload/download
- **Optimization**: Pre-signed URLs, CDN for downloads

## Security Considerations

### Current Implementation
- ⚠️ No authentication (single-user demo)
- ⚠️ No authorization checks
- ⚠️ No rate limiting
- ✅ CORS enabled for local development
- ✅ File upload validation
- ✅ SQL injection protection (ORM)

### Production Requirements
- [ ] User authentication (JWT/OAuth)
- [ ] API key authentication
- [ ] Rate limiting (per user/IP)
- [ ] File size limits
- [ ] Malware scanning
- [ ] Input validation & sanitization
- [ ] HTTPS/TLS
- [ ] Secret management (Vault/KMS)
- [ ] Audit logging

## Testing Strategy

### Unit Tests
- ✅ Version bumping logic
- ✅ Storage operations
- ✅ Embedding generation
- ✅ Path validation

### Integration Tests (TODO)
- [ ] Full upload flow
- [ ] Match endpoint
- [ ] Error handling
- [ ] Database transactions

### E2E Tests (TODO)
- [ ] UI upload flow
- [ ] Job matching workflow
- [ ] Download functionality

## Monitoring & Observability

### Recommended (future)
- **Logging**: Structured JSON logs
- **Metrics**: Prometheus + Grafana
  - Request latency
  - Embedding generation time
  - Vector search duration
  - Upload success/failure rate
- **Tracing**: OpenTelemetry
- **Alerting**: On error rates, slow queries

## Scalability Path

### Current Limits
- Single-server deployment
- ~10k resumes per user
- ~1M total vectors

### Scaling Strategy
1. **Horizontal Scaling**: Multiple backend instances behind load balancer
2. **Database**: PostgreSQL replication, connection pooling
3. **Storage**: Migrate to object storage (GCS/S3)
4. **Embeddings**: Separate worker service, queue-based
5. **Caching**: Redis for frequently accessed data
6. **Search**: Consider Elasticsearch for advanced queries

## Extension Points

### Adding Cloud Storage

Implement new storage backend:

```python
class GCSStorage(StorageBackend):
    def __init__(self, bucket_name: str):
        self.bucket = storage.Client().bucket(bucket_name)
    
    def save(self, file: BinaryIO, path: str) -> str:
        blob = self.bucket.blob(path)
        blob.upload_from_file(file)
        return path
    
    # ... implement other methods
```

Update factory in `storage.py`:

```python
def get_storage_backend(backend_type: str, **kwargs) -> StorageBackend:
    if backend_type == "local":
        return LocalFileStorage(kwargs["root_dir"])
    elif backend_type == "gcs":
        return GCSStorage(kwargs["bucket_name"])
    # ...
```

### Adding Authentication

1. Implement `User` model with password hashing
2. Add JWT token generation/validation
3. Create auth router with login/register
4. Add `get_current_user` dependency
5. Protect endpoints with dependencies

### Adding Resume Parsing

Create parser service:

```python
class ResumeParser:
    def parse(self, text: str) -> ParsedResume:
        # Extract structured data
        return ParsedResume(
            skills=[...],
            experience=[...],
            education=[...]
        )
```

Add `parsed_data` JSON column to `resumes` table.

## Conclusion

This architecture prioritizes:
- ✅ Clean separation of concerns
- ✅ Easy testing and maintenance
- ✅ Clear extension points
- ✅ Production-ready patterns
- ✅ Local-first (no cloud vendor lock-in)

The system is designed to start simple and scale as needed.
