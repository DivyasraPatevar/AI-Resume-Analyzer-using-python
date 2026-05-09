# 🏗️ AI Resume Analyzer - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            Streamlit Web Interface (8501)               │  │
│  │  - Resume Upload                                        │  │
│  │  - Real-time Analysis Display                           │  │
│  │  - Results Dashboard                                    │  │
│  │  - Job Description Matching                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REVERSE PROXY LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Nginx Reverse Proxy (80/443)                    │  │
│  │  - SSL/TLS Termination                                  │  │
│  │  - Request Routing                                      │  │
│  │  - Load Balancing                                       │  │
│  │  - Response Compression                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                    ▼                           ▼
┌────────────────────────────────────────────────────────────────┐
│                      API LAYER                                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │       FastAPI Backend (8000)                           │  │
│  │                                                         │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │  Endpoints                                       │  │  │
│  │  │  • POST   /api/analyze                           │  │  │
│  │  │  • GET    /api/analysis/{id}                     │  │  │
│  │  │  • GET    /api/analyses                          │  │  │
│  │  │  • PUT    /api/analysis/{id}                     │  │  │
│  │  │  • DELETE /api/analysis/{id}                     │  │  │
│  │  │  • POST   /api/analyze-batch                     │  │  │
│  │  │  • POST   /api/compare                           │  │  │
│  │  │  • GET    /health                                │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │  Core Functions                                 │  │  │
│  │  │  • File Processing (PDF, TXT)                   │  │  │
│  │  │  • Resume Analysis Engine                       │  │  │
│  │  │  • ML/NLP Integration                           │  │  │
│  │  │  • Error Handling                               │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                   DATABASE LAYER                               │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │     SQLAlchemy ORM Layer                              │  │
│  │                                                         │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │  CRUD Operations                                │  │  │
│  │  │  • Create (POST)                                │  │  │
│  │  │  • Read (GET)                                   │  │  │
│  │  │  • Update (PUT)                                 │  │  │
│  │  │  • Delete (DELETE)                              │  │  │
│  │  │  • Search & Filter                              │  │  │
│  │  │  • Statistics                                   │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                        ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Database Engines                                      │  │
│  │  ┌──────────────────┐  ┌──────────────────────────┐   │  │
│  │  │ SQLite (Dev)     │  │ PostgreSQL (Production) │   │  │
│  │  │ • Local file DB  │  │ • Network DB            │   │  │
│  │  │ • No setup       │  │ • Scalable              │   │  │
│  │  │ • 1GB+ capacity  │  │ • Replication ready     │   │  │
│  │  └──────────────────┘  └──────────────────────────┘   │  │
│  │                                                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  Table: resume_analyses                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ id | filename | resume_text | job_description |    │  │
│  │ analysis_results | created_at | updated_at      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Component Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                    User's Browser                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       │ HTTP/HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Nginx Proxy (80/443)                          │
│  ┌─────────────────┬─────────────────┐                          │
│  │ SSL Termination │ Load Balancing  │                          │
│  └────────┬────────┴────────┬────────┘                          │
└───────────┼─────────────────┼──────────────────────────────────┘
            │                 │
       HTTP │                 │ HTTP
            ▼                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                  Docker Network                                 │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ Streamlit      │  │ FastAPI        │  │ PostgreSQL       │  │
│  │ Container      │  │ Container      │  │ Container        │  │
│  │ (8501)         │  │ (8000)         │  │ (5432)           │  │
│  │                │  │                │  │                  │  │
│  │ - UI           │  │ - REST API     │  │ - Database       │  │
│  │ - File upload  │  │ - Analysis     │  │ - Storage        │  │
│  │ - Results      │  │ - CRUD ops     │  │ - Queries        │  │
│  │- Dashboard     │  │ - Validation   │  │                  │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│         │ requests         │ queries          │ volumes          │
│         └──────────┬───────┴──────────┬───────┘                  │
│                    │                  │                          │
│             Shared Network         Shared Storage                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
Step 1: Resume Upload
┌─────────┐
│ User    │
└────┬────┘
     │ PDF/TXT File
     ▼
