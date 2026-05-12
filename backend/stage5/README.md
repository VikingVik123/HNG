# Badge Generation Service

A high-performance asynchronous service for generating professional certificate badges for HNG internship participants. Built with FastAPI, Redis Queue (RQ), and PIL for stunning visual certificates.

## 🎯 Features

- ✨ **Asynchronous Processing** - Jobs queued and processed by worker threads
- 📸 **Professional Badges** - Beautiful certificate design with circular profile images
- 🎨 **Customizable Design** - Gold borders, gradient backgrounds, elegant typography
- 💾 **Persistent Storage** - SQLite database for job tracking
- 🚀 **High Performance** - Generates badges in ~0.5-1 second
- 📊 **Status Tracking** - Real-time job status monitoring via REST API
- 🔄 **Error Handling** - Comprehensive error logging and job failure recovery
- 🌐 **REST API** - Easy-to-use endpoints for badge generation and retrieval

---

## 📋 Prerequisites

- Python 3.8+
- Redis (local or cloud)
- pip (Python package manager)

---

## 🚀 Quick Start

### 1. Clone & Navigate

```bash
cd /home/vik/HNG/backend/stage5
```

### 2. Create Virtual Environment

```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r app/requirements.txt
```

### 4. Setup Environment Variables

Create a `.env` file in the stage5 directory:

```bash
# Database
DATABASE_URL=sqlite:///./social_badge.db

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Cloudinary (Optional - for cloud image storage)
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

### 5. Start Redis

```bash
# macOS
brew install redis
redis-server

# Ubuntu/Linux
sudo apt install redis-server
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:latest
```

### 6. Run the Application

Open 3 terminals:

**Terminal 1 - Start FastAPI:**
```bash
cd /home/vik/HNG/backend/stage5
uvicorn app.main:app --reload
```
Access API at: http://localhost:8000
Swagger UI: http://localhost:8000/docs

**Terminal 2 - Start RQ Worker:**
```bash
cd /home/vik/HNG/backend/stage5
rq worker badge-generation
```

**Terminal 3 - Optional: Monitor Queue**
```bash
cd /home/vik/HNG/backend/stage5
rqinfo
```

---

## 📚 API Documentation

### Generate Badge

**Endpoint:** `POST /badges/generate`

**Request:**
```bash
curl -X POST http://localhost:8000/badges/generate \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "hng-async-2024",
    "participant_name": "John Doe",
    "photo_url": "https://example.com/profile.jpg"
  }'
```

**Response (202 Accepted):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

---

### Check Job Status

**Endpoint:** `GET /badges/jobs/{job_id}`

**Request:**
```bash
curl http://localhost:8000/badges/jobs/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "badge_image_url": "http://localhost:8000/badges/badge_550e8400-e29b-41d4-a716-446655440000.png",
  "error_message": null
}
```

**Status Values:**
- `queued` - Job waiting for worker
- `processing` - Worker actively rendering badge
- `completed` - Badge successfully generated
- `failed` - Badge generation failed

---

## 📁 Project Structure

```
stage5/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   │
│   ├── db/
│   │   ├── session.py         # Database connection setup
│   │   └── base.py            # SQLAlchemy declarative base
│   │
│   ├── models/
│   │   └── badge_job.py       # BadgeGenerationJob SQLAlchemy model
│   │
│   ├── schemas/
│   │   └── badge.py           # Pydantic request/response schemas
│   │
│   ├── routes/
│   │   └── badges.py          # Badge API endpoints
│   │
│   ├── services/
│   │   ├── queue.py           # Redis/RQ configuration
│   │   ├── renderer.py        # Badge image rendering service
│   │   └── cloudinary.py      # Image storage service
│   │
│   ├── workers/
│   │   └── badge_worker.py    # RQ job processing logic
│   │
│   ├── enums/
│   │   └── job_status.py      # JobStatus enum
│   │
│   └── rendering/
│       └── engine.py          # PIL badge rendering engine
│
├── badges/                     # Generated badge storage (auto-created)
├── social_badge.db            # SQLite database (auto-created)
├── .env                        # Environment variables
├── README.md                   # This file
└── SYSTEM_DESIGN.md           # Detailed system architecture
```

---

## 🎨 Badge Design

The service generates professional certificates with:

- **Dimensions:** 1080 x 1080 pixels
- **Background:** Blue gradient
- **Profile Image:** Circular with gold border
- **Title:** "CERTIFICATE OF ACHIEVEMENT"
- **Subtitle:** "Async Engine"
- **Footer:** "HNG Internship Program"
- **Format:** PNG (150-300 KB)

---

## 🔧 Configuration

### Database Options

**SQLite (Default - Local Development):**
```
DATABASE_URL=sqlite:///./social_badge.db
```

**PostgreSQL (Production):**
```
DATABASE_URL=postgresql://user:password@localhost/badge_db
```

### Redis Options

**Local Redis:**
```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

**Redis Cloud:**
```
REDIS_URL=redis://default:password@host:port
```

---

## 📊 Usage Examples

### Python Example

