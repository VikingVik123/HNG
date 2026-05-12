# Badge Generation Service - System Design Document

## 1. Overview

The Badge Generation Service is an asynchronous microservice that generates professional certificate badges for HNG internship participants. It processes badge generation requests through a job queue system and stores results in a database.

**Key Features:**
- Asynchronous job processing using Redis Queue (RQ)
- Professional certificate badge rendering
- Support for participant profile images
- Persistent job tracking and status monitoring
- RESTful API for badge generation and status retrieval

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Badge Routes (/badges)                  │   │
│  │  • POST /badges/generate - Create badge job         │   │
│  │  • GET /badges/jobs/{job_id} - Get job status       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           ↓                                    ↓
    ┌──────────────┐                 ┌────────────────┐
    │  SQLite DB   │                 │  Redis Queue   │
    │ (Badge Jobs) │                 │  (Job Queue)   │
    └──────────────┘                 └────────────────┘
                                            ↓
                              ┌──────────────────────────┐
                              │   RQ Worker Process      │
                              │ (Badge Rendering Engine) │
                              └──────────────────────────┘
                                    ↓
                        ┌───────────────────────┐
                        │  Image Rendering      │
                        │  • PIL/Pillow         │
                        │  • Circular Masking   │
                        │  • Font Rendering     │
                        └───────────────────────┘
                                    ↓
                        ┌───────────────────────┐
                        │  Local File Storage   │
                        │  (badges/ directory)  │
                        │  Served by FastAPI    │
                        └───────────────────────┘
```

---

## 3. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **API** | FastAPI | REST API framework, automatic OpenAPI docs |
| **Database** | SQLite | Job storage, lightweight persistent data |
| **Job Queue** | Redis + RQ | Async job processing, worker management |
| **Image Processing** | Pillow (PIL) | Badge rendering, image manipulation |
| **HTTP Client** | httpx | Downloading participant profile images |
| **ORM** | SQLAlchemy | Database abstraction, query builder |
| **Config** | python-dotenv | Environment variable management |

---

## 4. Data Models

### BadgeGenerationJob
```python
{
  job_id: String(36)              # UUID (primary key)
  template_id: String             # Badge template identifier
  participant_name: String(200)   # Participant full name
  participant_photo_url: Text     # URL to profile image
  status: Enum                    # QUEUED, PROCESSING, COMPLETED, FAILED
  badge_image_url: Text           # Generated badge URL (nullable until complete)
  error_message: Text             # Error details if failed (nullable)
  created_at: DateTime            # Job creation timestamp
  completed_at: DateTime          # Job completion timestamp (nullable)
}
```

### JobStatus Enum
```python
QUEUED      # Job received, waiting for worker
PROCESSING  # Worker is actively processing
COMPLETED   # Badge successfully generated
FAILED      # Error during processing
```

---

## 5. API Endpoints

### POST /badges/generate
**Description:** Create and enqueue a badge generation job

**Request:**
```json
{
  "template_id": "hng-async-2024",
  "participant_name": "John Doe",
  "photo_url": "https://example.com/profile.jpg"
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

**Flow:**
1. Validate request payload
2. Create BadgeGenerationJob record in database (status: QUEUED)
3. Enqueue `process_badge_generation` job to Redis Queue
4. Return job_id and status

---

### GET /badges/jobs/{job_id}
**Description:** Retrieve badge generation job status and result

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "badge_image_url": "http://localhost:8000/badges/badge_550e8400-e29b-41d4-a716-446655440000.png",
  "error_message": null
}
```

**Status Meanings:**
- `queued`: Job waiting for worker
- `processing`: Worker actively rendering badge
- `completed`: Badge ready at `badge_image_url`
- `failed`: Check `error_message` for details

---

## 6. Worker Process Flow

```
┌─────────────────────────────────────────────────────────────┐
│                 RQ Worker Listening                         │
│              (rq worker badge-generation)                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
            Job received from Redis Queue
                          ↓
    ┌───────────────────────────────────────────┐
    │ process_badge_generation(job_id: str)     │
    │                                            │
    │ 1. Query database for job record          │
    │ 2. Update status: PROCESSING              │
    │ 3. Call generate_badge_image()            │
    │    • Download profile image via httpx     │
    │    • Render badge (1080x1080 PNG)         │
    │    • Create circular profile frame        │
    │ 4. Call save_image()                      │
    │    • Save to badges/ directory            │
    │    • Return public URL path               │
    │ 5. Update database:                       │
    │    • badge_image_url = /badges/...        │
    │    • status = COMPLETED                   │
    │    • completed_at = now()                 │
    │ 6. On error:                              │
    │    • status = FAILED                      │
    │    • error_message = exception details    │
    └───────────────────────────────────────────┘
                          ↓
                  Job Complete
