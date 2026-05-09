# AI Resume Analyzer v2.0 - Setup & Installation Guide

## Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
cd "C:\Users\Divyasra\OneDrive\Desktop\AI RESUME ANALYSER"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
streamlit run AA.py
```

The first run will automatically download:
- spaCy English model (en_core_web_sm) - ~40MB
- BERT model (facebook/bart-large-mnli) - ~1.6GB
- NLTK required data

**Total download time**: 3-5 minutes on first run

### Step 3: Access the App
Opens automatically at: `http://localhost:8501`

---

## What's New in v2.0

### 🤖 BERT-Powered Analysis
- Analyzes 5 key aspects of your resume
- Technical skills evaluation
- Leadership capabilities assessment
- Communication skills detection
- Problem-solving capability scoring
- Project management evaluation

### 🎓 Advanced Education Detection
- Automatically detects degrees (Bachelor, Master, PhD, etc.)
- Identifies educational institutions using Named Entity Recognition
- Recognizes certifications (AWS, Azure, Google Cloud, etc.)
- Shows detected education entries with visual cards

### 💼 Enhanced Experience Detection
- Extracts job positions and titles
- Identifies companies/organizations
- Calculates total years of experience
- Named Entity Recognition (NER) powered

### 🔍 Keyword Highlighting
Three color categories:
- **Yellow**: Technical skills detected
- **Green**: Action verbs (led, managed, developed, etc.)
- **Blue**: Education keywords

Interactive expandable view shows your resume with all keywords marked!

---

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB+ recommended)
- **Disk Space**: 2GB for models
- **Network**: For first-run model downloads
- **OS**: Windows, macOS, or Linux

---

## Model Information

| Component | Size | Purpose |
|-----------|------|---------|
| spaCy (en_core_web_sm) | ~40MB | Named Entity Recognition, tokenization |
| BERT (facebook/bart-large-mnli) | ~1.6GB | Zero-shot classification, aspect analysis |
| NLTK Data | ~100MB | Tokenization, lemmatization, stopwords |
| **Total** | **~1.75GB** | Complete ML pipeline |

---

## Features Summary

### ATS Optimization
- Score (0-100) for ATS compatibility
- Section presence checking
- Keyword density analysis
- Quantified achievement detection
- Action verb usage scoring

### Skill Recognition
70+ skills recognized across:
- 20+ Programming Languages
- 18+ Web Frameworks
- 14+ Databases
- 11+ Cloud Platforms
- 16+ Data Tools
- 14+ DevOps Tools
- Soft Skills

### Analysis Output
✅ ATS Score with improvement status
✅ Detected Education & Institutions
✅ Extracted Job Positions & Companies
✅ BERT Aspect Scores (5 dimensions)
✅ Skills with visual badges
✅ Strengths (3-5 items)
✅ Weaknesses (top 5)
✅ Actionable Suggestions (6 items)
✅ Job Fit for 6 roles
✅ Resume Statistics
✅ Highlighted Resume with keywords

---

## Troubleshooting

### Issue: "spaCy model not found"
**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: "BERT model loading error"
**Solution:**
- First run downloads automatically
- Requires internet connection
- Model is ~1.6GB
- Subsequent runs use cached model

### Issue: "Out of Memory"
**Solution:**
- Ensure 4GB+ RAM available
- Close other applications
- BERT analysis can be disabled if needed

### Issue: "PDF extraction fails"
**Solution:**
- Use text-based PDFs only
- Scanned/image PDFs won't work
- Convert to .txt format
- Ensure PDF not password protected

### Issue: "Streamlit port already in use"
**Solution:**
```bash
streamlit run AA.py --server.port 8502
```

---

## Usage Tips

### For Best Results:
1. **Clear Section Headers**: Use "Education", "Experience", "Skills"
2. **Quantify Metrics**: "Improved performance by 25%"
3. **Action Verbs**: Start bullets with verbs (led, developed, managed)
4. **Keywords**: Include relevant technical terms
5. **Standard Format**: Use Arial/Calibri, 10-12pt font
6. **Length**: Keep to 1-2 pages

