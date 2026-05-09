"""
Database models for storing resume analyses
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import databases
import sqlalchemy

# Database URL (SQLite for local development, PostgreSQL for production)
DATABASE_URL = "sqlite:///./resumes.db"
# Uncomment for PostgreSQL: DATABASE_URL = "postgresql://user:password@localhost/ai_resume_analyzer"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
Base = declarative_base()

# ============== RESUME ANALYSIS TABLE ==============
resume_analyses = sqlalchemy.Table(
    "resume_analyses",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("filename", String(255), nullable=False),
    Column("resume_text", Text, nullable=False),
    Column("job_description", Text, nullable=True),
    Column("analysis_results", JSON, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
)

# ============== ORM MODEL ==============
class ResumeAnalysis(Base):
    """ORM Model for Resume Analysis"""
    __tablename__ = "resume_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    resume_text = Column(Text, nullable=False)
    job_description = Column(Text, nullable=True)
    analysis_results = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    class Config:
        from_attributes = True

# ============== CREATE TABLES ==============
def create_tables():
    """Create database tables"""
    engine = sqlalchemy.create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
    metadata.create_all(bind=engine)