```

---

## 7. Badge Rendering Engine

### Visual Design
- **Dimensions:** 1080 x 1080 pixels
- **Background:** Blue gradient (#1a3a52 base)
- **Borders:** Double gold frame (#d4af37)
- **Profile Image:** Circular with gold border (350px)
- **Title:** "CERTIFICATE OF ACHIEVEMENT" (top)
- **Subtitle:** "Async Engine" (center, below profile)
- **Footer:** "HNG Internship Program" (bottom)

### Rendering Steps
1. Create canvas with gradient background
2. Draw decorative borders (gold)
3. Download and convert profile image to RGB
4. Create circular mask for profile image
5. Create gold-bordered circular frame
6. Composite elements onto canvas
7. Render text with proper fonts and positioning
8. Export as PNG to BytesIO buffer

---

## 8. Data Flow Diagram

```
User Request
    │
    ├─→ POST /badges/generate
    │        │
    │        ├─→ Validate payload
    │        ├─→ Create BadgeGenerationJob (QUEUED)
    │        └─→ Enqueue to Redis
    │
    └─→ Response: job_id + status
         │
         User polls GET /badges/jobs/{job_id}
         │
         ├─→ Status: QUEUED (job waiting)
         ├─→ Status: PROCESSING (rendering)
         └─→ Status: COMPLETED (✓ badge_image_url available)
              │
              └─→ User downloads badge via badge_image_url
```

---

## 9. Configuration

### Environment Variables (.env)

```ini
# Database
DATABASE_URL=sqlite:///./social_badge.db

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Cloudinary (Optional - for cloud storage)
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

### Key Configurations
- **Database:** SQLite (local file-based, no external dependency)
- **Queue:** Redis (local or cloud via REDIS_URL)
- **Storage:** Local filesystem (`badges/` directory)
- **Worker:** Single process listening to `badge-generation` queue

---

## 10. Directory Structure

```
app/
├── main.py                    # FastAPI application
├── requirements.txt           # Dependencies
├── .env                       # Configuration
│
├── db/
│   ├── session.py            # Database connection
│   └── base.py               # SQLAlchemy base
│
├── models/
│   └── badge_job.py          # BadgeGenerationJob model
│
├── schemas/
│   └── badge.py              # Request/response schemas
│
├── routes/
│   └── badges.py             # Badge API endpoints
│
├── services/
│   ├── queue.py              # Redis/RQ configuration
│   ├── renderer.py           # Image rendering service
│   └── cloudinary.py         # Image storage service
│
├── workers/
│   └── badge_worker.py       # Job processing logic
│
├── enums/
│   └── job_status.py         # JobStatus enum
│
└── rendering/
    └── engine.py             # Badge rendering engine
```

---

## 11. Deployment Guide

### Local Development

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start FastAPI
cd /home/vik/HNG/backend/stage5
uvicorn app.main:app --reload

# Terminal 3: Start RQ Worker
cd /home/vik/HNG/backend/stage5
rq worker badge-generation
```

### Production Considerations

1. **Redis:** Use managed Redis (Redis Cloud, AWS ElastiCache)
2. **Database:** Consider PostgreSQL for scalability
3. **Worker:** Run multiple worker processes for concurrency
4. **Storage:** Use Cloudinary or S3 for badge storage
5. **Monitoring:** Use `rqinfo` or Flower for queue monitoring
6. **Logging:** Implement structured logging and error tracking

---

## 12. Error Handling

| Error | Cause | Resolution |
|-------|-------|-----------|
| Job not found | Invalid job_id | Return 404 error |
| Profile image download failed | Network error or invalid URL | Store error_message, mark as FAILED |
| Image rendering error | Corrupted image or PIL issue | Log error, retry mechanism |
| Database connection error | SQLite file locked | Implement connection pooling |
| Redis connection error | Redis server down | Use connection retry logic |

---

## 13. Performance Metrics

- **Badge Generation Time:** ~0.5-1 second per badge
- **Database Queries:** 3-4 per job (create, fetch, update)
- **Image Size:** ~150-300 KB (PNG format)
- **Memory Usage:** ~50-100 MB for rendering engine

---

## 14. Security Considerations

1. **Input Validation:** Validate URLs and participant data
2. **Rate Limiting:** Implement throttling on /badges/generate
3. **Authentication:** Add API key or JWT authentication
4. **CORS:** Configure appropriately for frontend access
5. **Error Messages:** Don't expose internal server errors
6. **Image Storage:** Validate file types before processing

---

## 15. Future Enhancements

- [ ] Multiple badge templates
- [ ] Custom text/fonts per template
- [ ] Webhook notifications on job completion
- [ ] Batch badge generation API
- [ ] Badge download/sharing features
- [ ] Admin dashboard for job monitoring
- [ ] Analytics and statistics
- [ ] Email delivery of badges