┌──────────────────────┐
│ Streamlit Frontend   │
└────────┬─────────────┘
         │ HTTP POST
         ▼
┌──────────────────────────────────┐
│ Nginx                            │
└────────┬─────────────────────────┘
         │ HTTP Forward
         ▼
┌──────────────────────────────────┐
│ FastAPI /api/analyze             │
│ 1. Validate file type            │
│ 2. Extract text (PyPDF2/native)  │
│ 3. Run analysis                  │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Analysis Engine                  │
│ • Skills extraction              │
│ • ATS scoring                    │
│ • Job fit analysis               │
│ • ML/NLP processing              │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ CRUD Layer                       │
│ Save analysis results            │
└────────┬─────────────────────────┘
         │ INSERT Query
         ▼
┌──────────────────────────────────┐
│ PostgreSQL/SQLite                │
│ Store:                           │
│ - Resume ID                      │
│ - Extracted text                 │
│ - Analysis results (JSON)        │
│ - Metadata (timestamps)          │
└──────────────────────────────────┘
```

---

## Deployment Architecture

```
Development
└── Local Machine
    └── Venv + Local Services
        ├── Streamlit (8501)
        ├── FastAPI (8000)
        └── SQLite DB

Docker Local
└── Docker Desktop
    └── docker-compose up
        ├── Streamlit Container (8501)
        ├── FastAPI Container (8000)
        ├── PostgreSQL Container (5432)
        └── Nginx Container (80/443)

Cloud Deployment (Production)
└── Cloud Provider (AWS/GCP/Azure)
    └── Kubernetes/Managed Services
        ├── API Service (Load Balanced)
        ├── Frontend Service
        ├── Database Service (RDS/Cloud SQL)
        ├── Cache Service (Redis)
        ├── Monitoring (Prometheus/Datadog)
        ├── Logging (ELK/CloudWatch)
        └── Storage (S3/GCS)
```

---

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND                                │
├─────────────────────────────────────────────────────────────┤
│ • Streamlit       - UI Framework                           │
│ • PyPDF2          - PDF Processing                         │
│ • Python-docx     - DOCX Support                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    BACKEND API                              │
├─────────────────────────────────────────────────────────────┤
│ • FastAPI         - Web Framework                          │
│ • Uvicorn         - ASGI Server                            │
│ • Pydantic        - Data Validation                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    DATABASE                                 │
├─────────────────────────────────────────────────────────────┤
│ • SQLAlchemy      - ORM                                    │
│ • Databases       - Async Driver                           │
│ • PostgreSQL      - Production DB                          │
│ • SQLite          - Development DB                         │
│ • Psycopg2        - PostgreSQL Adapter                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    NLP/ML                                   │
├─────────────────────────────────────────────────────────────┤
│ • NLTK            - Text Processing                        │
│ • spaCy           - NLP Pipelines                          │
│ • Transformers    - BERT Models                            │
│ • scikit-learn    - ML Algorithms                          │
│ • Pandas/NumPy    - Data Analysis                          │
│ • sentence-trans  - Semantic Analysis                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE                           │
├─────────────────────────────────────────────────────────────┤
│ • Docker          - Containerization                       │
│ • Docker Compose  - Orchestration                          │
│ • Nginx           - Web Server                             │
│ • PostgreSQL      - Database Server                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Request/Response Flow

```
User Request
    ▼
+─────────────────────────────────────────┐
│ Nginx Reverse Proxy                     │
│ • Route request                         │
│ • SSL/TLS encryption                    │
│ • Load balancing                        │
│ • Request logging                       │
└─────────────┬───────────────────────────┘
              ▼
