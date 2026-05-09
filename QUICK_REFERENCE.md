# 🚀 Quick Reference Guide

## What's New ✨

### New Files Created:
```
✅ api/main.py            - FastAPI backend (8 endpoints)
✅ api/utils.py           - Helper functions
✅ database/models.py     - SQLAlchemy ORM + Config
✅ database/crud.py       - Database operations
✅ Dockerfile             - Container config
✅ docker-compose.yml     - Multi-service orchestration
✅ nginx.conf             - Reverse proxy
✅ setup.sh               - Linux/Mac setup
✅ setup.bat              - Windows setup
✅ PROJECT_STRUCTURE.md   - Full documentation
✅ .dockerignore          - Docker optimization
✅ .gitignore             - Git ignore rules
```

---

## 🎯 Quick Commands

### **Windows Setup**
```bash
setup.bat
```

### **Linux/Mac Setup**
```bash
bash setup.sh
```

### **Docker (Any OS)**
```bash
docker-compose up --build
```

### **Manual Local Setup**
```bash
# Create venv
python -m venv venv
venv\Scripts\activate

# Install deps
pip install -r requirements.txt

# Terminal 1: API
python -m uvicorn api.main:app --reload --port 8000

# Terminal 2: Frontend
streamlit run AA.py
```

---

## 📍 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:8501 | Streamlit UI |
| API | http://localhost:8000 | REST endpoints |
| API Docs | http://localhost:8000/docs | Interactive docs |
| Swagger | http://localhost:8000/redoc | ReDoc documentation |
| Database | localhost:5432 | PostgreSQL (Docker) |

---

## 🔌 API Quick Reference

### Upload & Analyze
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@resume.pdf" \
  -F "job_description=Senior Developer"
```

### Get Analysis
```bash
curl http://localhost:8000/api/analysis/1
```

### List All
```bash
curl "http://localhost:8000/api/analyses?skip=0&limit=10"
```

### Delete
```bash
curl -X DELETE http://localhost:8000/api/analysis/1
```

### Batch Upload
```bash
curl -X POST http://localhost:8000/api/analyze-batch \
  -F "files=@resume1.pdf" \
  -F "files=@resume2.pdf"
```

---

## 📦 Project Structure

```
AI RESUME ANALYSER/
├── api/                   ← FastAPI Backend
│   ├── main.py           (REST endpoints)
│   └── utils.py          (Helpers)
│
├── database/              ← Database Layer
│   ├── models.py         (ORM)
│   └── crud.py           (Operations)
│
├── models/                ← ML Models (empty now)
├── AA.py                  ← Streamlit UI
├── requirements.txt       ← Dependencies
├── Dockerfile             ← Container
├── docker-compose.yml     ← Orchestration
└── nginx.conf             ← Reverse Proxy
```

---

## 🔑 Key Features

✅ **Backend API**
- Upload resumes
- Analyze with ML/NLP
- Store in database
- Compare resumes
- Batch processing

✅ **Database**
- SQLite (dev)
- PostgreSQL (prod)
- Async operations
- Full CRUD
- Search & stats

✅ **Docker**
- Multi-container
- Auto-scaling ready
- SSL support
- Easy deployment

✅ **Frontend**
- Streamlit UI
- Real-time analysis
- Interactive results
- Export options

---

## 🐛 Common Issues & Fixes

### **Port Already in Use**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### **Docker Won't Start**
```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

### **Database Error**
```bash
# Check PostgreSQL
docker-compose exec postgres psql -U resume_user -d ai_resume_analyzer

# Reset
docker-compose down -v
docker-compose up
```

### **Missing Dependencies**
```bash
pip install -r requirements.txt --force-reinstall
```

---

## 📊 Database Configuration

### Development (SQLite)
```python
DATABASE_URL = "sqlite:///./resumes.db"
```

### Production (PostgreSQL)
```python
DATABASE_URL = "postgresql://user:password@localhost/ai_resume_analyzer"
```

Create database:
```bash
createdb ai_resume_analyzer
```

---

## 🚀 Deployment Options

### **Heroku**
```bash
heroku create ai-resume-analyzer
git push heroku main
```

### **AWS EC2**
```bash
# Push to ECR
docker tag ai-resume-analyzer:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/ai-resume-analyzer
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/ai-resume-analyzer
```

### **Google Cloud**
```bash
gcloud app deploy
```

### **DigitalOcean**
```bash
docker-machine create --driver digitalocean ai-resume
docker-compose up -d
```

---

## 📈 Performance Tips

1. **Caching**
   - Cache analysis results
   - Redis integration
   - Browser caching

2. **Database**
   - Connection pooling
   - Index optimization
   - Query tuning

3. **API**
   - Response compression
   - Async operations
   - Rate limiting

---

## 🔐 Security Checklist

- [ ] Use environment variables for secrets
- [ ] Enable HTTPS/SSL
- [ ] Implement API authentication
- [ ] Add rate limiting
- [ ] Validate all inputs
- [ ] Regular backups
- [ ] Update dependencies
- [ ] Use strong DB passwords
- [ ] CORS configuration
- [ ] CSRF protection

---

## 📚 Documentation

**For Complete Guide:**
- `PROJECT_STRUCTURE.md` - Full documentation
- `SETUP_COMPLETE.md` - Setup summary

**API Documentation:**
- Visit: http://localhost:8000/docs
- Interactive Swagger UI

---

## 🎯 Next Actions

1. ✅ Run `setup.bat` (Windows) or `bash setup.sh` (Linux/Mac)
2. ✅ Test local environment
3. ✅ Upload a test resume
4. ✅ Verify API endpoints
5. ✅ Deploy to cloud (optional)

---

## 💡 Pro Tips

- Use `docker-compose logs -f` to debug
- API docs auto-generated at `/docs`
- Database browser with DBeaver
- Use Postman for API testing
- Enable hot-reload for development
- Use `.env` for secrets

---

## 📞 Support

- Check documentation first
- Review error messages carefully
- Check logs for details
- Test endpoints individually
- Use API docs for testing

---

**Status:** ✅ **Ready to Use**
**Version:** 1.0.0
**Last Updated:** May 9, 2026

**Next:** Run `setup.bat` or `bash setup.sh` to get started!
