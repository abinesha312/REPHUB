# Resume Repository

A production-grade resume versioning and job-matching system. Think "GitHub for resumes" – with automatic versioning, organized storage, and AI-powered semantic matching using pgvector.

## Features

### 🗂️ Resume Version Control
- **Automatic versioning**: Upload resumes and get automatic version numbers (`v_1`, `v_2`, `v_3`...)
- **Format organization**: Separate version histories for PDF, LaTeX, DOC, and DOCX formats
- **Local storage**: Files stored in a clear filesystem layout: `{user_id}/{format}/v_{N}/filename`
- **Metadata tracking**: Full metadata in PostgreSQL including upload time, file size, extracted text

### 🔍 AI-Powered Job Matching
- **Semantic search**: Paste a job description and find the best matching resume
- **pgvector integration**: Fast vector similarity search using cosine distance
- **Ranked results**: Get similarity scores and download the best matches
- **Local embeddings**: Uses sentence-transformers (no paid API required)

### 🏗️ Production Architecture
- **FastAPI backend**: Clean REST API with health checks, upload, download, list, and match endpoints
- **React + Material-UI frontend**: Modern, responsive UI with Vite
- **PostgreSQL + pgvector**: Production database with vector extension
- **Docker Compose**: Complete stack with one command
- **Storage abstraction**: Clean interface ready for GCS/S3 integration later

## Quick Start

### Prerequisites
- Docker & Docker Compose
- 4GB+ RAM (for embedding model)
- ~2GB disk space

### 1. Clone and Configure

```bash
git clone https://github.com/abinesha312/REPHUB.git
cd REPHUB

# Copy environment template
cp .env.example .env

# Edit .env if needed (defaults work for local development)
```

### 2. Start the Stack

```bash
docker-compose up --build
```

This will:
- Start PostgreSQL with pgvector extension
- Build and start the FastAPI backend (port 8000)
- Build and start the React frontend (port 5173)
- Download the embedding model on first run (~80MB)

### 3. Access the Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Usage

### Upload Flow
1. Go to **Resumes** page
2. Select format (PDF, LaTeX, DOC, DOCX)
3. Choose file
4. Click **Upload Resume**
5. System automatically:
   - Determines next version number
   - Stores file in `storage/{user_id}/{format}/v_{N}/`
   - Extracts text content
   - Generates embedding vector
   - Saves metadata to database

### Match Flow
1. Go to **Match** page
2. Paste job description
3. Click **Find Best Matches**
4. View ranked results with similarity scores
5. Download the best matching resume

### Repository Structure
Files are organized as:
```
storage/
├── 1/                    # User ID
│   ├── pdf/
│   │   ├── v_1/
│   │   │   └── resume.pdf
│   │   ├── v_2/
│   │   │   └── resume_updated.pdf
│   │   └── v_3/
│   │       └── resume_final.pdf
│   ├── latex/
│   │   ├── v_1/
│   │   │   └── resume.tex
│   │   └── v_2/
│   │       └── resume.tex
│   └── docx/
│       └── v_1/
│           └── resume.docx
```

## API Endpoints

### Health
- `GET /api/health` - Service health check

### Resumes
- `POST /api/resumes/upload` - Upload new resume version
  - Form data: `file`, `user_id`, `format`
  - Returns: Resume metadata with version number
- `GET /api/resumes/list?user_id={id}&format={fmt}` - List resumes
- `GET /api/resumes/download/{resume_id}` - Download resume file
- `GET /api/resumes/folders?user_id={id}` - Get folder tree structure

### Matching
- `POST /api/match/` - Find matching resumes
  - Body: `{"job_description": "...", "user_id": 1, "limit": 10}`
  - Returns: Ranked list with similarity scores

## Development

### Local Development (without Docker)

