"""
FastAPI Backend for AI Resume Analyzer
Main API endpoints for resume analysis and storage
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import ResumeAnalysis, database
from database.crud import create_analysis, get_analysis, get_all_analyses, delete_analysis, update_analysis
from api.utils import extract_resume_text, run_analysis
import PyPDF2

# Create FastAPI app
app = FastAPI(
    title="AI Resume Analyzer API",
    description="API for comprehensive resume analysis with NLP and ML",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== EVENTS ==============
@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown"""
    await database.disconnect()

# ============== HEALTH CHECK ==============
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Resume Analyzer API"}

# ============== RESUME UPLOAD & ANALYSIS ==============
@app.post("/api/analyze")
async def analyze_resume(file: UploadFile = File(...), job_description: str = ""):
    """
    Upload and analyze a resume
    
    Args:
        file: PDF or TXT resume file
        job_description: Optional job description for tailoring
    
    Returns:
        Analysis results with ATS score, skills, recommendations
    """
    try:
        # Validate file type
        if file.content_type not in ["application/pdf", "text/plain"]:
            raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
        
        # Extract text from resume
        resume_text = await extract_resume_text(file)
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from file")
        
        # Run analysis
        analysis = run_analysis(resume_text, job_description)
        
        # Save to database
        db_entry = await create_analysis(
            filename=file.filename,
            resume_text=resume_text,
            job_description=job_description,
            analysis_results=analysis
        )
        
        return {
            "id": db_entry.id,
            "filename": db_entry.filename,
            "analysis": analysis,
            "timestamp": db_entry.created_at
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# ============== RETRIEVE ANALYSIS ==============
@app.get("/api/analysis/{analysis_id}")
async def get_resume_analysis(analysis_id: int):
    """
    Retrieve a specific analysis by ID
    
    Args:
        analysis_id: ID of the analysis to retrieve
    
    Returns:
        Stored analysis results
    """
    try:
        analysis = await get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== LIST ALL ANALYSES ==============
@app.get("/api/analyses")
async def list_analyses(skip: int = 0, limit: int = 10):
    """
    List all stored analyses with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum records to return
    
    Returns:
        List of analyses
    """
    try:
        analyses = await get_all_analyses(skip=skip, limit=limit)
        return {
            "total": len(analyses),
            "analyses": analyses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== UPDATE ANALYSIS ==============
@app.put("/api/analysis/{analysis_id}")
async def update_resume_analysis(analysis_id: int, updates: dict):
    """
    Update an existing analysis
    
    Args:
        analysis_id: ID of the analysis to update
        updates: Dictionary of fields to update
    
    Returns:
        Updated analysis
    """
    try:
        updated = await update_analysis(analysis_id, updates)
        if not updated:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== DELETE ANALYSIS ==============
@app.delete("/api/analysis/{analysis_id}")
async def delete_resume_analysis(analysis_id: int):
    """
    Delete an analysis record
    
    Args:
        analysis_id: ID of the analysis to delete
    
    Returns:
        Confirmation message
    """
    try:
        deleted = await delete_analysis(analysis_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return {"message": "Analysis deleted successfully", "id": analysis_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== BATCH ANALYSIS ==============
@app.post("/api/analyze-batch")
async def analyze_batch(files: list[UploadFile] = File(...)):
    """
    Analyze multiple resumes in batch
    
    Args:
        files: List of resume files
    
    Returns:
        Analysis results for all files
    """
    results = []
    errors = []
    
    for file in files:
        try:
            resume_text = await extract_resume_text(file)
            analysis = run_analysis(resume_text, "")
            
            db_entry = await create_analysis(
                filename=file.filename,
                resume_text=resume_text,
                job_description="",
                analysis_results=analysis
            )
            
            results.append({
                "id": db_entry.id,
                "filename": db_entry.filename,
                "status": "success"
            })
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }

# ============== COMPARISON ENDPOINT ==============
@app.post("/api/compare")
async def compare_resumes(resume1_id: int, resume2_id: int):
    """
    Compare two resumes side-by-side
    
    Args:
        resume1_id: ID of first resume
        resume2_id: ID of second resume
    
    Returns:
        Comparison metrics
    """
    try:
        analysis1 = await get_analysis(resume1_id)
        analysis2 = await get_analysis(resume2_id)
        
        if not analysis1 or not analysis2:
            raise HTTPException(status_code=404, detail="One or both analyses not found")
        
        comparison = {
            "resume1": {
                "filename": analysis1.filename,
                "ats_score": analysis1.analysis_results.get("ats_score", 0),
                "skills_count": len(analysis1.analysis_results.get("skills_found", []))
            },
            "resume2": {
                "filename": analysis2.filename,
                "ats_score": analysis2.analysis_results.get("ats_score", 0),
                "skills_count": len(analysis2.analysis_results.get("skills_found", []))
            }
        }
        
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
