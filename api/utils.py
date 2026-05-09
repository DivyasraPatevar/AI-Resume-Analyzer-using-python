"""
Utility functions for API - file handling and analysis
"""

import sys
import os
from io import BytesIO
from fastapi import UploadFile
import PyPDF2

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from main AA.py analysis functions (placeholder - will be refactored)
try:
    from AA import (
        extract_skills, calculate_ats_score, detect_education,
        detect_experience, identify_strengths, identify_weaknesses,
        generate_suggestions, analyze_job_fit
    )
except ImportError:
    # Fallback implementations
    pass

async def extract_resume_text(file: UploadFile) -> str:
    """
    Extract text from uploaded resume file (PDF or TXT)
    
    Args:
        file: UploadFile object
    
    Returns:
        Extracted text content
    """
    content = await file.read()
    
    if file.content_type == "application/pdf":
        # Extract from PDF
        pdf_reader = PyPDF2.PdfReader(BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    
    elif file.content_type == "text/plain":
        # Extract from TXT
        return content.decode('utf-8')
    
    else:
        raise ValueError(f"Unsupported file type: {file.content_type}")

def run_analysis(resume_text: str, job_description: str = "") -> dict:
    """
    Run comprehensive resume analysis
    
    Args:
        resume_text: Extracted resume content
        job_description: Optional job description
    
    Returns:
        Analysis results dictionary
    """
    try:
        # Extract skills
        skills = extract_skills(resume_text)
        
        # Calculate ATS score
        ats_score = calculate_ats_score(resume_text)
        
        # Identify strengths and weaknesses
        strengths = identify_strengths(resume_text, skills, ats_score)
        weaknesses = identify_weaknesses(resume_text, skills)
        
        # Generate suggestions
        suggestions = generate_suggestions(resume_text, ats_score, skills)
        
        # Job fit analysis
        job_fit = analyze_job_fit(resume_text, skills)
        
        return {
            "ats_score": ats_score,
            "skills_found": skills,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
            "job_fit_analysis": job_fit
        }
    
    except Exception as e:
        return {"error": str(e)}

def format_analysis_response(analysis: dict) -> dict:
    """
    Format analysis results for API response
    
    Args:
        analysis: Raw analysis dictionary
    
    Returns:
        Formatted response
    """
    return {
        "overview": {
            "ats_score": analysis.get("ats_score", 0),
            "skills_count": len(analysis.get("skills_found", [])),
            "strengths_count": len(analysis.get("strengths", [])),
            "improvement_areas": len(analysis.get("weaknesses", []))
        },
        "details": analysis
    }
