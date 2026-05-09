"""
CRUD operations for resume analyses
"""

from database.models import database, resume_analyses, ResumeAnalysis
from datetime import datetime
from typing import List, Optional

# ============== CREATE ==============
async def create_analysis(
    filename: str,
    resume_text: str,
    job_description: str,
    analysis_results: dict
) -> dict:
    """
    Create a new resume analysis record
    
    Args:
        filename: Name of the resume file
        resume_text: Extracted resume content
        job_description: Job description (if provided)
        analysis_results: Analysis results dictionary
    
    Returns:
        Created record with ID
    """
    query = resume_analyses.insert().values(
        filename=filename,
        resume_text=resume_text,
        job_description=job_description,
        analysis_results=analysis_results,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    last_record_id = await database.execute(query)
    return {
        "id": last_record_id,
        "filename": filename,
        "created_at": datetime.utcnow()
    }

# ============== READ ==============
async def get_analysis(analysis_id: int) -> Optional[dict]:
    """
    Retrieve a specific analysis by ID
    
    Args:
        analysis_id: ID of the analysis
    
    Returns:
        Analysis record or None
    """
    query = resume_analyses.select().where(resume_analyses.c.id == analysis_id)
    return await database.fetch_one(query)

# ============== READ ALL ==============
async def get_all_analyses(skip: int = 0, limit: int = 10) -> List[dict]:
    """
    Retrieve all analyses with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum records to return
    
    Returns:
        List of analysis records
    """
    query = resume_analyses.select().offset(skip).limit(limit)
    return await database.fetch_all(query)

# ============== SEARCH ==============
async def search_analyses(filename: str = "", skill: str = "") -> List[dict]:
    """
    Search analyses by filename or skill
    
    Args:
        filename: Filename to search
        skill: Skill to search in analysis results
    
    Returns:
        Matching records
    """
    if filename:
        query = resume_analyses.select().where(
            resume_analyses.c.filename.ilike(f"%{filename}%")
        )
    elif skill:
        # Note: This is a simplified search; for production use full-text search
        query = resume_analyses.select()
    
    return await database.fetch_all(query)

# ============== UPDATE ==============
async def update_analysis(analysis_id: int, updates: dict) -> Optional[dict]:
    """
    Update an existing analysis
    
    Args:
        analysis_id: ID of the analysis
        updates: Dictionary of fields to update
    
    Returns:
        Updated record or None
    """
    # Ensure updated_at is set
    updates["updated_at"] = datetime.utcnow()
    
    query = resume_analyses.update().where(
        resume_analyses.c.id == analysis_id
    ).values(**updates)
    
    await database.execute(query)
    return await get_analysis(analysis_id)

# ============== DELETE ==============
async def delete_analysis(analysis_id: int) -> bool:
    """
    Delete an analysis record
    
    Args:
        analysis_id: ID of the analysis to delete
    
    Returns:
        True if deleted, False if not found
    """
    query = resume_analyses.delete().where(resume_analyses.c.id == analysis_id)
    result = await database.execute(query)
    return result > 0

# ============== DELETE ALL ==============
async def delete_all_analyses() -> int:
    """
    Delete all analysis records (use with caution)
    
    Returns:
        Number of records deleted
    """
    query = resume_analyses.delete()
    return await database.execute(query)

# ============== GET STATISTICS ==============
async def get_statistics() -> dict:
    """
    Get statistics about stored analyses
    
    Returns:
        Dictionary with statistics
    """
    # Count total records
    count_query = resume_analyses.select()
    records = await database.fetch_all(count_query)
    
    return {
        "total_analyses": len(records),
        "oldest_analysis": records[0]["created_at"] if records else None,
        "newest_analysis": records[-1]["created_at"] if records else None,
        "average_ats_score": sum(
            r["analysis_results"].get("ats_score", 0) for r in records
        ) / len(records) if records else 0
    }
