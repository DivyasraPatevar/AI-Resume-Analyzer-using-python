# AI Resume Analyzer 📄 - Enhanced Edition

An intelligent resume analyzer built with Streamlit and advanced NLP/ML techniques featuring BERT models, spaCy entity recognition, and comprehensive resume analysis with keyword highlighting.

## 🆕 Enhanced Features (v2.0)

### Advanced NLP Analysis
- **🤖 BERT-Powered Analysis**: Zero-shot classification using Facebook's BART model for deeper text understanding of technical skills, leadership, communication, problem-solving, and project management
- **🎓 Accurate Education Detection**: Identifies degrees, institutions, fields of study, and certifications using spaCy NER and pattern matching
- **💼 Enhanced Experience Detection**: Extracts job titles, organizations, and years of experience using Named Entity Recognition
- **🔍 Keyword Highlighting**: Visual highlighting with color-coded display of skills (yellow), action verbs (green), and education keywords (blue)

## Core Features

✨ **ATS Score**: Get a score (0-100) on how well your resume is optimized for Applicant Tracking Systems

🔍 **Skills Extraction**: Automatically identifies 70+ technical skills across multiple categories

📋 **Experience Details**: Extracts job positions, organizations, and total years of experience

✅ **Strengths Identification**: Highlights the strongest points of your resume

⚠️ **Weakness Detection**: Identifies areas that need improvement based on best practices

💡 **Actionable Suggestions**: Specific, practical tips to enhance your resume

🎯 **Job Fit Analysis**: Evaluates compatibility with 6 different job roles

## Installation

### 1. Navigate to Project
```bash
cd "C:\Users\Divyasra\OneDrive\Desktop\AI RESUME ANALYSER"
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download Models (First Run)
The app automatically downloads spaCy and BERT models on first use.

## Running the Application

```bash
streamlit run AA.py
```

Opens at `http://localhost:8501`

## Technologies

- **Streamlit**: Web framework
- **spaCy**: Advanced NLP and Named Entity Recognition
- **Transformers**: BERT-based zero-shot classification (Facebook BART)
- **NLTK**: Tokenization, lemmatization, stopword removal
- **PyPDF2**: PDF extraction
- **scikit-learn**: Machine Learning and similarity metrics
- **Pandas**: Data manipulation

## Analysis Techniques

### 1. Skill Extraction (70+ Skills)
- Regex pattern matching with word boundaries
- Database includes 20+ programming languages, 18+ frameworks, 14+ databases, 11+ cloud platforms
- Recognized categories: Programming, Web, Databases, Cloud, Data Tools, DevOps, Soft Skills

### 2. Education Detection
- Pattern matching for 13+ degree types
- spaCy NER for institutions (ORG entities)
- Recognition of 20+ certification types

### 3. Experience Detection
- spaCy NER extraction (Organizations, Dates)
- Job title pattern recognition
- Years of experience calculation
- Position and organization extraction

### 4. BERT Analysis
- Zero-shot classification on 5 key aspects
- Technical skills, leadership, communication assessment
- Problem-solving and project management evaluation
- Confidence scores provided

### 5. Keyword Highlighting
- Color-coded visual marking
- Interactive expandable resume view
- Multiple highlight categories

### 6. ATS Score Calculation
- Essential sections presence
- Technical keyword density
- Quantifiable achievements
- Action verb usage
- Structure quality

## Output Sections

### Immediate Metrics
- ATS Score (0-100)
- Skills Count
- BERT Aspect Scores

### Detailed Analysis
- **Education Detected**: Degrees and institutions found
- **Experience Detected**: Positions, organizations, years
- **Skills Identified**: Technical skills with badges
- **BERT Analysis**: AI-powered aspect evaluation
- **Strengths**: Top positive aspects
- **Weaknesses**: Areas for improvement
- **Suggestions**: Actionable recommendations
- **Job Fit**: Role compatibility (%)
- **Statistics**: Character, word count, action verbs
- **Highlighted Resume**: Keyword visualization

## Supported Roles for Job Fit Analysis

1. Software Engineer
2. Data Scientist
3. DevOps Engineer
4. Full Stack Developer
5. Product Manager
6. QA Engineer

## Supported File Formats

- PDF (.pdf)
- Text (.txt)

## Tips for Best Results

1. Use clear, professional formatting
2. Include relevant industry keywords
3. Quantify achievements with metrics
4. Keep to 1-2 pages (ATS optimal)
5. Use standard fonts (Arial, Calibri, Times New Roman)
6. Start bullets with strong action verbs
7. Use distinct section headers

## Troubleshooting

### Model Download Issues
- Models auto-download on first run (~1GB total)
- Manual download: `python -m spacy download en_core_web_sm`
- BERT: facebook/bart-large-mnli

### PDF Issues
- Text extraction requires readable PDFs
- Scanned/image-based PDFs won't extract
- Try converting to .txt format

### Memory/Performance
- Models require significant memory
- First run will download ~1GB of data
- Subsequent runs use cached models

### Streamlit Issues
```bash
streamlit run AA.py --logger.level=debug
```

## File Structure

```
AI RESUME ANALYSER/
├── AA.py                    # Main application
├── requirements.txt         # Dependencies
├── README.md               # Original documentation
└── README_ENHANCED.md      # This file
```

## Model Information

- **spaCy**: en_core_web_sm (small English model)
- **BERT**: facebook/bart-large-mnli (175M parameters)
- **NLTK**: Multiple trained models for text processing

## What's New in v2.0

- ✨ BERT zero-shot classification integration
- 🎓 Advanced education detection with spaCy NER
- 💼 Enhanced experience extraction with entity recognition
- 🔍 Keyword highlighting with visual categories
- 📊 BERT aspect scoring (5 key dimensions)
- 🎨 Color-coded highlighting (yellow skills, green verbs, blue education)
- 📈 Improved statistics and visualization
- 🚀 Better entity extraction accuracy

## Performance Notes

- First run: ~2-3 minutes (model downloads)
- Subsequent runs: ~10-30 seconds depending on resume size
- Requires Python 3.8+
- Recommended RAM: 4GB+
- Recommended disk: 2GB free space

## Future Enhancements

- DOCX file support
- Resume template suggestions
- Multi-resume comparison
- Job description tailoring
- Interactive resume builder
- Batch processing
- Custom model training
- Industry-specific analysis

## License

Open source for personal use.

## Support & Issues

Check error messages in the app terminal. Common issues usually involve:
- Model download failures
- PDF extraction problems
- Memory constraints

---

**Made with ❤️ using Streamlit, spaCy, Transformers (BERT), NLTK, scikit-learn & Pandas**

**v2.0 - Enhanced with BERT, spaCy NER, and Advanced NLP**