```python
import requests
import time

# Generate badge
response = requests.post(
    "http://localhost:8000/badges/generate",
    json={
        "template_id": "hng-async-2024",
        "participant_name": "Jane Smith",
        "photo_url": "https://example.com/jane.jpg"
    }
)

job_id = response.json()["job_id"]
print(f"Job ID: {job_id}")

# Poll status
while True:
    status_response = requests.get(
        f"http://localhost:8000/badges/jobs/{job_id}"
    )
    status = status_response.json()
    
    if status["status"] == "completed":
        print(f"Badge URL: {status['badge_image_url']}")
        break
    elif status["status"] == "failed":
        print(f"Error: {status['error_message']}")
        break
    
    print(f"Status: {status['status']}")
    time.sleep(1)
```

### JavaScript Example

```javascript
// Generate badge
const response = await fetch('http://localhost:8000/badges/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    template_id: 'hng-async-2024',
    participant_name: 'John Doe',
    photo_url: 'https://example.com/profile.jpg'
  })
});

const data = await response.json();
const jobId = data.job_id;

// Poll status
const checkStatus = async () => {
  const statusRes = await fetch(`http://localhost:8000/badges/jobs/${jobId}`);
  const status = await statusRes.json();
  
  if (status.status === 'completed') {
    console.log('Badge URL:', status.badge_image_url);
  } else if (status.status === 'failed') {
    console.error('Error:', status.error_message);
  } else {
    console.log('Status:', status.status);
    setTimeout(checkStatus, 1000);
  }
};

checkStatus();
```

---

## 🐛 Troubleshooting

### Worker Not Starting

**Problem:** `rq worker badge-generation` fails to connect

**Solution:**
1. Ensure Redis is running: `redis-cli ping` (should return `PONG`)
2. Check Redis host/port in `.env`
3. Verify firewall allows Redis port (6379)

### Badge Generation Fails

**Problem:** Status shows `failed` with error message

**Common Issues:**
- **Invalid profile image URL** - Ensure the image URL is publicly accessible
- **Network timeout** - Profile image server is slow/unreachable
- **Font not found** - System missing DejaVu fonts (install: `sudo apt install fonts-dejavu`)
- **SQLite locked** - Database file in use by another process

### Null badge_image_url

**Problem:** Job completed but `badge_image_url` is null

**Solution:**
1. Verify `badges/` directory exists and is writable
2. Check worker logs for rendering errors
3. Ensure participant_photo_url is a valid, accessible image

### API Requests Hang

**Problem:** POST/GET requests timeout

**Solution:**
1. Verify FastAPI server is running
2. Check if Redis is running
3. Use timeout parameter: `curl --max-time 10 http://localhost:8000/badges/jobs/{id}`

---

## 📈 Performance Tips

1. **Multiple Workers:** Run multiple RQ workers for concurrency
   ```bash
   rq worker badge-generation --burst
   ```

2. **Database Indexing:** Add indexes on frequently queried columns
   ```python
   # Already indexed in model: job_id, status
   ```

3. **Image Optimization:** Pre-process profile images for consistent sizing

4. **Queue Monitoring:** Use `rqinfo` to monitor queue depth
   ```bash
   rqinfo --interval 1
   ```

5. **Error Alerts:** Implement monitoring for failed jobs

---

## 🔐 Security Best Practices

1. **Input Validation:** Always validate participant names and URLs
2. **Rate Limiting:** Implement throttling on `/badges/generate` endpoint
3. **Authentication:** Add API key or JWT authentication
4. **CORS:** Configure appropriately for frontend access
5. **File Storage:** Use cloud storage (S3, Cloudinary) for production
6. **Error Messages:** Don't expose internal server errors to clients

---

## 🚢 Deployment

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY app/requirements.txt .
RUN pip install -r requirements.txt

COPY app/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: badge-service
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: api
        image: badge-service:latest
        env:
        - name: DATABASE_URL
          value: postgresql://...
        - name: REDIS_URL
          value: redis://...
```

---

## 📝 Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **sqlalchemy** - ORM
- **psycopg2-binary** - PostgreSQL driver
- **redis** - Redis client
- **rq** - Job queue library
- **pillow** - Image processing
- **httpx** - HTTP client
- **pydantic** - Data validation
- **python-dotenv** - Environment variables

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📖 Documentation

- [System Design Document](./SYSTEM_DESIGN.md) - Detailed architecture and design
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [RQ Documentation](https://python-rq.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

## 🆘 Support

For issues or questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Review [System Design](./SYSTEM_DESIGN.md)
3. Check worker logs: `rq worker badge-generation --verbose`
4. Enable FastAPI debug: `uvicorn app.main:app --reload --log-level debug`

---

## 📄 License

This project is part of the HNG Internship Program.

---

## 👨‍💻 Author

Created as part of the HNG Stage 5 Backend Challenge - Async Engine

---

## ✅ Checklist for Production

- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure Redis Cloud or AWS ElastiCache
- [ ] Set up SSL/TLS certificates
- [ ] Implement API authentication (JWT/API Keys)
- [ ] Configure CORS for frontend domain
- [ ] Set up rate limiting
- [ ] Enable structured logging
- [ ] Configure error tracking (Sentry)
- [ ] Set up CI/CD pipeline
- [ ] Configure monitoring and alerts
- [ ] Use environment-specific `.env` files
- [ ] Enable HTTPS for all endpoints
- [ ] Set up database backups
- [ ] Configure auto-scaling for workers

---

**Last Updated:** May 12, 2026

Happy badge generating! 🎉