#### Backend
```bash
cd backend

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up database (requires PostgreSQL with pgvector)
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/resumerepo"
export STORAGE_ROOT="./storage"

# Run tests
pytest

# Start server
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### Running Tests

```bash
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html
```

### Test Coverage
- ✅ Version bumping logic
- ✅ Storage path validation
- ✅ File save/load/delete operations
- ✅ Embedding generation
- ✅ Similarity scoring

## Architecture

### Backend Stack
- **FastAPI**: Modern, async Python web framework
- **SQLAlchemy**: ORM with PostgreSQL support
- **pgvector**: PostgreSQL extension for vector similarity search
- **sentence-transformers**: Local embedding generation (all-MiniLM-L6-v2)
- **pdfplumber**: PDF text extraction
- **docx2txt**: DOCX text extraction

### Frontend Stack
- **React 19**: UI library
- **Material-UI (MUI)**: Component library
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **Vite**: Build tool and dev server

### Database Schema

#### `users` table
- `id`: Primary key
- `username`: Unique username
- `email`: Email (optional)
- `created_at`: Timestamp

#### `resumes` table
- `id`: Primary key
- `user_id`: Foreign key to users
- `format`: Format type (pdf, latex, doc, docx)
- `version`: Version number (1, 2, 3...)
- `filename`: Original filename
- `storage_path`: Path in storage backend
- `content_type`: MIME type
- `file_size`: Size in bytes
- `extracted_text`: Full text content
- `embedding`: Vector(384) - pgvector column
- `uploaded_at`: Timestamp

### Storage Backend Interface

The storage layer uses an abstract interface (`StorageBackend`) with a local filesystem implementation (`LocalFileStorage`). This design allows easy migration to cloud storage:

```python
class StorageBackend(ABC):
    @abstractmethod
    def save(self, file: BinaryIO, path: str) -> str: ...
    
    @abstractmethod
    def load(self, path: str) -> bytes: ...
    
    @abstractmethod
    def delete(self, path: str) -> None: ...
    
    @abstractmethod
    def exists(self, path: str) -> bool: ...
```

To add GCS/S3 support later, implement a new class (e.g., `GCSStorage`) with the same interface.

## Configuration

### Environment Variables

See `.env.example` for all options:

- `DATABASE_URL`: PostgreSQL connection string
- `STORAGE_ROOT`: Base directory for file storage
- `EMBEDDING_MODEL`: Sentence-transformers model name
  - Default: `sentence-transformers/all-MiniLM-L6-v2` (384 dim, ~80MB)
  - Alternative: `sentence-transformers/all-mpnet-base-v2` (768 dim, better quality, ~420MB)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)

### Embedding Models

The system uses local sentence-transformers models:

| Model | Dimensions | Size | Quality |
|-------|-----------|------|---------|
| all-MiniLM-L6-v2 | 384 | ~80MB | Good |
| all-mpnet-base-v2 | 768 | ~420MB | Better |
| all-MiniLM-L12-v2 | 384 | ~120MB | Good+ |

No API keys or external services required.

## Limitations & Future Work

### Current Limitations
- **Single-user mode**: Authentication not implemented (uses default user_id=1)
- **Local storage only**: No cloud storage integration yet
- **Basic text extraction**: DOCX/DOC support is best-effort
- **No resume parsing**: Doesn't extract structured data (skills, experience, etc.)
- **No image processing**: Text must be selectable/extractable

### Future Enhancements
- [ ] Multi-user authentication (OAuth, JWT)
- [ ] GCS/S3 storage backend
- [ ] Resume parsing (extract skills, experience, education)
- [ ] OCR for scanned PDFs
- [ ] Compare resume versions (diff view)
- [ ] Export statistics and analytics
- [ ] Batch upload
- [ ] API key authentication
- [ ] Rate limiting
- [ ] Caching layer (Redis)

## Security Notes

⚠️ **Important**: The original repository contained `backend/kaggle.json` which has been removed from git tracking. If you cloned the old version:

1. The kaggle.json file is now gitignored
2. **Rotate any credentials** that were in that file
3. Never commit API keys, tokens, or credentials

Always use environment variables for secrets and never commit:
- API keys
- Database passwords
- Service account credentials
- Private keys

## Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml:
# - "8001:8000"  # Backend
# - "5174:5173"  # Frontend
```

### Embedding Model Download Fails
```bash
# Pre-download the model:
docker-compose run backend python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Database Connection Issues
```bash
# Check PostgreSQL is running:
docker-compose ps postgres

# View logs:
docker-compose logs postgres

# Ensure pgvector extension is installed:
docker-compose exec postgres psql -U postgres -d resumerepo -c "CREATE EXTENSION IF NOT EXISTS vector"
```

### Text Extraction Fails
- **PDF**: Requires selectable text (not scanned images)
- **DOCX**: Basic support only, complex formatting may not extract well
- **LaTeX**: Extracts raw .tex source code

## Contributing

Contributions welcome! Areas for improvement:
- Cloud storage backends (GCS, S3, Azure)
- Resume parsing and structured extraction
- OCR support for scanned documents
- Multi-user authentication
- Performance optimizations
- Better test coverage

## License

MIT License - see LICENSE file for details

## Original Repository

This is a complete refactor of [abinesha312/REPHUB](https://github.com/abinesha312/REPHUB), rebuilt from a Kaggle training pipeline into a production-ready application.

## Acknowledgments

- [sentence-transformers](https://www.sbert.net/) for local embeddings
- [pgvector](https://github.com/pgvector/pgvector) for PostgreSQL vector search
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent framework
- [Material-UI](https://mui.com/) for React components