### What Gets Highlighted:
- All 70+ technical skills found
- 15+ action verbs (led, managed, developed, etc.)
- 20+ education keywords
- Certifications and degrees

### BERT Analysis Evaluates:
1. Technical Skills - Does resume mention relevant tech?
2. Leadership Experience - Evidence of leadership?
3. Communication Skills - Communication abilities shown?
4. Problem-Solving - Problem-solving examples present?
5. Project Management - PM experience evident?

---

## File Contents

```
AA.py
├── Main Streamlit Application
├── Enhanced NLP Functions
│   ├── detect_education() - spaCy-based education extraction
│   ├── detect_experience() - NER-based experience detection
│   ├── highlight_keywords() - Visual keyword highlighting
│   ├── analyze_text_with_bert() - BERT-based analysis
│   └── load_spacy_model() - Cached model loading
├── Analysis Functions
│   ├── calculate_ats_score()
│   ├── extract_skills()
│   ├── identify_strengths()
│   ├── identify_weaknesses()
│   ├── generate_suggestions()
│   └── analyze_job_fit()
└── Streamlit UI with Enhanced Display

requirements.txt
├── streamlit==1.28.1
├── PyPDF2==3.0.1
├── nltk==3.8.1
├── scikit-learn==1.3.2
├── pandas==2.1.3
├── numpy==1.24.3
├── transformers==4.35.2 (BERT models)
├── torch==2.1.1 (Required by transformers)
├── spacy==3.7.2 (NER and NLP)
├── python-docx==0.8.11 (Future enhancement)
└── pydantic==2.5.0 (Data validation)
```

---

## Performance Expectations

| Stage | Time | Notes |
|-------|------|-------|
| First Run - Downloads | 3-5 min | One-time, requires internet |
| First Run - Analysis | 15-30 sec | Loading models into memory |
| Subsequent Runs - Analysis | 10-20 sec | Models cached |
| BERT Analysis | 5-10 sec | Zero-shot classification |
| Total First Run | 3-6 min | Includes downloads |
| Total Subsequent | 10-25 sec | Typical analysis |

---

## Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'spacy'` | Incomplete installation | `pip install -r requirements.txt` |
| `RuntimeError: Model 'en_core_web_sm' not found` | spaCy model missing | `python -m spacy download en_core_web_sm` |
| `MemoryError` | Insufficient RAM | Close apps, ensure 4GB+ free RAM |
| `Connection timeout` | Model download failed | Check internet, try again |
| `PDF extraction returns empty` | Scanned/image PDF | Convert to .txt or use text PDF |

---

## What Happens During First Run

1. **Streamlit starts** (~2 sec)
2. **NLTK data downloads** (~10-20 sec)
3. **spaCy model downloads** (~30-60 sec)
4. **BERT model downloads** (~2-3 min)
5. **Models load into memory** (~10 sec)
6. **App ready** - Access at localhost:8501

Total: **3-5 minutes**

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Run: `streamlit run AA.py`
3. ✅ Wait for models to download (first run)
4. ✅ Upload your resume (PDF or TXT)
5. ✅ Click "Analyze Resume"
6. ✅ Review all results and suggestions
7. ✅ Download analysis as JSON

---

## Support & FAQs

**Q: Why is the first run slow?**
A: Models are downloading (~1.75GB total). Subsequent runs use cached models.

**Q: Can I use Word (.docx) resumes?**
A: Not yet, but it's planned. Convert to PDF first.

**Q: Will my resume data be stored?**
A: No, everything is local. No data is sent to external servers.

**Q: Can I run this offline after setup?**
A: Yes, after models download. First run requires internet.

**Q: What if I only want to use certain features?**
A: You can comment out features in the code, but all are optimized for performance.

---

## Version Information

- **Version**: 2.0 (Enhanced with BERT & spaCy)
- **Release Date**: 2024
- **Python**: 3.8+
- **Status**: Production Ready

---

**Ready to analyze? Run: `streamlit run AA.py`**

Made with ❤️ using Streamlit, spaCy, BERT, NLTK, scikit-learn & Pandas
