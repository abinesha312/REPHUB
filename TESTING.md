# Testing Guide

## Pre-deployment Checklist

Before merging this PR, please test the following:

### 1. Docker Compose Startup

```bash
# Clean start
docker-compose down -v
docker-compose up --build

# Or with newer Docker syntax
docker compose down -v
docker compose up --build
```

**Expected:**
- PostgreSQL starts with pgvector extension
- Backend starts on port 8000
- Frontend starts on port 5173
- No error logs in any container

### 2. Health Check

```bash
curl http://localhost:8000/api/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

### 3. Frontend Access

Open browser to http://localhost:5173

**Expected:**
- Homepage loads with navigation
- "Resume Repository" title visible
- Three feature cards displayed
- Navigation to Resumes and Match pages works

### 4. Backend API Documentation

Open http://localhost:8000/docs

**Expected:**
- Swagger UI loads
- All endpoints visible:
  - GET /api/health
  - POST /api/resumes/upload
  - GET /api/resumes/list
  - GET /api/resumes/download/{resume_id}
  - GET /api/resumes/folders
  - POST /api/match/

### 5. Upload Flow Test

Using the UI or API:

#### Via UI:
1. Go to "Resumes" page
2. Select format: PDF
3. Choose a PDF file
4. Click "Upload Resume"
5. Verify:
   - Success message appears
   - Version v_1 is shown in the list
   - File appears in repository tree
   - "✓ Embedded" indicator shown

#### Via API:
```bash
curl -X POST http://localhost:8000/api/resumes/upload \
  -F "file=@test_resume.pdf" \
  -F "user_id=1" \
  -F "format=pdf"
```

**Expected response:**
```json
{
  "id": 1,
  "user_id": 1,
  "format": "pdf",
  "version": 1,
  "filename": "test_resume.pdf",
  "storage_path": "1/pdf/v_1/test_resume.pdf",
  "content_type": "application/pdf",
  "file_size": 12345,
  "uploaded_at": "2026-09-17T04:10:00",
  "has_embedding": true
}
```

### 6. Version Increment Test

Upload the same format again:

1. Select PDF format
2. Choose another PDF file
3. Upload
4. Verify version is now v_2

**Check storage structure:**
```bash
docker-compose exec backend ls -la /app/storage/1/pdf/
```

**Expected:**
```
drwxr-xr-x v_1/
drwxr-xr-x v_2/
```

### 7. Multiple Format Test

Upload different formats:

1. Upload a PDF → should be v_1 for PDF
2. Upload a LaTeX file → should be v_1 for LaTeX (independent versioning)
3. Upload another PDF → should be v_2 for PDF
4. Upload another LaTeX → should be v_2 for LaTeX

**Verify in UI:**
- PDF section shows v_1 and v_2
- LaTeX section shows v_1 and v_2
- Both sections are separate

### 8. Download Test

1. Click download button on any resume in the list
2. Verify file downloads with correct filename
3. Open downloaded file and verify it's the correct content

### 9. Job Match Test

#### Create test data first:
Upload 2-3 resumes with different content (e.g., one software engineer resume, one data scientist resume)

#### Test matching:
1. Go to Match page
2. Paste a job description (e.g., "Looking for a Senior Python Developer with React experience...")
3. Click "Find Best Matches"
4. Verify:
   - Results appear ranked by similarity
   - Similarity scores are between 0-1
   - Higher scores for more relevant resumes
   - Download buttons work
   - Top match is highlighted

#### Via API:
```bash
curl -X POST http://localhost:8000/api/match/ \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Senior Python Developer with 5 years experience in backend development, REST APIs, and PostgreSQL",
    "user_id": 1,
    "limit": 10
  }'
```

**Expected response:**
```json
{
  "job_description": "Senior Python Developer...",
  "matches": [
    {
      "resume_id": 1,
      "user_id": 1,
      "format": "pdf",
      "version": 2,
      "filename": "backend_engineer_resume.pdf",
      "similarity_score": 0.8234,
      "uploaded_at": "2026-09-17T04:10:00"
    }
  ],
  "total_candidates": 3
}
```

### 10. Unit Tests

Run backend tests:

```bash
# Enter backend container
docker-compose exec backend bash

# Run tests
cd /app/backend
pytest -v

# Or with coverage
pytest --cov=app --cov-report=html
```

**Expected:**
- All tests pass
- Coverage > 70%

### 11. Text Extraction Verification

Test with different file types:

1. **PDF with text**: Upload → verify "✓ Embedded" appears
2. **LaTeX/TeX file**: Upload → verify text extracted
3. **DOCX**: Upload → verify text extracted (if supported)

**Check extracted text:**
```bash
docker-compose exec backend python -c "
from backend.app.database import SessionLocal
from backend.app.models import Resume

db = SessionLocal()
resume = db.query(Resume).first()
print('Extracted text length:', len(resume.extracted_text or ''))
print('Has embedding:', resume.embedding is not None)
"
```

### 12. Error Handling

Test error cases:

1. **Upload without selecting format**: Should show error
2. **Upload invalid file type**: Should be rejected or show warning
3. **Download non-existent resume**: Should return 404
4. **Match with empty JD**: Should show validation error
5. **Match with very short JD**: Should show error (< 10 chars)

### 13. Storage Verification

Check that files are actually stored:

```bash
# Check storage structure
docker-compose exec backend ls -R /app/storage/

# Verify a specific file exists
docker-compose exec backend cat /app/storage/1/pdf/v_1/test_resume.pdf | head -c 100
```

### 14. Database Verification

Check database records:

```bash
docker-compose exec postgres psql -U postgres -d resumerepo -c "
SELECT id, user_id, format, version, filename, 
       length(extracted_text) as text_len,
       embedding IS NOT NULL as has_embedding
FROM resumes;
"
```

**Expected:**
- Records match uploaded files
- extracted_text is populated
- embedding column has data

### 15. pgvector Extension

Verify pgvector is working:

```bash
docker-compose exec postgres psql -U postgres -d resumerepo -c "
SELECT version FROM pg_available_extensions WHERE name = 'vector';
"
```

**Expected:** Version number (e.g., 0.5.0)

### 16. Performance Test

Upload 10 resumes and measure:

1. Upload time per resume
2. Embedding generation time
3. Match query response time

**Expected:**
- Upload: < 5 seconds per resume
- Match: < 1 second for 10 resumes
- No memory leaks after multiple operations

### 17. Logs Check

Check for any errors or warnings:

```bash
docker-compose logs backend | grep -i error
docker-compose logs postgres | grep -i error
docker-compose logs frontend | grep -i error
```

**Expected:** No critical errors (info/debug logs are OK)

## Known Issues / Limitations

Document any issues found during testing:

- [ ] Text extraction from scanned PDFs (no OCR)
- [ ] DOCX with complex formatting may not extract perfectly
- [ ] First request may be slow (model loading ~2 seconds)
- [ ] No authentication (single user mode)
- [ ] No file size limits enforced
- [ ] No malware scanning

## Sign-off

Testing completed by: _______________
Date: _______________
Environment: _______________
All tests passed: [ ] Yes [ ] No

Notes:
_________________________________
_________________________________