+─────────────────────────────────────────┐
│ FastAPI Middleware                      │
│ • CORS validation                       │
│ • Request parsing                       │
│ • Authentication (optional)             │
│ • Rate limiting (optional)              │
└─────────────┬───────────────────────────┘
              ▼
+─────────────────────────────────────────┐
│ Route Handler                           │
│ • Input validation                      │
│ • Business logic                        │
│ • File processing                       │
│ • Analysis execution                    │
└─────────────┬───────────────────────────┘
              ▼
+─────────────────────────────────────────┐
│ Database Operations                     │
│ • Query building (ORM)                  │
│ • Connection pooling                    │
│ • Transaction management                │
│ • Result fetching                       │
└─────────────┬───────────────────────────┘
              ▼
+─────────────────────────────────────────┐
│ Response Construction                   │
│ • JSON serialization                    │
│ • Error handling                        │
│ • Status codes                          │
│ • Headers                               │
└─────────────┬───────────────────────────┘
              ▼
+─────────────────────────────────────────┐
│ Nginx Response Processing               │
│ • Compression                           │
│ • Caching headers                       │
│ • SSL encryption                        │
│ • Response logging                      │
└─────────────┬───────────────────────────┘
              ▼
          User Response
```

---

## File Organization

```
ai-resume-analyzer/
│
├── 📄 AA.py                          # Main Streamlit app
├── 📄 requirements.txt               # Python dependencies
│
├── 📁 api/                           # Backend API
│   ├── __init__.py
│   ├── main.py                       # FastAPI app + routes
│   └── utils.py                      # Helper functions
│
├── 📁 database/                      # Database layer
│   ├── __init__.py
│   ├── models.py                     # SQLAlchemy models
│   └── crud.py                       # CRUD operations
│
├── 📁 models/                        # ML models (extensible)
│   └── __init__.py
│
├── 📁 data/                          # Data storage (runtime)
│   └── resumes.db                    # SQLite database
│
├── 🐳 Docker Files
│   ├── Dockerfile                    # Container image
│   ├── docker-compose.yml            # Service orchestration
│   ├── nginx.conf                    # Web server config
│   └── .dockerignore                 # Docker build optimization
│
├── ⚙️ Setup Scripts
│   ├── setup.sh                      # Linux/Mac setup
│   └── setup.bat                     # Windows setup
│
└── 📚 Documentation
    ├── PROJECT_STRUCTURE.md          # Architecture & guide
    ├── QUICK_REFERENCE.md            # Commands & tips
    ├── SETUP_COMPLETE.md             # Setup summary
    ├── VERIFICATION_CHECKLIST.md     # Verification steps
    ├── DEPLOYMENT_CHECKLIST.md       # Deployment guide
    ├── FINAL_SUMMARY.md              # Project summary
    └── .gitignore                    # Git configuration
```

---

## Performance Considerations

```
┌──────────────────────────────────────┐
│ Optimization Strategies              │
├──────────────────────────────────────┤
│ • Async operations (FastAPI)         │
│ • Connection pooling (DB)            │
│ • Response compression (Nginx)       │
│ • Query optimization (ORM)           │
│ • Caching (Redis - optional)         │
│ • Load balancing (Nginx)             │
│ • Container scaling (Docker)         │
│ • CDN for static assets              │
└──────────────────────────────────────┘
```

---

## Monitoring & Logging

```
┌──────────────────────────────────────────────────┐
│ Application Monitoring                          │
├──────────────────────────────────────────────────┤
│ • FastAPI /health endpoint                      │
│ • Docker health checks                          │
│ • Database connection monitoring                │
│ • Request/response logging                      │
│ • Error tracking & alerts                       │
│ • Performance metrics                           │
│ • Resource usage monitoring                     │
└──────────────────────────────────────────────────┘
```

---

**Architecture Version:** 1.0.0  
**Last Updated:** May 9, 2026  
**Status:** ✅ Production Ready
