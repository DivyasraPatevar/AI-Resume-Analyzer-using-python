# AI Resume Analyzer - Complete Project Setup

## 📋 Project Structure

```
AI RESUME ANALYSER/
├── AA.py                      # Main Streamlit frontend app
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker container configuration
├── docker-compose.yml         # Multi-container orchestration
├── nginx.conf                 # Nginx reverse proxy config
├── 
├── api/                       # FastAPI backend
│   ├── __init__.py
│   ├── main.py               # FastAPI application & routes
│   └── utils.py              # Helper functions (file extraction, analysis)
│
├── database/                 # Database layer
│   ├── __init__.py
│   ├── models.py            # SQLAlchemy models & configuration
│   └── crud.py              # CRUD operations for database
│
├── models/                   # ML/NLP models & schemas
│   └── __init__.py
│
├── data/                     # Local data storage (created at runtime)
│   └── resumes.db           # SQLite database
│
└── docs/
    ├── API_DOCUMENTATION.md
    └── DEPLOYMENT_GUIDE.md
```

## 🚀 Quick Start

### Option 1: Local Development (Without Docker)

#### Prerequisites
- Python 3.10+
- pip package manager
- Virtual environment

#### Setup Steps

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# OR
source venv/bin/activate      # Linux/Mac
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run Streamlit frontend:**
```bash
streamlit run AA.py
```

Visit: http://localhost:8501

4. **Run FastAPI backend (in another terminal):**
```bash
python -m uvicorn api.main:app --reload --port 8000
```

API Docs: http://localhost:8000/docs

---

### Option 2: Docker Development

#### Prerequisites
- Docker
- Docker Compose

#### Setup Steps

1. **Build and start containers:**
```bash
docker-compose up --build
```

2. **Services will be available at:**
- Frontend (Streamlit): http://localhost:8501
- API (FastAPI): http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: PostgreSQL on localhost:5432
- Reverse Proxy (Nginx): http://localhost:80

3. **Stop services:**
```bash
docker-compose down
```

4. **View logs:**
```bash
docker-compose logs -f api
```

---

## 📚 API Endpoints

### 1. **Health Check**
```
GET /health
```

### 2. **Upload & Analyze Resume**
```
POST /api/analyze
- file: Resume file (PDF/TXT)
- job_description: Optional job description
```

### 3. **Retrieve Analysis**
```
GET /api/analysis/{analysis_id}
```

### 4. **List All Analyses**
```
GET /api/analyses?skip=0&limit=10
```

### 5. **Update Analysis**
```
PUT /api/analysis/{analysis_id}
- updates: Dictionary of fields to update
```

### 6. **Delete Analysis**
```
DELETE /api/analysis/{analysis_id}
```

### 7. **Batch Analysis**
```
POST /api/analyze-batch
- files: List of resume files
```

### 8. **Compare Resumes**
```
POST /api/compare?resume1_id=1&resume2_id=2
```

---

## 🗄️ Database Configuration

### SQLite (Development)
- Default: `sqlite:///./resumes.db`
- Stored locally in project directory

### PostgreSQL (Production)
Update `DATABASE_URL` in `database/models.py`:
```python
DATABASE_URL = "postgresql://user:password@localhost/ai_resume_analyzer"
```

#### Create Database:
```bash
psql -U postgres
CREATE DATABASE ai_resume_analyzer;
CREATE USER resume_user WITH PASSWORD 'secure_password';
ALTER ROLE resume_user SET client_encoding TO 'utf8';
ALTER ROLE resume_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE resume_user SET default_transaction_deferral TO on;
ALTER ROLE resume_user SET default_transaction_deferral_readonly TO off;
GRANT ALL PRIVILEGES ON DATABASE ai_resume_analyzer TO resume_user;
```

---

## 🔧 Configuration

### Environment Variables
Create `.env` file:
```
DATABASE_URL=sqlite:///./resumes.db
API_HOST=0.0.0.0
API_PORT=8000
STREAMLIT_PORT=8501
DEBUG=True
```

### Streamlit Configuration
Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[logger]
level = "info"

[client]
maxUploadSize = 100
```

---

## 📦 Docker Commands

### Build Image
```bash
docker build -t ai-resume-analyzer:latest .
```

### Run Container
```bash
docker run -p 8000:8000 -p 8501:8501 ai-resume-analyzer:latest
```

### Docker Compose - Common Commands
```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose up --build

# Scale services
docker-compose up --scale api=3

# Execute command in container
docker-compose exec api python -m spacy download en_core_web_sm
```

---

## 🧪 Testing

### Run API Tests
```bash
pytest tests/test_api.py -v
```

### Run Database Tests
```bash
pytest tests/test_database.py -v
```

### Load Testing
```bash
locust -f locustfile.py --host=http://localhost:8000
```

---

## 📊 Database Schema

### resume_analyses Table
```sql
CREATE TABLE resume_analyses (
    id INTEGER PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    resume_text TEXT NOT NULL,
    job_description TEXT,
    analysis_results JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔐 Security Best Practices

1. **API Security**
   - Implement authentication (JWT tokens)
   - Rate limiting on endpoints
   - Input validation
   - CORS configuration

2. **Database Security**
   - Use strong passwords
   - Enable SSL connections
   - Regular backups
   - Principle of least privilege

3. **Deployment**
   - Use environment variables for secrets
   - Enable HTTPS
   - Implement CSRF protection
   - Regular security updates

---

## 📈 Performance Optimization

1. **Caching**
   - Cache analysis results
   - Cache skill database
   - Redis for distributed caching

2. **Database**
   - Index frequently searched columns
   - Connection pooling
   - Query optimization

3. **API**
   - Async operations
   - Response compression
   - CDN for static assets

---

## 🐛 Troubleshooting

### Issue: Database Connection Error
```bash
# Check PostgreSQL is running
psql -U postgres -d ai_resume_analyzer

# Reset database
docker-compose down
docker volume rm ai_resume_analyzer_postgres_data
docker-compose up
```

### Issue: Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Issue: Docker Build Fails
```bash
# Clear Docker cache
docker system prune -a

# Rebuild
docker-compose up --build
```

---

## 📝 Development Guidelines

1. **Code Style**
   - Follow PEP 8
   - Use type hints
   - Document functions with docstrings

2. **Git Workflow**
   - Create feature branches
   - Write meaningful commit messages
   - Submit pull requests for review

3. **Testing**
   - Write unit tests for functions
   - Integration tests for API endpoints
   - Test coverage > 80%

---

## 🚀 Deployment

### Cloud Platforms

**AWS (EC2 + RDS)**
```bash
# Push image to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag ai-resume-analyzer:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/ai-resume-analyzer:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/ai-resume-analyzer:latest
```

**Heroku**
```bash
heroku create ai-resume-analyzer
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

**Google Cloud**
```bash
gcloud app deploy app.yaml
```

---

## 📞 Support

For issues and questions:
1. Check documentation
2. Review existing issues
3. Create GitHub issue with details

---

## 📄 License

This project is licensed under the MIT License.

---

**Last Updated:** May 2026
**Maintainer:** AI Resume Analyzer Team
