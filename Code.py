import streamlit as st
import PyPDF2
import json
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import Counter
try:
    import spacy  # type: ignore
except ImportError:
    spacy = None

try:
    from transformers import pipeline  # type: ignore
except ImportError:
    pipeline = None

import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
@st.cache_resource
def download_nltk_resources():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')
    try:
        nltk.data.find('corpora/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('averaged_perceptron_tagger')

download_nltk_resources()

# Load spaCy model
@st.cache_resource
def load_spacy_model():
    if spacy is None:
        st.warning("spaCy is not installed. NLP features will be limited.")
        return None

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        st.info("Downloading spaCy model...")
        import subprocess
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
        nlp = spacy.load("en_core_web_sm")
    return nlp

# Load BERT-based zero-shot classifier
@st.cache_resource
def load_bert_classifier():
    if pipeline is None:
        st.warning("Transformers is not installed. BERT analysis will be disabled.")
        return None
    try:
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        return classifier
    except Exception as e:
        st.warning(f"BERT model loading: {e}")
        return None

# Configure page
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# CSS styling
st.markdown("""
    <style>
    .header {
        text-align: center;
        color: #1f77b4;
        padding: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .skill-badge {
        display: inline-block;
        background-color: #1f77b4;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        margin: 5px 5px 5px 0;
        font-weight: bold;
    }
    .keyword-highlight {
        background-color: #FFE5B4;
        font-weight: bold;
        padding: 2px 4px;
        border-radius: 3px;
        color: #333;
    }
    .education-highlight {
        background-color: #D4E8F7;
        font-weight: bold;
        padding: 2px 4px;
        border-radius: 3px;
        color: #0056b3;
    }
    .experience-highlight {
        background-color: #E8F5E9;
        font-weight: bold;
        padding: 2px 4px;
        border-radius: 3px;
        color: #1b5e20;
    }
    .entity-box {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# Title and Introduction
st.markdown("<div class='header'><h1>📄 AI Resume Analyzer</h1></div>", unsafe_allow_html=True)
st.markdown("<div style='background: linear-gradient(135deg, #1f77b4 0%, #5ab9f8 100%); padding: 18px; border-radius: 14px; color: white; margin-bottom: 20px;'>\n    <h2 style=\"margin: 0;\">Resume intelligence powered with local NLP, ATS optimization, and role-fit insights.</h2>\n    <p style=\"margin: 8px 0 0; font-size: 16px;\">Upload a resume, add a job description, and get recruiter-ready feedback instantly.</p>\n</div>", unsafe_allow_html=True)

resume_text = ""

if 'what_if_input' not in st.session_state:
    st.session_state.what_if_input = ''

if 'what_if_result' not in st.session_state:
    st.session_state.what_if_result = None

if 'what_if_resume_name' not in st.session_state:
    st.session_state.what_if_resume_name = None

if 'job_description' not in st.session_state:
    st.session_state.job_description = ''

if 'job_desc_resume_name' not in st.session_state:
    st.session_state.job_desc_resume_name = None

if 'job_match_results' not in st.session_state:
    st.session_state.job_match_results = None

# Sidebar for information
with st.sidebar:
    st.header("⚙️ About This Tool")
    st.markdown("""
    This analyzer uses advanced NLP and Machine Learning to provide comprehensive resume analysis.
    
    **Technologies Used:**
    - NLTK: Natural Language Processing
    - scikit-learn: Machine Learning
    - Pandas: Data Analysis
    - PyPDF2: PDF Processing
    """)
    
    st.markdown("---")
    st.markdown("### How to use:")
    st.markdown("""
    1. Upload a PDF or TXT resume
    2. Click 'Analyze Resume'
    3. Get detailed feedback
    """)

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

def extract_text_from_txt(txt_file):
    """Extract text from TXT file"""
    try:
        return txt_file.read().decode('utf-8')
    except Exception as e:
        st.error(f"Error reading TXT: {e}")
        return None

# --- Analysis Functions ---

# Technical skills database - Enhanced
TECHNICAL_SKILLS = {
    'Programming Languages': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'typescript', 'scala', 'r', 'matlab', 'perl', 'vb.net', 'objective-c', 'groovy', 'clojure'],
    'Web Frameworks': ['django', 'flask', 'fastapi', 'spring', 'react', 'angular', 'vue', 'express', 'node', 'laravel', 'rails', 'asp.net', 'blazor', 'next.js', 'nuxt', 'svelte', 'ember', 'backbone'],
    'Databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'cassandra', 'redis', 'oracle', 'nosql', 'elasticsearch', 'dynamodb', 'firestore', 'neo4j', 'influxdb', 'mariadb'],
    'Cloud Platforms': ['aws', 'azure', 'gcp', 'heroku', 'docker', 'kubernetes', 'cloud', 'openshift', 'cloudfoundry', 'ibm cloud', 'alibaba cloud'],
    'Data Tools': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'spark', 'hadoop', 'tableau', 'power bi', 'excel', 'r', 'plotly', 'matplotlib', 'seaborn', 'dask', 'airflow'],
    'DevOps': ['ci/cd', 'jenkins', 'gitlab', 'github', 'git', 'devops', 'linux', 'nginx', 'apache', 'terraform', 'ansible', 'puppet', 'docker', 'k8s'],
    'Soft Skills': ['leadership', 'communication', 'teamwork', 'problem-solving', 'project management', 'agile', 'scrum', 'kanban', 'analytics', 'stakeholder management']
}

# Education degrees and certifications database
EDUCATION_KEYWORDS = {
    'Degrees': ['bachelor', 'master', 'phd', 'diploma', 'associate', 'degree', 'b.s.', 'b.a.', 'm.s.', 'm.a.', 'b.tech', 'm.tech', 'b.e.', 'm.e.'],
    'Fields': ['computer science', 'engineering', 'business', 'information technology', 'data science', 'statistics', 'mathematics', 'economics', 'finance', 'management', 'communications', 'marketing'],
    'Institutions': ['university', 'college', 'institute', 'school', 'academy', 'polytechnic'],
    'Certifications': ['certified', 'certification', 'aws certified', 'azure certified', 'google cloud', 'scrum', 'pmp', 'prince2', 'cissp', 'ccna', 'comptia']
}

# Experience-related keywords
EXPERIENCE_KEYWORDS = {
    'Job Titles': ['software engineer', 'developer', 'analyst', 'manager', 'specialist', 'consultant', 'architect', 'lead', 'senior', 'junior', 'associate', 'director', 'engineer', 'scientist', 'designer', 'coordinator'],
    'Action Verbs': ['led', 'managed', 'developed', 'created', 'implemented', 'designed', 'improved', 'increased', 'decreased', 'optimized', 'automated', 'coordinated', 'collaborated', 'spearheaded', 'pioneered', 'accelerated'],
    'Achievement Words': ['achieved', 'accomplished', 'exceeded', 'surpassed', 'milestone', 'awarded', 'recognized', 'outperformed']
}

# --- Enhanced NLP Functions ---

def detect_education(text, nlp):
    """Enhanced education detection using spaCy NER and pattern matching"""
    education_entries = []
    
    # Fallback if spaCy is unavailable
    if nlp is None:
        degree_patterns = [
            r'((?:bachelor|master|phd|b\.s\.|m\.s\.|b\.a\.|m\.a\.|b\.tech|m\.tech)[^\n]*?(?:in|of)\s+([a-z\s]+?)(?:\,|$))',
            r'([A-Z][a-z\s]+)?\s+(bachelor|master|phd|diploma)[^\n]*?(?:in)?\s+([a-z\s]+)?',
        ]
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                degree_text = ' '.join(filter(None, match))
                if degree_text and degree_text not in education_entries:
                    education_entries.append(degree_text.strip())
        return education_entries[:5]

    doc = nlp(text)
    education_section_pattern = r'(?:education|academic|qualification|degree|school|university|college)[\s\n]+(.*?)(?=\n[A-Z]|$)'
    education_matches = re.findall(education_section_pattern, text, re.IGNORECASE | re.DOTALL)
    
    if education_matches:
        education_text = '\n'.join(education_matches)
        # Extract entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'GPE']:  # Organization or Location
                if re.search(education_section_pattern, text, re.IGNORECASE | re.DOTALL):
                    if ent.text in education_text:
                        education_entries.append(ent.text)
    
    # Pattern matching for degrees
    degree_patterns = [
        r'((?:bachelor|master|phd|b\.s\.|m\.s\.|b\.a\.|m\.a\.|b\.tech|m\.tech)[^\n]*?(?:in|of)\s+([a-z\s]+?)(?:\,|$))',
        r'([A-Z][a-z\s]+)?\s+(bachelor|master|phd|diploma)[^\n]*?(?:in)?\s+([a-z\s]+)?',
    ]
    
    for pattern in degree_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            degree_text = ' '.join(filter(None, match))
            if degree_text and degree_text not in education_entries:
                education_entries.append(degree_text.strip())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_entries = []
    for entry in education_entries:
        if entry.lower() not in seen:
            seen.add(entry.lower())
            unique_entries.append(entry)
    
    return unique_entries[:5]  # Return top 5

def detect_experience(text, nlp):
    """Enhanced experience detection using spaCy NER"""
    experience_entries = []
    organizations = []
    
    if nlp is None:
        # Fallback to regex-based experience parsing
        job_title_pattern = r'([A-Z][a-z\s]+(?:Engineer|Developer|Manager|Analyst|Architect|Lead|Director|Specialist|Consultant)(?:[^\n]*)?)'
        job_matches = re.findall(job_title_pattern, text)
        for job in job_matches[:5]:
            if job.strip() and job.strip() not in experience_entries:
                experience_entries.append(job.strip())

        org_matches = re.findall(r'\b([A-Z][A-Za-z0-9& ]{2,}?(?:Inc|LLC|Ltd|Corp|Company|Institute|University|Organization|Systems|Technologies|Solutions))\b', text)
        organizations = list(dict.fromkeys(org_matches))[:3]

        years_pattern = r'(\d+)\s*(?:years?|yrs?|y\.)'
        years_matches = re.findall(years_pattern, text.lower())
        total_years = max([int(y) for y in years_matches]) if years_matches else 0

        return {
            'positions': experience_entries[:3],
            'organizations': organizations,
            'years': total_years
        }

    doc = nlp(text)
    
    # Extract named entities (ORG, PERSON, DATE, etc.)
    dates = []
    
    for ent in doc.ents:
        if ent.label_ == 'ORG':
            organizations.append(ent.text)
        elif ent.label_ == 'DATE':
            dates.append(ent.text)
    
    # Find experience section
    exp_section_pattern = r'(?:experience|work\s+experience|employment|career|professional)[\s\n]+(.*?)(?=\n(?:education|skills|certification|project)|$)'
    exp_matches = re.findall(exp_section_pattern, text, re.IGNORECASE | re.DOTALL)
    
    if exp_matches:
        exp_text = '\n'.join(exp_matches)
        
        # Extract job titles and companies
        job_title_pattern = r'([A-Z][a-z\s]+(?:Engineer|Developer|Manager|Analyst|Architect|Lead|Director|Specialist|Consultant)(?:[^\n]*)?)'
        job_matches = re.findall(job_title_pattern, exp_text)
        
        for job in job_matches[:5]:
            if job.strip() not in experience_entries:
                experience_entries.append(job.strip())
    
    # Extract years of experience
    years_pattern = r'(\d+)\s*(?:years?|yrs?|y\.)'
    years_matches = re.findall(years_pattern, text.lower())
    total_years = max([int(y) for y in years_matches]) if years_matches else 0
    
    return {
        'positions': experience_entries[:3],
        'organizations': list(dict.fromkeys(organizations))[:3],
        'years': total_years
    }

def highlight_keywords(text, skills):
    """Highlight technical keywords in text"""
    highlighted_text = text
    
    # Highlight technical skills
    for skill in skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        highlighted_text = re.sub(
            pattern,
            lambda match: f'<span class="keyword-highlight">{match.group(0)}</span>',
            highlighted_text,
            flags=re.IGNORECASE
        )
    
    # Highlight action verbs
    action_verbs = EXPERIENCE_KEYWORDS['Action Verbs']
    for verb in action_verbs:
        pattern = r'\b' + re.escape(verb) + r'\b'
        highlighted_text = re.sub(
            pattern,
            lambda match: f'<span class="experience-highlight">{match.group(0)}</span>',
            highlighted_text,
            flags=re.IGNORECASE
        )
    
    # Highlight education keywords
    for edu_keywords in EDUCATION_KEYWORDS.values():
        for keyword in edu_keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            highlighted_text = re.sub(
                pattern,
                lambda match: f'<span class="education-highlight">{match.group(0)}</span>',
                highlighted_text,
                flags=re.IGNORECASE
            )
    
    return highlighted_text

def analyze_text_with_bert(text, classifier, aspects=None):
    """Analyze text using BERT-based zero-shot classification"""
    if classifier is None:
        return {}
    
    try:
        if aspects is None:
            aspects = ['technical skills', 'leadership experience', 'communication skills', 'problem-solving', 'project management']
        
        # Split text into chunks for analysis
        sentences = sent_tokenize(text)
        chunk_size = 5
        chunks = [' '.join(sentences[i:i+chunk_size]) for i in range(0, len(sentences), chunk_size) if sentences[i:i+chunk_size]]
        
        results = {}
        for aspect in aspects:
            scores = []
            for chunk in chunks[:3]:  # Analyze first 3 chunks
                try:
                    result = classifier(chunk[:512], candidate_labels=[aspect], multi_class=True)  # BERT has 512 token limit
                    if result and 'scores' in result:
                        scores.append(result['scores'][0])
                except Exception:
                    continue
            
            if scores:
                results[aspect] = round(np.mean(scores) * 100, 2)
        
        return results
    except Exception as e:
        st.warning(f"BERT analysis: {e}")
        return {}

def preprocess_text(text):
    """Preprocess text for analysis"""
    lemmatizer = WordNetLemmatizer()
    text = text.lower()
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t.isalnum() and t not in stop_words]
    return tokens, text.lower()

def extract_skills(text):
    """Extract skills from resume text"""
    skills_found = []
    text_lower = text.lower()
    
    for category, skills in TECHNICAL_SKILLS.items():
        for skill in skills:
            # Look for the skill as a whole word
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                skills_found.append(skill.title())
    
    return list(set(skills_found))  # Remove duplicates 

def calculate_ats_score(text):
    """Calculate ATS compatibility score"""
    score = 0
    max_score = 100
    
    # Check for essential sections
    sections = ['experience', 'education', 'skills', 'contact', 'email', 'phone']
    section_score = 0
    for section in sections:
        if re.search(r'\b' + section + r'\b', text.lower()):
            section_score += 10
    
    score += min(section_score, 30)  # Max 30 points for sections
    
    # Check keyword density (more keywords = better for ATS)
    tokens, _ = preprocess_text(text)
    technical_keywords = sum(1 for keyword in TECHNICAL_SKILLS.values() for item in keyword if item in ' '.join(tokens))
    keyword_score = min((technical_keywords / max(len(tokens), 1)) * 100, 40)
    score += keyword_score  # Max 40 points for keywords
    
    # Check for quantifiable achievements
    achievements = len(re.findall(r'\d+%|\d+\s*(increased|decreased|improved|grew|boosted|reduced|saved)', text.lower()))
    achievement_score = min(achievements * 5, 20)
    score += achievement_score  # Max 20 points for achievements
    
    # Check for action verbs
    action_verbs = ['led', 'developed', 'managed', 'created', 'implemented', 'designed', 'improved', 'increased', 'decreased', 'optimized', 'automated', 'streamlined']
    action_score = sum(1 for verb in action_verbs if verb in text.lower()) * 2
    score += min(action_score, 10)  # Max 10 points for action verbs
    
    return int(min(score, 100)) 

@st.cache_data(show_spinner=False)
def simulate_resume_update(original_text, addition_text):
    """Simulate runtime impact of adding a hypothetical update to the resume."""
    addition_text = addition_text.strip()
    if not addition_text:
        return None

    original_score = calculate_ats_score(original_text)
    simulated_text = original_text.rstrip() + '\n' + addition_text
    new_score = calculate_ats_score(simulated_text)
    delta = new_score - original_score

    added_skills = extract_skills(addition_text)

    section_signals = []
    if re.search(r'\b(project|developed|built|designed|launched|delivered|implemented)\b', addition_text.lower()):
        section_signals.append('Experience/Projects')
    if re.search(r'\b(certification|certified|degree|course|training|education|bootcamp)\b', addition_text.lower()):
        section_signals.append('Education/Certifications')
    if re.search(r'\b(linkedin|github|portfolio|contact|email|phone)\b', addition_text.lower()):
        section_signals.append('Contact & Links')

    suggestions = []
    if delta <= 0:
        suggestions.append('Add measurable metrics such as percentages, time savings, or revenue impact.')
        suggestions.append('Mention relevant technical keywords and specific tools used.')
        if not added_skills:
            suggestions.append('Include at least one skill from the target role, such as Python, AWS, or SQL.')
    else:
        if new_score < 80:
            suggestions.append('Keep adding strong metrics and role-specific keywords to push the score above 80.')
        if len(added_skills) < 2:
            suggestions.append('Add more explicit technical skills or tools to strengthen keyword density.')

    return {
        'original_score': original_score,
        'new_score': new_score,
        'delta': delta,
        'added_skills': added_skills,
        'changed_sections': section_signals,
        'suggestions': suggestions,
        'simulated_text': simulated_text
    }


def run_what_if_simulation(resume_text, addition_text):
    """Backend wrapper for the What-If resume simulator."""
    if not resume_text or not addition_text:
        return None
    return simulate_resume_update(resume_text, addition_text)


def process_job_description_matching(resume_text, job_description, skills, ats_score, experience_data):
    """Backend wrapper for job description matching and tailoring."""
    if not job_description or not resume_text:
        return None
    
    return {
        'tailored': tailor_resume_for_job(resume_text, job_description),
        'explainable': explainable_job_match(resume_text, job_description, skills, ats_score)
    }


def rewrite_resume_text(resume_text):
    """Rewrite resume language to be more action-oriented."""
    replacements = {
        'responsible for': 'led',
        'worked on': 'delivered',
        'participated in': 'contributed to',
        'helped with': 'supported',
        'assisted with': 'supported',
        'experience in': 'expertise in',
        'skilled in': 'proficient in',
        'dedicated to': 'focused on',
        'involved in': 'executed',
        'responsible for': 'owned'
    }
    rewritten = resume_text
    for weak, strong in replacements.items():
        rewritten = re.sub(r'\b' + re.escape(weak) + r'\b', strong, rewritten, flags=re.IGNORECASE)

    bullets = [line for line in rewritten.splitlines() if re.match(r'^\s*[-*•]', line)]
    if bullets:
        return '\n'.join(bullets[:12])
    return rewritten[:1200] + ('...' if len(rewritten) > 1200 else '')


def evaluate_resume_formatting(text):
    """Score resume formatting and highlight issues."""
    score = 0
    issues = []
    lower = text.lower()

    if re.search(r'\n\s*[-*•]', text):
        score += 25
    else:
        issues.append('Use bullet points to improve readability')

    if re.search(r'\b(education|experience|skills|projects|certifications|contact|summary)\b', lower):
        score += 25
    else:
        issues.append('Add clear section headers for structure')

    if len(text.splitlines()) > 10:
        score += 20
    else:
        issues.append('Expand the resume with richer achievements and details')

    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text):
        score += 15
    else:
        issues.append('Include an email address in the contact section')

    if re.search(r'\b(https?://|github\.com|linkedin\.com)\b', lower):
        score += 15
    else:
        issues.append('Include LinkedIn, GitHub, or portfolio links')

    return int(min(score, 100)), issues


def detect_exaggeration(text):
    """Detect over-the-top or suspicious resume language."""
    text_lower = text.lower()
    flags = []
    suspicious_phrases = ['expert', 'guru', 'rockstar', 'ninja', 'best-in-class', 'world-class', 'visionary', 'unlimited', 'always', 'never']
    for phrase in suspicious_phrases:
        if phrase in text_lower:
            flags.append(f"Potential exaggeration language: '{phrase}'")

    if re.search(r'\b\d\+\s*years?\b', text_lower):
        flags.append('Vague experience claim using a plus sign instead of precise dates')

    return flags if flags else ['No major exaggeration signals detected.']


def analyze_github_and_linkedin(text):
    """Analyze LinkedIn and GitHub presence in the resume."""
    lower = text.lower()
    github = re.search(r'https?://(?:www\.)?github\.com/[A-Za-z0-9_-]+', text)
    linkedin = re.search(r'https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+', text)
    portfolio = re.search(r'https?://(?:www\.)?(portfolio|behance|dribbble|devpost)\.[^\s]+', text)

    result = {
        'github': github.group(0) if github else None,
        'linkedin': linkedin.group(0) if linkedin else None,
        'portfolio': portfolio.group(0) if portfolio else None,
        'projects_detected': bool(github or portfolio)
    }

    if not result['linkedin']:
        result['linkedin_tip'] = 'Add a LinkedIn URL to improve recruiter visibility.'
    if not result['github'] and result['projects_detected']:
        result['github_tip'] = 'Include a GitHub profile link if you mention technical projects.'

    return result


def semantic_resume_overview(text):
    """Summarize resume structure and semantic coverage."""
    sections = ['summary', 'experience', 'education', 'skills', 'projects', 'certifications', 'contact']
    lower = text.lower()
    detected = [section for section in sections if re.search(r'\b' + section + r'\b', lower)]
    missing = [section for section in sections if section not in detected]

    return {
        'overview': f'Detected {len(detected)} core sections: {", ".join(detected) if detected else "None"}.',
        'detected_sections': detected,
        'missing_sections': missing
    }


def analyze_personality_insights(text):
    """Infer personality traits from resume keywords."""
    lower = text.lower()
    traits = {
        'Leadership': int(bool(re.search(r'\b(led|managed|directed|spearheaded|owned)\b', lower))) * 80,
        'Collaboration': int(bool(re.search(r'\b(collaborated|team|partnered|cross-functional|stakeholder)\b', lower))) * 75,
        'Innovation': int(bool(re.search(r'\b(innovated|designed|created|developed|optimized)\b', lower))) * 80,
        'Dependability': int(bool(re.search(r'\b(reliable|dedicated|consistent|organized)\b', lower))) * 70,
        'Growth Mindset': int(bool(re.search(r'\b(learned|improved|adapted|upskilled|growth)\b', lower))) * 75
    }
    return traits


def build_resume_heatmap_data(text, skills):
    """Build a simple heatmap summary for resume strength categories."""
    lower = text.lower()
    categories = {
        'Technical Depth': len(skills),
        'Leadership Signals': len(re.findall(r'\b(led|managed|directed|spearheaded)\b', lower)),
        'Quantified Impact': len(re.findall(r'\d+%|\d+\s*(increased|decreased|improved|grew)', lower)),
        'Collaboration': len(re.findall(r'\b(collaborated|team|partnered|cross-functional)\b', lower))
    }
    return categories


def generate_skill_gap_and_learning_path(skills, job_fit):
    """Create a learning path based on missing skills for the strongest role fit."""
    role_keywords = {
        'Software Engineer': ['python', 'java', 'javascript', 'c++', 'api', 'database', 'git'],
        'Data Scientist': ['python', 'pandas', 'scikit-learn', 'tensorflow', 'sql', 'analysis', 'ml'],
        'DevOps Engineer': ['docker', 'kubernetes', 'aws', 'ci/cd', 'linux', 'terraform', 'jenkins'],
        'Full Stack Developer': ['javascript', 'react', 'node', 'sql', 'api', 'css', 'html'],
        'Product Manager': ['leadership', 'agile', 'roadmap', 'stakeholder', 'analytics', 'strategy'],
        'QA Engineer': ['testing', 'automation', 'selenium', 'api', 'debugging', 'junit']
    }
    if not job_fit:
        return {'target_role': 'Unknown', 'missing_skills': [], 'learning_path': ['Add more role-specific keywords and projects.']}

    target_role = max(job_fit, key=job_fit.get)
    lower_skills = [s.lower() for s in skills]
    missing = [keyword for keyword in role_keywords.get(target_role, []) if keyword not in lower_skills]
    learning_path = [f'Learn {skill} through hands-on projects, online courses, or certifications.' for skill in missing[:6]]
    if not learning_path:
        learning_path = [f'Your resume is already well aligned with the {target_role} role. Continue deepening project impact.']

    return {'target_role': target_role, 'missing_skills': missing, 'learning_path': learning_path}


def generate_ai_feedback(resume_text, ats_score, skills, experience_data):
    """Generate comprehensive AI-powered feedback for resume improvement."""
    feedback = []
    
    # ATS-focused feedback
    if ats_score < 50:
        feedback.append({
            'type': 'critical',
            'title': 'Low ATS Compatibility',
            'message': 'Your resume has a low ATS score. Add more industry keywords and structure with clear sections.',
            'action': 'Ensure consistent formatting with bullet points and standard section headers.'
        })
    elif ats_score < 70:
        feedback.append({
            'type': 'warning',
            'title': 'Moderate ATS Score',
            'message': 'Your resume passes basic ATS filters but could be optimized further.',
            'action': 'Add technical keywords and quantified metrics to improve the score.'
        })
    else:
        feedback.append({
            'type': 'success',
            'title': 'Strong ATS Optimization',
            'message': 'Your resume is well-optimized for ATS systems.',
            'action': 'Focus on content quality and tailoring for specific roles.'
        })
    
    # Skills feedback
    if len(skills) < 5:
        feedback.append({
            'type': 'warning',
            'title': 'Limited Skills Listed',
            'message': f'Only {len(skills)} skills detected. Industry roles typically feature 8-12 core skills.',
            'action': 'Expand your skills section with relevant technical and soft skills.'
        })
    elif len(skills) > 20:
        feedback.append({
            'type': 'info',
            'title': 'Comprehensive Skill Set',
            'message': f'Excellent: {len(skills)} skills identified across multiple domains.',
            'action': 'Prioritize the top 8-10 most relevant skills for each job application.'
        })
    
    # Experience feedback
    years = experience_data.get('years', 0) if experience_data else 0
    if years < 1:
        feedback.append({
            'type': 'info',
            'title': 'Entry-Level Profile',
            'message': 'Your resume shows early-career experience. Focus on projects and learning achievements.',
            'action': 'Highlight impactful projects, internships, and growth areas.'
        })
    elif years >= 5:
        feedback.append({
            'type': 'success',
            'title': 'Solid Experience Base',
            'message': f'Strong {years}+ years of experience. Emphasize leadership and impact.',
            'action': 'Showcase mentoring, team leadership, and strategic contributions.'
        })
    
    return feedback


def detailed_multi_role_analysis(text, skills, ats_score):
    """Provide detailed fit analysis across multiple roles with recommendations."""
    role_details = {
        'Software Engineer': {
            'keywords': ['python', 'java', 'javascript', 'c++', 'api', 'database', 'git', 'agile'],
            'ideal_ats': 75,
            'description': 'Software development and system design'
        },
        'Data Scientist': {
            'keywords': ['python', 'pandas', 'scikit-learn', 'tensorflow', 'sql', 'analysis', 'ml', 'r'],
            'ideal_ats': 80,
            'description': 'Data analysis and machine learning'
        },
        'DevOps Engineer': {
            'keywords': ['docker', 'kubernetes', 'aws', 'ci/cd', 'linux', 'terraform', 'jenkins'],
            'ideal_ats': 72,
            'description': 'Infrastructure and deployment automation'
        },
        'Full Stack Developer': {
            'keywords': ['javascript', 'react', 'node', 'sql', 'api', 'css', 'html', 'mongodb'],
            'ideal_ats': 78,
            'description': 'Frontend and backend web development'
        },
        'Product Manager': {
            'keywords': ['leadership', 'agile', 'roadmap', 'stakeholder', 'analytics', 'strategy', 'metrics'],
            'ideal_ats': 65,
            'description': 'Product strategy and team management'
        },
        'QA Engineer': {
            'keywords': ['testing', 'automation', 'selenium', 'api', 'debugging', 'junit', 'ci/cd'],
            'ideal_ats': 70,
            'description': 'Quality assurance and testing'
        }
    }
    
    text_lower = text.lower()
    analysis = {}
    
    for role, details in role_details.items():
        matching_keywords = sum(1 for keyword in details['keywords'] if keyword in text_lower)
        fit_percentage = int((matching_keywords / len(details['keywords'])) * 100)
        ats_gap = details['ideal_ats'] - ats_score
        
        analysis[role] = {
            'fit_percentage': fit_percentage,
            'matched_keywords': [kw for kw in details['keywords'] if kw in text_lower],
            'missing_keywords': [kw for kw in details['keywords'] if kw not in text_lower],
            'ats_gap': ats_gap,
            'recommendation': f'Strong fit for {role}' if fit_percentage >= 60 else f'Moderate fit. Add more {details["description"]} keywords.',
            'description': details['description']
        }
    
    return analysis


def generate_interview_questions(resume_text, job_title='Software Engineer'):
    """Generate role-specific interview questions based on resume content."""
    questions = []
    lower = resume_text.lower()
    
    # General questions
    questions.append({
        'category': 'General',
        'question': 'Tell us about your most impactful project and the challenges you faced.',
        'focus': 'Leadership and problem-solving'
    })
    
    questions.append({
        'category': 'General',
        'question': 'How do you stay current with new technologies and industry trends?',
        'focus': 'Learning and growth'
    })
    
    # Technical questions
    if any(term in lower for term in ['python', 'java', 'javascript', 'c++']):
        questions.append({
            'category': 'Technical',
            'question': 'Explain a complex technical problem you solved. Walk us through your approach.',
            'focus': 'Problem-solving and technical depth'
        })
    
    if any(term in lower for term in ['api', 'rest', 'microservices']):
        questions.append({
            'category': 'Technical',
            'question': 'Describe your experience designing or working with APIs. What best practices do you follow?',
            'focus': 'Architecture and design'
        })
    
    if any(term in lower for term in ['led', 'managed', 'team', 'mentored']):
        questions.append({
            'category': 'Behavioral',
            'question': 'Give an example of a time you led a team or project. How did you handle conflicts?',
            'focus': 'Leadership and collaboration'
        })
    
    if any(term in lower for term in ['agile', 'scrum', 'sprint']):
        questions.append({
            'category': 'Behavioral',
            'question': 'How do you approach working in an Agile/Scrum environment? Describe a sprint experience.',
            'focus': 'Team dynamics and adaptability'
        })
    
    # Default behavioral questions
    if len(questions) < 6:
        questions.append({
            'category': 'Behavioral',
            'question': 'Describe a situation where you had to learn something quickly under pressure.',
            'focus': 'Adaptability and learning'
        })
    
    questions.append({
        'category': 'Behavioral',
        'question': 'Why are you interested in this role and our company?',
        'focus': 'Motivation and alignment'
    })
    
    return questions[:8]  # Return top 8 questions


def tailor_resume_for_job(resume_text, job_description):
    """Tailor resume by inserting job-specific keywords and rewriting bullets."""
    if not job_description:
        return {"tailored_resume": resume_text, "improvements": []}
    
    job_keywords = re.findall(r'\b[a-z]+\b', job_description.lower())
    job_keywords = [kw for kw in job_keywords if len(kw) > 3]
    
    # Extract resume bullets
    bullets = [line.strip() for line in resume_text.split('\n') if re.match(r'^\s*[-*•]', line)]
    tailored_bullets = []
    improvements = []
    
    for bullet in bullets[:10]:
        clean_bullet = re.sub(r'^[-*•]\s*', '', bullet).strip()
        enhanced = clean_bullet
        
        # Add relevant job keywords if missing
        for keyword in job_keywords[:5]:
            if keyword not in enhanced.lower() and len(enhanced) < 120:
                if any(action in enhanced.lower() for action in ['built', 'created', 'developed', 'designed']):
                    enhanced += f' using {keyword}' if 'using' not in enhanced.lower() else ''
        
        # Strengthen weak language
        weak_to_strong = {
            'worked on': 'developed',
            'involved in': 'led',
            'helped': 'contributed',
            'participated': 'spearheaded',
            'did': 'delivered'
        }
        
        for weak, strong in weak_to_strong.items():
            if weak in enhanced.lower():
                enhanced = re.sub(r'\b' + weak + r'\b', strong, enhanced, flags=re.IGNORECASE)
                improvements.append(f"Changed '{weak}' to '{strong}' for more impact")
        
        # Add metric if missing
        if not re.search(r'\d+%|\d+\s*(increased|decreased|improved|saved)', enhanced.lower()):
            enhanced += ' (estimated impact quantifiable)'
        
        tailored_bullets.append(f"• {enhanced}")
    
    tailored_resume = '\n'.join(tailored_bullets)
    return {"tailored_resume": tailored_resume, "improvements": improvements[:5]}


def explainable_job_match(resume_text, job_description, skills, ats_score):
    """Provide explainable breakdown of job match score."""
    if not job_description:
        return {"score": 0, "reasons": [], "breakdown": {}}
    
    job_lower = job_description.lower()
    resume_lower = resume_text.lower()
    
    matching_skills = [s for s in skills if s.lower() in job_lower]
    missing_skills = [re.findall(r'\b[a-z]+\b', job_lower)[i] for i in range(min(5, len(job_lower.split()))) if len(re.findall(r'\b[a-z]+\b', job_lower)[i]) > 3]
    
    reasons = []
    breakdown = {}
    
    # Positive signals
    if matching_skills:
        reasons.append(f"✅ Skills Match: {len(matching_skills)} relevant skills detected ({', '.join(matching_skills[:3])})")
        breakdown['skills_match'] = min(len(matching_skills) * 10, 40)
    
    if re.search(r'\d+\s*(years?|yr)', resume_lower):
        years_found = int(re.search(r'(\d+)\s*(?:years?|yr)', resume_lower).group(1))
        if 'years' in job_lower or 'experience' in job_lower:
            reasons.append(f"✅ Experience Aligned: {years_found}+ years mentioned")
            breakdown['experience_match'] = 20
    
    if re.search(r'\d+%|\d+\s*(increased|decreased|improved)', resume_lower):
        reasons.append("✅ Quantified Impact: Achievement metrics found")
        breakdown['quantified_metrics'] = 20
    
    if ats_score >= 70:
        reasons.append(f"✅ High ATS Score: {ats_score}/100 indicates strong resume optimization")
        breakdown['ats_quality'] = 15
    
    # Negative signals
    missing_count = 0
    for keyword in ['python', 'java', 'cloud', 'database', 'api']:
        if keyword in job_lower and keyword not in resume_lower:
            missing_count += 1
            reasons.append(f"❌ Missing: {keyword.upper()} skill mentioned in job posting")
    
    breakdown['missing_skills_penalty'] = -missing_count * 5
    
    final_score = sum(breakdown.values())
    final_score = max(0, min(100, final_score))
    
    return {
        "score": final_score,
        "reasons": reasons,
        "breakdown": breakdown,
        "matching_skills": matching_skills,
        "missing_skills": [s for s in ['Python', 'Java', 'Docker', 'AWS', 'SQL'] if s.lower() in job_lower and s.lower() not in resume_lower]
    }


def score_resume_sections(resume_text):
    """Score individual resume sections (Skills, Experience, Projects, Education)."""
    sections_text = {
        'skills': '',
        'experience': '',
        'projects': '',
        'education': ''
    }
    
    section_pattern = r'(?:^|\n)(skills?|experience|projects?|education)[:\s]*\n(.*?)(?=\n(?:skills?|experience|projects?|education|$))'
    matches = re.finditer(section_pattern, resume_text, re.IGNORECASE | re.DOTALL)
    
    for match in matches:
        section_name = match.group(1).lower()
        section_content = match.group(2)
        for key in sections_text:
            if key in section_name:
                sections_text[key] = section_content
    
    scores = {}
    
    # Skills section scoring
    if sections_text['skills']:
        skill_count = len(re.findall(r',', sections_text['skills'])) + 1
        scores['skills'] = min(90, 30 + skill_count * 5)
    else:
        scores['skills'] = 20
    
    # Experience section scoring
    if sections_text['experience']:
        exp_bullets = len(re.findall(r'[-*•]', sections_text['experience']))
        quantified = len(re.findall(r'\d+%|\d+\s*(increased|decreased)', sections_text['experience']))
        action_verbs = len(re.findall(r'\b(led|managed|developed|created)\b', sections_text['experience']))
        scores['experience'] = min(90, 30 + exp_bullets * 8 + quantified * 10 + action_verbs * 5)
    else:
        scores['experience'] = 30
    
    # Projects section scoring
    if sections_text['projects']:
        projects = len(re.findall(r'[-*•]', sections_text['projects']))
        tech_depth = len(re.findall(r'\b(python|java|react|aws|docker|kubernetes)\b', sections_text['projects'], re.IGNORECASE))
        scores['projects'] = min(95, 40 + projects * 10 + tech_depth * 8)
    else:
        scores['projects'] = 15
    
    # Education section scoring
    if sections_text['education']:
        has_degree = bool(re.search(r'\b(bachelor|master|phd|b\.s\.|m\.s\.|b\.a\.|m\.a\.|diploma)\b', sections_text['education'], re.IGNORECASE))
        has_uni = bool(re.search(r'\b(university|college|institute|school)\b', sections_text['education'], re.IGNORECASE))
        has_cert = bool(re.search(r'\b(certification|certified|aws|gcp|azure)\b', sections_text['education'], re.IGNORECASE))
        scores['education'] = 60 if has_degree and has_uni else 40 + (20 if has_cert else 0)
    else:
        scores['education'] = 25
    
    return scores


def analyze_project_impact(resume_text):
    """Detect weak vs strong project descriptions and score impact."""
    project_section = re.search(r'(?:projects?)[:\s]*\n(.*?)(?=\n[A-Z]|$)', resume_text, re.IGNORECASE | re.DOTALL)
    
    if not project_section:
        return {"projects": [], "weak_count": 0, "strong_count": 0}
    
    project_text = project_section.group(1)
    projects = re.split(r'\n\s*[-*•]', project_text)
    
    analyzed_projects = []
    
    for project in projects:
        if len(project.strip()) < 5:
            continue
        
        metrics = 0
        tech_depth = 0
        impact_score = 0
        
        # Check for metrics
        if re.search(r'\d+k\s*(?:users?|downloads?)|(\d+)%|(\d+)x', project):
            metrics = 1
        
        # Check for tech depth
        tech_keywords = ['python', 'java', 'react', 'nodejs', 'aws', 'docker', 'tensorflow', 'api', 'database', 'machine learning']
        tech_depth = sum(1 for tech in tech_keywords if tech in project.lower())
        
        # Overall impact
        if metrics and tech_depth >= 2:
            impact_score = 85
            strength = "Strong"
        elif metrics or tech_depth >= 2:
            impact_score = 60
            strength = "Moderate"
        else:
            impact_score = 35
            strength = "Weak"
        
        analyzed_projects.append({
            "description": project.strip()[:100],
            "strength": strength,
            "impact_score": impact_score,
            "metrics_found": bool(metrics),
            "tech_depth": tech_depth
        })
    
    weak_count = sum(1 for p in analyzed_projects if p["strength"] == "Weak")
    strong_count = sum(1 for p in analyzed_projects if p["strength"] == "Strong")
    
    return {
        "projects": analyzed_projects,
        "weak_count": weak_count,
        "strong_count": strong_count,
        "overall_score": int(np.mean([p["impact_score"] for p in analyzed_projects])) if analyzed_projects else 0
    }


def compare_with_benchmark(skills, ats_score, experience_years=0):
    """Compare resume against top candidate benchmarks."""
    benchmarks = {
        'top_10_percent': {'ats_score': 85, 'skills_count': 12, 'years': 5, 'projects': 3},
        'top_25_percent': {'ats_score': 75, 'skills_count': 10, 'years': 4, 'projects': 2},
        'average': {'ats_score': 65, 'skills_count': 7, 'years': 3, 'projects': 1},
        'below_average': {'ats_score': 45, 'skills_count': 4, 'years': 1, 'projects': 0}
    }
    
    user_percentile = 'average'
    if ats_score >= 85 and len(skills) >= 12:
        user_percentile = 'top_10_percent'
    elif ats_score >= 75 and len(skills) >= 10:
        user_percentile = 'top_25_percent'
    elif ats_score < 50:
        user_percentile = 'below_average'
    
    benchmark = benchmarks[user_percentile]
    
    improvements = []
    if ats_score < benchmark['ats_score']:
        improvements.append(f"Improve ATS score from {ats_score} to {benchmark['ats_score']}")
    if len(skills) < benchmark['skills_count']:
        improvements.append(f"Add {benchmark['skills_count'] - len(skills)} more skills")
    
    return {
        "percentile": user_percentile,
        "percentile_rank": {'top_10_percent': 90, 'top_25_percent': 75, 'average': 50, 'below_average': 25}[user_percentile],
        "benchmark": benchmark,
        "improvements": improvements
    }


def career_path_recommendations(skills, job_fit):
    """Generate career path recommendations based on current skills."""
    career_paths = {
        'Software Engineer': {
            'next_steps': ['Master system design', 'Learn microservices architecture', 'Contribute to open source'],
            'skills_to_add': ['Go', 'Rust', 'Kubernetes'],
            'projects': ['Build distributed system', 'Contribute to major open source project']
        },
        'Data Scientist': {
            'next_steps': ['Master deep learning frameworks', 'Publish research papers', 'Build end-to-end ML pipeline'],
            'skills_to_add': ['PyTorch', 'Advanced SQL', 'MLOps'],
            'projects': ['Kaggle competition', 'NLP project', 'Computer vision project']
        },
        'DevOps Engineer': {
            'next_steps': ['Master Kubernetes orchestration', 'Learn IaC tools', 'Setup CI/CD pipelines'],
            'skills_to_add': ['Terraform', 'Ansible', 'Prometheus'],
            'projects': ['Design scalable infrastructure', 'Automate deployments']
        }
    }
    
    best_role = max(job_fit, key=job_fit.get) if job_fit else 'Software Engineer'
    path = career_paths.get(best_role, career_paths['Software Engineer'])
    
    return {
        'current_best_fit': best_role,
        'next_steps': path['next_steps'],
        'skills_to_add': path['skills_to_add'],
        'projects_to_build': path['projects']
    }


def check_resume_consistency(resume_text):
    """Detect contradictions and inconsistencies in the resume."""
    inconsistencies = []
    lower = resume_text.lower()
    
    # Check experience claims vs project count
    years_match = re.search(r'(\d+)\s*(?:years?|yrs?)', lower)
    projects = len(re.findall(r'(?:project|built|developed)', lower))
    
    if years_match:
        years = int(years_match.group(1))
        if years >= 5 and projects < 2:
            inconsistencies.append({
                'type': 'warning',
                'message': f'Claims {years} years experience but only {projects} projects mentioned. Add more project descriptions.'
            })
    
    # Check skill level claims
    if 'expert' in lower and 'beginner' in lower:
        inconsistencies.append({
            'type': 'warning',
            'message': 'Resume claims both expert and beginner levels. Clarify skill levels.'
        })
    
    # Check company/role consistency
    companies = len(re.findall(r'(?:worked at|at|company:|employer:)', lower))
    roles = len(re.findall(r'(?:engineer|developer|analyst|manager|specialist)', lower))
    
    if companies > 0 and roles < companies:
        inconsistencies.append({
            'type': 'info',
            'message': f'{companies} companies mentioned but only {roles} role titles. Add specific role descriptions.'
        })
    
    # Check education consistency
    degrees = len(re.findall(r'\b(bachelor|master|phd|diploma)\b', lower))
    universities = len(re.findall(r'\b(university|college|institute)\b', lower))
    
    if degrees > universities:
        inconsistencies.append({
            'type': 'info',
            'message': f'{degrees} degrees mentioned but only {universities} institutions. List all universities.'
        })
    
    if not inconsistencies:
        inconsistencies.append({'type': 'success', 'message': 'Resume appears consistent with no major contradictions.'})
    
    return inconsistencies


def analyze_skill_context(resume_text, skills):
    """Analyze skill usage context - are skills just listed or actually used?"""
    skill_analysis = []
    
    for skill in skills[:15]:  # Analyze top 15 skills
        skill_lower = skill.lower()
        
        # Check if skill appears in project/experience context
        project_context = bool(re.search(rf'{skill_lower}.*(?:built|developed|created|implemented)', resume_text, re.IGNORECASE))
        achievement_context = bool(re.search(rf'(?:using|with).*{skill_lower}.*(?:\d+%|\d+x|improved|increased)', resume_text, re.IGNORECASE))
        multiple_mentions = len(re.findall(rf'\b{skill_lower}\b', resume_text, re.IGNORECASE)) > 1
        
        strength = 'Strong'
        reason = 'Used in projects with measurable impact'
        
        if not (project_context or achievement_context):
            strength = 'Listed only'
            reason = 'Skill listed but no project context'
        elif project_context and not achievement_context:
            strength = 'Moderate'
            reason = 'Used in projects but no metrics'
        
        skill_analysis.append({
            'skill': skill,
            'strength': strength,
            'context_usage': project_context or achievement_context,
            'reason': reason,
            'mentions': multiple_mentions
        })
    
    strong_count = sum(1 for s in skill_analysis if s['strength'] == 'Strong')
    weak_count = sum(1 for s in skill_analysis if s['strength'] == 'Listed only')
    
    return {
        'analysis': skill_analysis,
        'strong_skills': strong_count,
        'weak_skills': weak_count,
        'recommendation': f'Strengthen {weak_count} skills by adding project context and measurable outcomes.'
    }


def generate_mock_interview_questions(resume_text, skills):
    """Generate dynamic mock interview questions based on resume content."""
    questions = []
    lower = resume_text.lower()
    
    # Technical questions based on top skills
    for skill in skills[:3]:
        skill_lower = skill.lower()
        if skill_lower in ['python', 'java', 'javascript', 'golang', 'rust', 'c++']:
            questions.append({
                'type': 'Technical',
                'difficulty': 'Hard',
                'question': f'Describe a complex {skill} project you built. How did you optimize performance?',
                'focus': 'Technical depth and optimization'
            })
        elif skill_lower in ['tensorflow', 'pytorch', 'scikit-learn', 'machine learning']:
            questions.append({
                'type': 'Technical',
                'difficulty': 'Hard',
                'question': f'Walk me through a {skill} model you implemented. How did you prevent overfitting?',
                'focus': 'ML/AI expertise'
            })
    
    # Behavioral questions
    if 'led' in lower or 'managed' in lower or 'team' in lower:
        questions.append({
            'type': 'Behavioral',
            'difficulty': 'Medium',
            'question': 'Tell me about a time you led a project that failed. What did you learn?',
            'focus': 'Leadership and failure handling'
        })
    
    if re.search(r'\d+%|\d+x', lower):
        questions.append({
            'type': 'Behavioral',
            'difficulty': 'Medium',
            'question': 'You mentioned achieving metrics like this. Walk me through your approach.',
            'focus': 'Impact and results'
        })
    
    # HR questions
    questions.append({
        'type': 'HR',
        'difficulty': 'Easy',
        'question': 'Why are you interested in this role and our company?',
        'focus': 'Motivation'
    })
    
    questions.append({
        'type': 'HR',
        'difficulty': 'Medium',
        'question': 'Describe a situation where you had to learn something new quickly.',
        'focus': 'Learning ability'
    })
    
    return questions


def track_resume_improvements(versions):
    """Track resume improvement timeline across versions."""
    if not versions:
        return {'timeline': [], 'total_improvement': 0}
    
    timeline = []
    for i, version in enumerate(versions, 1):
        timeline.append({
            'version': i,
            'ats_score': version.get('ats_score', 0),
            'skills': len(version.get('skills', [])),
            'improvement_from_previous': version.get('ats_score', 0) - (versions[i-2].get('ats_score', 0) if i > 1 else 0)
        })
    
    total_improvement = timeline[-1]['ats_score'] - timeline[0]['ats_score'] if timeline else 0
    
    return {
        'timeline': timeline,
        'total_improvement': total_improvement,
        'average_improvement_per_version': total_improvement / len(versions) if versions else 0
    }


def recruiter_simulation(resume_text, ats_score):
    """Simulate recruiter's 6-second resume scan with first impressions."""
    impressions = []
    lower = resume_text.lower()
    first_100_chars = resume_text[:150]
    
    # Check summary/objective
    if re.search(r'summary|objective|professional|profile', lower):
        if len(re.search(r'summary|objective|professional|profile', lower).group(0)) > 0:
            impressions.append({'element': 'Opening', 'impression': '✅ Strong', 'note': 'Clear summary/objective found'})
        else:
            impressions.append({'element': 'Opening', 'impression': '❌ Weak', 'note': 'No clear opening statement'})
    
    # Check skills visibility
    skills_visible = len(re.findall(r'\b(python|java|aws|react|docker|kubernetes)\b', first_100_chars, re.IGNORECASE)) > 0
    impressions.append({
        'element': 'Skills Visibility',
        'impression': '✅ Strong' if skills_visible else '⚠️ Moderate',
        'note': 'Technical skills visible in opening' if skills_visible else 'Add key skills to opening'
    })
    
    # Check formatting
    has_structure = len(re.findall(r'[-*•]', resume_text[:300])) >= 2
    impressions.append({
        'element': 'Formatting',
        'impression': '✅ Strong' if has_structure else '❌ Weak',
        'note': 'Well-structured with bullets' if has_structure else 'Use bullet points for clarity'
    })
    
    # Check ATS compatibility
    impressions.append({
        'element': 'ATS Score',
        'impression': '✅ Strong' if ats_score >= 70 else '⚠️ Moderate' if ats_score >= 50 else '❌ Weak',
        'note': f'ATS Score: {ats_score}/100'
    })
    
    return impressions


def resume_pdf_export_ready(resume_text, ats_score):
    """Check if resume is export-ready with all best practices."""
    export_checklist = []
    lower = resume_text.lower()
    
    checks = {
        'Contact Info': bool(re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', resume_text)),
        'Professional Summary': bool(re.search(r'summary|objective|profile', lower)),
        'Experience Section': bool(re.search(r'experience|work|employment', lower)),
        'Skills Section': bool(re.search(r'skills?', lower)),
        'Education': bool(re.search(r'education|degree|bachelor|master', lower)),
        'High ATS Score': ats_score >= 70,
        'Action Verbs': len(re.findall(r'\b(led|managed|developed|created|designed)\b', lower)) >= 3,
        'Quantified Metrics': len(re.findall(r'\d+%|\d+x|\d+\s*million', lower)) >= 2
    }
    
    for check, status in checks.items():
        export_checklist.append({'item': check, 'ready': status})
    
    readiness_score = int((sum(1 for c in export_checklist if c['ready']) / len(export_checklist)) * 100)
    
    return {
        'checklist': export_checklist,
        'readiness_score': readiness_score,
        'is_export_ready': readiness_score >= 75
    }


def analyze_experience(text):
    """Analyze professional experience"""
    sentences = sent_tokenize(text)
    
    # Look for job titles and company names
    job_titles = []
    companies = []
    
    job_keywords = ['software engineer', 'developer', 'analyst', 'manager', 'specialist', 'consultant', 'architect', 'lead', 'senior']
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        for job_keyword in job_keywords:
            if job_keyword in sentence_lower:
                job_titles.append(job_keyword.title())
                break
    
    # Extract years of experience
    experience_pattern = r'(\d+)\+?\s*(?:years?|yrs?)'
    experience_matches = re.findall(experience_pattern, text.lower())
    
    if experience_matches:
        total_years = max(int(y) for y in experience_matches)
        exp_summary = f"Approximately {total_years}+ years of professional experience in roles including {', '.join(set(job_titles[:3]))}"
    else:
        exp_summary = "Professional experience in roles including " + ", ".join(set(job_titles[:3])) if job_titles else "Professional experience details extracted from resume"
    
    return exp_summary 
def identify_strengths(text, skills, ats_score):
    """Identify resume strengths"""
    strengths = []
    
    if ats_score >= 70:
        strengths.append("Strong ATS optimization with good keyword density")
    
    if len(skills) >= 10:
        strengths.append(f"Comprehensive skill set with {len(skills)} technical skills identified")
    
    if len(re.findall(r'\d+%|\d+\s*(increased|decreased|improved)', text.lower())) >= 3:
        strengths.append("Good use of quantifiable metrics and achievements")
    
    if len(re.findall(r'led|managed|developed|designed', text.lower())) >= 5:
        strengths.append("Strong action verbs demonstrating leadership and initiative")
    
    if re.search(r'(bachelor|master|phd|certificate|certification)', text.lower()):
        strengths.append("Clear educational background and certifications listed")
    
    if not strengths:
        strengths.append("Resume structure and basic information are present")
    
    return strengths

def identify_weaknesses(text, skills):
    """Identify areas for improvement"""
    weaknesses = []
    
    if len(skills) < 5:
        weaknesses.append("Limited technical skills mentioned - add more specific skills")
    
    if len(re.findall(r'\d+%|\d+\s*(increased|decreased|improved)', text.lower())) < 3:
        weaknesses.append("Lack of quantifiable metrics - add numbers and percentages to achievements")
    
    if len(re.findall(r'led|managed|developed|designed|created', text.lower())) < 3:
        weaknesses.append("Limited use of strong action verbs - use more impactful language")
    
    if len(text) < 300:
        weaknesses.append("Resume seems brief - consider adding more details and achievements")
    
    if not re.search(r'@|email|contact', text.lower()):
        weaknesses.append("Missing contact information - ensure email is clearly visible")
    
    if not re.search(r'(bachelor|master|phd|certificate)', text.lower()):
        weaknesses.append("Educational background not clearly listed")
    
    return weaknesses[:5]  # Return top 5 weaknesses

def generate_suggestions(text, ats_score, skills):
    """Generate actionable suggestions"""
    suggestions = []
    
    if ats_score < 60:
        suggestions.append("Include more industry-specific keywords and technical terminology")
    
    if len(skills) < 8:
        suggestions.append("Add a dedicated 'Skills' section with 8-10 relevant technical competencies")
    
    if len(re.findall(r'increased|improved|decreased|grew', text.lower())) == 0:
        suggestions.append("Quantify your achievements with percentages and metrics (e.g., 'improved by 25%')")
    
    if len(text) < 500:
        suggestions.append("Expand experience descriptions with specific projects and measurable outcomes")
    
    if not re.search(r'linkedin|github|portfolio', text.lower()):
        suggestions.append("Add links to LinkedIn, GitHub, or portfolio for better visibility")
    
    if len(re.findall(r'certification|certified|aws|gcp|azure', text.lower())) == 0:
        suggestions.append("Highlight relevant certifications and credentials")
    
    suggestions.append("Use a consistent format and clear hierarchy with section headers")
    
    return suggestions[:6]  # Return top 6 suggestions

def analyze_job_fit(text, skills):
    """Analyze fit for different job roles"""
    job_roles = {
        'Software Engineer': ['python', 'java', 'javascript', 'c++', 'api', 'database', 'git'],
        'Data Scientist': ['python', 'pandas', 'scikit-learn', 'tensorflow', 'sql', 'analysis', 'ml'],
        'DevOps Engineer': ['docker', 'kubernetes', 'aws', 'ci/cd', 'linux', 'terraform', 'jenkins'],
        'Full Stack Developer': ['javascript', 'react', 'node', 'sql', 'api', 'css', 'html'],
        'Product Manager': ['leadership', 'agile', 'roadmap', 'stakeholder', 'analytics', 'strategy'],
        'QA Engineer': ['testing', 'automation', 'selenium', 'api', 'debugging', 'junit']
    }
    
    text_lower = text.lower()
    job_fit = {}
    
    for role, keywords in job_roles.items():
        matching_keywords = sum(1 for keyword in keywords if keyword in text_lower)
        fit_score = int((matching_keywords / len(keywords)) * 100)
        job_fit[role] = min(fit_score, 100)
    
    return job_fit

def analyze_resume_with_ml(resume_text, job_description=""):
    """Comprehensive resume analysis using ML/NLP with BERT and spaCy"""
    try:
        # Load NLP models
        nlp = load_spacy_model()
        classifier = load_bert_classifier()
        
        # Extract skills
        skills = extract_skills(resume_text)
        
        # Calculate ATS score
        ats_score = calculate_ats_score(resume_text)
        
        # Enhanced experience detection using spaCy
        experience_data = detect_experience(resume_text, nlp)
        
        # Enhanced education detection
        education_entries = detect_education(resume_text, nlp)
        
        # BERT-based analysis
        bert_analysis = analyze_text_with_bert(resume_text, classifier)
        
        # Identify strengths and weaknesses
        strengths = identify_strengths(resume_text, skills, ats_score)
        weaknesses = identify_weaknesses(resume_text, skills)
        
        # Generate suggestions
        suggestions = generate_suggestions(resume_text, ats_score, skills)
        
        # Job fit analysis
        job_fit = analyze_job_fit(resume_text, skills)
        
        # Highlight keywords
        highlighted_text = highlight_keywords(resume_text, skills)
        
        # Advanced feature outputs
        rewritten_resume = rewrite_resume_text(resume_text)
        formatting_score, formatting_issues = evaluate_resume_formatting(resume_text)
        exaggeration_flags = detect_exaggeration(resume_text)
        github_data = analyze_github_and_linkedin(resume_text)
        personality_insights = analyze_personality_insights(resume_text)
        semantic_overview = semantic_resume_overview(resume_text)
        heatmap_data = build_resume_heatmap_data(resume_text, skills)
        learning_path = generate_skill_gap_and_learning_path(skills, job_fit)
        
        # New advanced features
        ai_feedback = generate_ai_feedback(resume_text, ats_score, skills, experience_data)
        multi_role_analysis = detailed_multi_role_analysis(resume_text, skills, ats_score)
        interview_questions = generate_interview_questions(resume_text)
        
        # MUST-ADD Features
        tailored_resume = tailor_resume_for_job(resume_text, job_description)
        explainable_match = explainable_job_match(resume_text, job_description, skills, ats_score)
        section_scores = score_resume_sections(resume_text)
        
        # ADVANCED Features
        project_analysis = analyze_project_impact(resume_text)
        benchmark = compare_with_benchmark(skills, ats_score, experience_data.get('years', 0) if experience_data else 0)
        career_path = career_path_recommendations(skills, job_fit)
        
        # UNIQUE Features
        consistency = check_resume_consistency(resume_text)
        skill_context = analyze_skill_context(resume_text, skills)
        mock_interview = generate_mock_interview_questions(resume_text, skills)
        export_ready = resume_pdf_export_ready(resume_text, ats_score)
        recruiter_sim = recruiter_simulation(resume_text, ats_score)
        
        analysis = {
            'ats_score': ats_score,
            'skills_found': skills,
            'experience_data': experience_data,
            'education': education_entries,
            'bert_analysis': bert_analysis,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions,
            'job_fit_analysis': job_fit,
            'highlighted_text': highlighted_text,
            'rewritten_resume': rewritten_resume,
            'formatting_score': formatting_score,
            'formatting_issues': formatting_issues,
            'exaggeration_flags': exaggeration_flags,
            'github_data': github_data,
            'personality_insights': personality_insights,
            'semantic_overview': semantic_overview,
            'heatmap_data': heatmap_data,
            'learning_path': learning_path,
            'ai_feedback': ai_feedback,
            'multi_role_analysis': multi_role_analysis,
            'interview_questions': interview_questions,
            'tailored_resume': tailored_resume,
            'explainable_match': explainable_match,
            'section_scores': section_scores,
            'project_analysis': project_analysis,
            'benchmark': benchmark,
            'career_path': career_path,
            'consistency': consistency,
            'skill_context': skill_context,
            'mock_interview': mock_interview,
            'export_ready': export_ready,
            'recruiter_sim': recruiter_sim
        }

        
        return analysis
    
    except Exception as e:
        st.error(f"Error analyzing resume: {e}")
        return None

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📤 Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a resume file (PDF or TXT)",
        type=["pdf", "txt"],
        help="Upload your resume in PDF or TXT format"
    )

with col2:
    st.subheader("🔍 Analysis Options")
    st.info("✅ Ready to analyze - no API key needed!")

# Process resume
if uploaded_file:
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    
    # Extract text from uploaded file
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = extract_text_from_txt(uploaded_file)
    
    if resume_text:
        with st.expander("📝 Preview Resume Text", expanded=False):
            st.text_area("Resume Content:", resume_text, height=150, disabled=True)
        
        # Job description input for tailoring
        st.subheader("💼 Optional: Paste Job Description")
        st.text_area(
            "Paste job description for resume tailoring and match analysis",
            key='job_description',
            height=120,
            placeholder="Example: We are looking for a Senior Python Developer with AWS experience..."
        )
        
        # Analyze button
        if st.button("🔍 Analyze Resume", use_container_width=True, type="primary"):
            with st.spinner("🤖 Analyzing your resume..."):
                analysis = analyze_resume_with_ml(resume_text, st.session_state.job_description)
            
            if analysis:
                # Display Results
                st.markdown("---")
                st.markdown("## 📊 Analysis Results")
                
                # ATS Score
                col1, col2, col3 = st.columns(3)
                with col1:
                    ats_score = analysis.get('ats_score', 0)
                    st.metric("ATS Score", f"{ats_score}/100", 
                             delta="Good" if ats_score >= 70 else "Needs improvement")
                
                with col2:
                    skills_count = len(analysis.get('skills_found', []))
                    st.metric("Skills Identified", skills_count)
                
                with col3:
                    suggestions_count = len(analysis.get('suggestions', []))
                    st.metric("Improvement Tips", suggestions_count)
                
                st.markdown("---")
                st.subheader("🧠 Smart Dashboard")
                dash_col1, dash_col2, dash_col3, dash_col4 = st.columns(4)
                with dash_col1:
                    st.metric("Formatting Score", analysis.get('formatting_score', 0))
                with dash_col2:
                    st.metric("Best Role Fit", analysis.get('learning_path', {}).get('target_role', 'N/A'))
                with dash_col3:
                    has_profile = analysis.get('github_data', {}).get('github') or analysis.get('github_data', {}).get('linkedin')
                    st.metric("GitHub/LinkedIn", "Yes" if has_profile else "No")
                with dash_col4:
                    st.metric("Semantic Sections", len(analysis.get('semantic_overview', {}).get('detected_sections', [])))
                
                st.markdown("---")
                
                # Skills Found
                st.subheader("💼 Skills Identified")
                skills = analysis.get('skills_found', [])
                if skills:
                    skill_html = ""
                    for skill in skills[:20]:  # Show top 20 skills
                        skill_html += f"<span class='skill-badge'>{skill}</span>"
                    st.markdown(skill_html, unsafe_allow_html=True)
                else:
                    st.info("No specific skills extracted.")
                
                # Education Detection
                st.subheader("🎓 Education Detected")
                education = analysis.get('education', [])
                if education:
                    for edu in education:
                        st.markdown(f"<div class='entity-box'><strong>{edu}</strong></div>", unsafe_allow_html=True)
                else:
                    st.info("No education information detected.")
                
                # Experience Detection
                st.subheader("💼 Experience Detected")
                experience_data = analysis.get('experience_data', {})
                if experience_data:
                    positions = experience_data.get('positions', [])
                    orgs = experience_data.get('organizations', [])
                    years = experience_data.get('years', 0)
                    
                    col_exp1, col_exp2, col_exp3 = st.columns(3)
                    with col_exp1:
                        st.metric("Years of Experience", years)
                    with col_exp2:
                        st.metric("Positions Found", len(positions))
                    with col_exp3:
                        st.metric("Organizations", len(orgs))
                    
                    if positions:
                        st.markdown("**Job Positions:**")
                        for pos in positions:
                            st.markdown(f"<div class='entity-box'>{pos}</div>", unsafe_allow_html=True)
                    
                    if orgs:
                        st.markdown("**Organizations:**")
                        for org in orgs:
                            st.markdown(f"<div class='entity-box'>{org}</div>", unsafe_allow_html=True)
                
                # BERT Analysis
                bert_analysis = analysis.get('bert_analysis', {})
                if bert_analysis:
                    st.subheader("🤖 AI-Powered Analysis (BERT)")
                    bert_cols = st.columns(2)
                    for idx, (aspect, score) in enumerate(bert_analysis.items()):
                        with bert_cols[idx % 2]:
                            st.metric(aspect.title(), f"{score:.1f}%")
                
                st.markdown("---")
                st.subheader("✍️ AI Resume Rewriter")
                st.write("Improve your resume language with action-oriented revisions.")
                st.text_area("Rewritten Resume Preview", analysis.get('rewritten_resume', ''), height=180, disabled=True)

                st.markdown("---")
                st.subheader("📚 Skill Gap + Learning Path Generator")
                learning_path = analysis.get('learning_path', {})
                st.write(f"**Target Role:** {learning_path.get('target_role', 'N/A')}")
                if learning_path.get('missing_skills'):
                    st.write("**Missing Skills:** " + ', '.join(learning_path.get('missing_skills', [])))
                for i, tip in enumerate(learning_path.get('learning_path', []), 1):
                    st.info(f"{i}. {tip}")

                st.markdown("---")
                st.subheader("🧾 ATS Resume Formatter Checker")
                st.metric("Formatting Score", analysis.get('formatting_score', 0))
                for issue in analysis.get('formatting_issues', []):
                    st.warning(issue)

                st.markdown("---")
                st.subheader("🕵️ Fake/Exaggeration Detection")
                for flag in analysis.get('exaggeration_flags', []):
                    if 'No major' in flag:
                        st.success(flag)
                    else:
                        st.warning(flag)

                st.markdown("---")
                st.subheader("💻 GitHub + Project Analyzer")
                github_data = analysis.get('github_data', {})
                if github_data.get('github'):
                    st.markdown(f"**GitHub:** {github_data.get('github')}")
                if github_data.get('linkedin'):
                    st.markdown(f"**LinkedIn:** {github_data.get('linkedin')}")
                if github_data.get('portfolio'):
                    st.markdown(f"**Portfolio:** {github_data.get('portfolio')}")
                if not any([github_data.get('github'), github_data.get('linkedin'), github_data.get('portfolio')]):
                    st.info('No GitHub, LinkedIn, or portfolio link detected.')

                st.markdown("---")
                st.subheader("🌍 LinkedIn Profile Analyzer")
                if github_data.get('linkedin'):
                    st.success('LinkedIn profile detected. Great for recruiter reach.')
                else:
                    st.info('Add a LinkedIn profile to improve discoverability.')

                st.markdown("---")
                st.subheader("🔬 Deep Resume Analysis")
                semantic = analysis.get('semantic_overview', {})
                st.write(semantic.get('overview', ''))
                if semantic.get('missing_sections'):
                    st.warning('Missing sections: ' + ', '.join(semantic.get('missing_sections', [])))

                heatmap_data = analysis.get('heatmap_data', {})
                if heatmap_data:
                    st.bar_chart(pd.Series(heatmap_data))

                st.markdown("---")
                st.subheader("🧠 Personality Insights")
                personality_insights = analysis.get('personality_insights', {})
                if personality_insights:
                    pi_cols = st.columns(len(personality_insights))
                    for idx, (trait, score) in enumerate(personality_insights.items()):
                        with pi_cols[idx]:
                            st.metric(trait, f"{score}%")

                st.markdown("---")
                st.subheader("🔮 What-If Resume Simulator")
                st.text_area(
                    "Add a hypothetical skill, achievement, or project to simulate ATS impact",
                    key='what_if_input',
                    height=120,
                    placeholder="Example: Built a data pipeline using Python and AWS, improving query speed by 35%"
                )

                if st.button("Run What-If Simulation", key="what_if_sim"):
                    if st.session_state.what_if_input.strip():
                        st.session_state.what_if_result = run_what_if_simulation(resume_text, st.session_state.what_if_input)
                    else:
                        st.info('Enter a short resume update or achievement description to simulate impact.')

                simulation = st.session_state.get('what_if_result')
                if simulation:
                    st.metric('Current ATS Score', f"{simulation['original_score']}/100")
                    st.metric('Simulated ATS Score', f"{simulation['new_score']}/100")

                    delta = simulation['delta']
                    if delta > 0:
                        st.success(f"Estimated gain: +{delta} points. This update helps your ATS score.")
                    elif delta < 0:
                        st.warning(f"Estimated change: {delta} points. Try stronger achievements or clearer keywords.")
                    else:
                        st.info('No ATS score change detected. Add quantifiable metrics or more role-specific keywords.')

                    if simulation['added_skills']:
                        st.write(f"**Skills added:** {', '.join(simulation['added_skills'])}")

                    if simulation['changed_sections']:
                        st.write(f"**Potential section improvements:** {', '.join(simulation['changed_sections'])}")

                    if simulation['suggestions']:
                        st.write("**Quick improvement tips:**")
                        for suggestion in simulation['suggestions']:
                            st.info(suggestion)

                    st.markdown("**Simulated Resume Preview**")
                    st.text_area("Updated resume with your added text:", simulation['simulated_text'], height=140, disabled=True)

                st.markdown("---")
                st.subheader("💬 AI Feedback Generator")
                st.write("Comprehensive AI-powered recommendations for your resume:")
                ai_feedback = analysis.get('ai_feedback', [])
                for feedback_item in ai_feedback:
                    if feedback_item.get('type') == 'critical':
                        st.error(f"**{feedback_item.get('title')}**\n{feedback_item.get('message')}\n\n*Action:* {feedback_item.get('action')}")
                    elif feedback_item.get('type') == 'warning':
                        st.warning(f"**{feedback_item.get('title')}**\n{feedback_item.get('message')}\n\n*Action:* {feedback_item.get('action')}")
                    elif feedback_item.get('type') == 'success':
                        st.success(f"**{feedback_item.get('title')}**\n{feedback_item.get('message')}\n\n*Action:* {feedback_item.get('action')}")
                    else:
                        st.info(f"**{feedback_item.get('title')}**\n{feedback_item.get('message')}\n\n*Action:* {feedback_item.get('action')}")

                st.markdown("---")
                st.subheader("🎯 Multi-Role Fit Analysis")
                st.write("Detailed role alignment with actionable recommendations:")
                multi_role = analysis.get('multi_role_analysis', {})
                
                # Create data for visualization
                role_names = list(multi_role.keys())
                fit_scores = [multi_role[role].get('fit_percentage', 0) for role in role_names]
                
                # Display chart
                role_data = pd.DataFrame({
                    'Role': role_names,
                    'Fit %': fit_scores
                })
                st.bar_chart(role_data.set_index('Role'))
                
                # Detailed analysis for each role
                with st.expander("📊 Detailed Role Analysis", expanded=False):
                    for role, details in multi_role.items():
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.subheader(f"{role}")
                            st.write(f"**Fit Score:** {details.get('fit_percentage', 0)}%")
                            st.write(f"**Recommendation:** {details.get('recommendation', '')}")
                            
                            if details.get('matched_keywords'):
                                st.write(f"**Matched Skills:** {', '.join(details.get('matched_keywords', []))}")
                            
                            if details.get('missing_keywords'):
                                missing = ', '.join(details.get('missing_keywords', []))
                                st.write(f"**Missing Skills:** {missing}")
                        
                        with col2:
                            ats_gap = details.get('ats_gap', 0)
                            if ats_gap > 0:
                                st.warning(f"ATS Gap: +{ats_gap} points to optimize")
                            elif ats_gap < 0:
                                st.success(f"Exceeds target by {abs(ats_gap)} points")
                            else:
                                st.success("Perfectly aligned")

                st.markdown("---")
                st.subheader("🎤 Interview Question Generator")
                st.write("Role-specific interview questions to help you prepare:")
                interview_questions = analysis.get('interview_questions', [])
                
                # Group questions by category
                question_categories = {}
                for q in interview_questions:
                    category = q.get('category', 'Other')
                    if category not in question_categories:
                        question_categories[category] = []
                    question_categories[category].append(q)
                
                for category, questions in question_categories.items():
                    with st.expander(f"📌 {category} Questions", expanded=True if category == 'General' else False):
                        for idx, q in enumerate(questions, 1):
                            st.write(f"**Q{idx}: {q.get('question', '')}**")
                            st.caption(f"Focus Area: {q.get('focus', '')}")

                st.markdown("---")
                st.subheader("🎯 Resume Tailoring Engine (Based on Job Description)")
                if st.session_state.job_description:
                    tailored = analysis.get('tailored_resume', {})
                    st.write("**Tailored Resume:**")
                    st.text_area("Optimized resume bullets for job fit", tailored.get('tailored_resume', ''), height=150, disabled=True)
                    if tailored.get('improvements'):
                        st.write("**Improvements Made:**")
                        for improvement in tailored.get('improvements', []):
                            st.success(improvement)
                else:
                    st.info("Paste a job description above to generate tailored resume suggestions.")

                st.markdown("---")
                st.subheader("📊 Explainable Job Match (Why This Score?)")
                if st.session_state.job_description:
                    match_data = analysis.get('explainable_match', {})
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.metric("Match Score", f"{match_data.get('score', 0)}%")
                    with col2:
                        st.write("**Reasoning:**")
                        for reason in match_data.get('reasons', []):
                            if reason.startswith('✅'):
                                st.success(reason)
                            elif reason.startswith('❌'):
                                st.error(reason)
                            else:
                                st.info(reason)
                else:
                    st.info("Paste a job description to see explainable job match analysis.")

                st.subheader("📈 Resume Section Quality Scoring")
                section_scores = analysis.get('section_scores', {})
                if section_scores:
                    score_df = pd.DataFrame(list(section_scores.items()), columns=['Section', 'Score'])
                    st.bar_chart(score_df.set_index('Section'))
                    
                    for section, score in section_scores.items():
                        col = st.columns(4)[list(section_scores.keys()).index(section) % 4]
                        with col:
                            st.metric(section.capitalize(), score)

                st.markdown("---")
                st.subheader("💡 Project Impact Analyzer")
                project_analysis = analysis.get('project_analysis', {})
                if project_analysis.get('projects'):
                    st.write(f"**Overall Project Score:** {project_analysis.get('overall_score', 0)}/100")
                    st.write(f"**Strong Projects:** {project_analysis.get('strong_count', 0)} | **Weak Projects:** {project_analysis.get('weak_count', 0)}")
                    
                    with st.expander("📌 Detailed Project Analysis", expanded=False):
                        for proj in project_analysis.get('projects', []):
                            color = '🟢' if proj['strength'] == 'Strong' else '🟡' if proj['strength'] == 'Moderate' else '🔴'
                            st.write(f"{color} **{proj['strength']}** (Impact: {proj['impact_score']}/100)")
                            st.write(f"Tech Depth: {proj['tech_depth']} | Metrics Found: {proj['metrics_found']}")
                            st.caption(proj['description'])

                st.markdown("---")
                st.subheader("🏆 Resume vs Top Candidates Benchmark")
                benchmark = analysis.get('benchmark', {})
                st.metric("Your Percentile", f"{benchmark.get('percentile_rank', 0)}th %")
                st.write(f"**Category:** {benchmark.get('percentile', 'Average').title()}")
                for improvement in benchmark.get('improvements', [])[:3]:
                    st.info(improvement)

                st.markdown("---")
                st.subheader("🚀 Career Path Recommendation")
                career = analysis.get('career_path', {})
                st.write(f"**Best Role Fit:** {career.get('current_best_fit', 'N/A')}")
                st.write("**Next Career Steps:**")
                for i, step in enumerate(career.get('next_steps', []), 1):
                    st.write(f"{i}. {step}")
                st.write("**Skills to Add:**")
                st.write(", ".join(career.get('skills_to_add', [])))

                st.markdown("---")
                st.subheader("🔍 Resume Consistency Checker")
                consistency = analysis.get('consistency', [])
                for check in consistency:
                    if check.get('type') == 'success':
                        st.success(check.get('message', ''))
                    elif check.get('type') == 'warning':
                        st.warning(check.get('message', ''))
                    else:
                        st.info(check.get('message', ''))

                st.markdown("---")
                st.subheader("🎯 Skill Context Analyzer")
                skill_ctx = analysis.get('skill_context', {})
                st.write(f"**Strong Skills (with context):** {skill_ctx.get('strong_skills', 0)}")
                st.write(f"**Listed Only Skills:** {skill_ctx.get('weak_skills', 0)}")
                st.info(skill_ctx.get('recommendation', ''))
                
                with st.expander("📊 Skill Strength Breakdown", expanded=False):
                    for skill_info in skill_ctx.get('analysis', [])[:10]:
                        strength_icon = '💪' if skill_info['strength'] == 'Strong' else '⚠️'
                        st.write(f"{strength_icon} **{skill_info['skill']}**: {skill_info['strength']} - {skill_info['reason']}")

                st.markdown("---")
                st.subheader("🎤 AI Mock Interview Questions")
                mock_questions = analysis.get('mock_interview', [])
                question_types = {}
                for q in mock_questions:
                    q_type = q.get('type', 'Other')
                    if q_type not in question_types:
                        question_types[q_type] = []
                    question_types[q_type].append(q)
                
                for q_type, questions in question_types.items():
                    with st.expander(f"❓ {q_type} Questions", expanded=False):
                        for i, q in enumerate(questions, 1):
                            st.write(f"**Q{i}: {q.get('question', '')}**")
                            st.write(f"📍 Focus: {q.get('focus', '')} | Difficulty: {q.get('difficulty', '')}")

                st.markdown("---")
                st.subheader("📋 Recruiter's 6-Second Scan Simulation")
                recruiter_sim = analysis.get('recruiter_sim', [])
                for impression in recruiter_sim:
                    element = impression.get('element', '')
                    imp = impression.get('impression', '')
                    note = impression.get('note', '')
                    
                    if '✅' in imp:
                        st.success(f"**{element}:** {imp} - {note}")
                    elif '❌' in imp:
                        st.error(f"**{element}:** {imp} - {note}")
                    else:
                        st.warning(f"**{element}:** {imp} - {note}")

                st.markdown("---")
                st.subheader("✅ Export Readiness Checklist")
                export = analysis.get('export_ready', {})
                st.metric("Export Readiness", f"{export.get('readiness_score', 0)}%")
                
                for item in export.get('checklist', []):
                    status = '✅' if item['ready'] else '❌'
                    st.write(f"{status} {item['item']}")
                
                if export.get('is_export_ready'):
                    st.success("Your resume is ready to export!")
                else:
                    st.warning("Complete the checklist before exporting.")

                st.markdown("---")
                st.subheader("✨ Strengths")
                strengths = analysis.get('strengths', [])
                for i, strength in enumerate(strengths, 1):
                    st.success(f"**{i}. {strength}**")
                
                # Weaknesses
                st.subheader("⚠️ Areas for Improvement")
                weaknesses = analysis.get('weaknesses', [])
                for i, weakness in enumerate(weaknesses, 1):
                    st.warning(f"**{i}. {weakness}**")
                
                # Suggestions
                st.subheader("💡 Actionable Suggestions")
                suggestions = analysis.get('suggestions', [])
                for i, suggestion in enumerate(suggestions, 1):
                    st.info(f"**{i}. {suggestion}**")
                
                # Job Fit Analysis
                st.subheader("🎯 Job Fit Analysis")
                job_fit = analysis.get('job_fit_analysis', {})
                if job_fit:
                    fit_cols = st.columns(2)
                    for idx, (job_role, fit_score) in enumerate(job_fit.items()):
                        with fit_cols[idx % 2]:
                            st.write(f"**{job_role}: {fit_score}%**")
                            st.progress(min(fit_score / 100, 1.0))
                
                # Statistics
                st.markdown("---")
                st.subheader("📈 Resume Statistics")
                
                stats_col1, stats_col2, stats_col3 = st.columns(3)
                
                with stats_col1:
                    st.metric("Total Characters", f"{len(resume_text)}")
                
                with stats_col2:
                    word_count = len(resume_text.split())
                    st.metric("Word Count", word_count)
                
                with stats_col3:
                    action_verbs = len(re.findall(r'\b(led|managed|developed|created|designed|implemented)\b', resume_text.lower()))
                    st.metric("Action Verbs", action_verbs)
                
                # Highlighted Resume
                st.markdown("---")
                st.subheader("🔍 Highlighted Resume (Keywords)")
                with st.expander("View highlighted resume with keywords marked", expanded=False):
                    highlighted_text = analysis.get('highlighted_text', '')
                    st.markdown(highlighted_text, unsafe_allow_html=True)
                
                # Download Results as JSON
                st.markdown("---")
                st.subheader("📥 Export Results")
                json_results = json.dumps(analysis, indent=2)
                st.download_button(
                    label="Download Analysis (JSON)",
                    data=json_results,
                    file_name="resume_analysis.json",
                    mime="application/json"
                )

else:
    st.info("👆 Please upload a resume to get started!")
    
    # Show example features
    with st.expander("📚 What this analyzer does:"):
        st.markdown("""
        - **ATS Score**: Evaluates how well your resume is optimized for Applicant Tracking Systems
        - **Skills Extraction**: Identifies all technical and professional skills mentioned
        - **Experience Analysis**: Summarizes your professional background
        - **Strengths Identification**: Highlights what makes your resume stand out
        - **Weakness Detection**: Identifies areas that need improvement
        - **Actionable Suggestions**: Provides specific tips to improve your resume
        - **Job Fit Analysis**: Shows how well your resume matches different job roles
        - **Resume Statistics**: Character count, word count, and usage metrics
        """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    Made with ❤️ using Streamlit, NLTK, scikit-learn & Pandas
</div>
""", unsafe_allow_html=True)
