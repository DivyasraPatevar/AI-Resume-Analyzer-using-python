# AI Resume Analyzer 📄

An intelligent resume analyzer built with Streamlit and traditional Machine Learning/NLP techniques that provides comprehensive analysis and improvement suggestions for your resume using NLTK, scikit-learn, and Pandas.

## Features

✨ **ATS Score**: Get a score (0-100) on how well your resume is optimized for Applicant Tracking Systems

🔍 **Skills Extraction**: Automatically identifies and lists all technical and professional skills using keyword matching

📋 **Experience Summary**: Extracts and summarizes your professional background

✅ **Strengths Identification**: Highlights the strongest points of your resume using rule-based analysis

⚠️ **Weakness Detection**: Identifies areas that need improvement based on best practices

💡 **Actionable Suggestions**: Specific, practical tips to enhance your resume

🎯 **Job Fit Analysis**: Evaluates how well your resume matches different job roles using similarity metrics

## Installation

### 1. Clone or Navigate to the Project
```bash
cd "C:\Users\Divyasra\OneDrive\Desktop\AI RESUME ANALYSER"
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
streamlit run Code.py
```

The app will open in your default browser at `http://localhost:8501`

## How to Use

1. **Upload Resume**: Click to upload your resume (PDF or TXT format)
2. **Preview**: Optionally preview your resume text
3. **Analyze**: Click the "Analyze Resume" button (no API key required!)
4. **Review Results**: Get comprehensive feedback and suggestions
5. **Export**: Download the analysis results as JSON for future reference

## Supported File Formats

- **PDF**: .pdf files
- **Text**: .txt files

## Output Sections

- **ATS Score**: How well optimized for automated systems (0-100)
- **Skills Identified**: List of extracted skills with badges
- **Experience Summary**: Professional background summary extracted from resume
- **Strengths**: Top 3-5 positive aspects of your resume
- **Areas for Improvement**: Specific weaknesses identified
- **Actionable Suggestions**: Step-by-step improvement recommendations
- **Job Fit Analysis**: Compatibility with different roles (Software Engineer, Data Scientist, DevOps Engineer, etc.)
- **Resume Statistics**: Character count, word count, and action verb usage

## File Structure

```
AI RESUME ANALYSER/
├── AA.py                 # Main Streamlit application
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Technologies Used

- **Streamlit**: Web application framework
- **PyPDF2**: PDF text extraction
- **NLTK**: Natural Language Processing (tokenization, lemmatization, stopword removal)
- **scikit-learn**: Machine Learning (TF-IDF, similarity metrics)
- **Pandas**: Data manipulation and analysis
- **Python**: Core programming language

## How It Works

### Analysis Techniques

1. **Skill Extraction**: Uses regex pattern matching against a comprehensive technical skills database
2. **ATS Score**: Calculates based on:
   - Presence of essential resume sections
   - Technical keyword density
   - Quantifiable achievements
   - Use of action verbs
   - Overall structure

3. **Experience Analysis**: Extracts job titles, companies, and years of experience using NLP

4. **Strengths & Weaknesses**: Rule-based analysis checking for:
   - Skill variety and count
   - Quantifiable metrics usage
   - Action verb usage
   - Resume length and completeness
   - Educational background clarity

5. **Job Fit Analysis**: Uses keyword matching to evaluate relevance for different job roles

## Tips for Best Results

1. **Use Clear Formatting**: Well-formatted resumes yield better analysis
2. **Include Keywords**: Add relevant industry keywords and skills
3. **Quantify Achievements**: Use metrics and numbers in accomplishments
4. **Keep It Concise**: Generally 1-2 pages for better ATS compatibility
5. **Use Standard Fonts**: Stick to fonts like Arial, Calibri, or Times New Roman
6. **Action Verbs**: Start bullet points with strong action verbs (led, developed, managed, etc.)

## Supported Job Roles for Fit Analysis

- Software Engineer
- Data Scientist
- DevOps Engineer
- Full Stack Developer
- Product Manager
- QA Engineer

## Skills Database

The analyzer recognizes 6 categories of skills:
- **Programming Languages**: Python, Java, JavaScript, C++, C#, PHP, Ruby, Go, etc.
- **Web Frameworks**: Django, Flask, React, Angular, Vue, Express, etc.
- **Databases**: SQL, MySQL, PostgreSQL, MongoDB, Cassandra, Redis, etc.
- **Cloud Platforms**: AWS, Azure, GCP, Docker, Kubernetes, etc.
- **Data Tools**: Pandas, NumPy, scikit-learn, TensorFlow, PyTorch, Spark, etc.
- **DevOps**: CI/CD, Jenkins, GitLab, GitHub, Git, Linux, Nginx, etc.
- **Soft Skills**: Leadership, Communication, Teamwork, Problem-solving, Agile, Scrum

## Troubleshooting

### NLTK Data Not Found
The app automatically downloads required NLTK data on first run. If you encounter issues:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
```

### PDF Extraction Issues
- Try converting your PDF to a text file if extraction fails
- Ensure the PDF is not password protected
- Scanned PDFs may not extract text properly

### Streamlit Not Running
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Try running: `streamlit run AA.py --logger.level=debug`

## Future Enhancements

- Support for DOCX format
- Resume template suggestions
- Multiple resume comparison
- Job description matching
- Custom skills database configuration
- Resume formatting analysis

## License

This project is open source and available for personal use.

## Support

For issues or suggestions, please check the error messages in the app or review your resume content and formatting.

---

**Made with ❤️ using Streamlit, NLTK, scikit-learn & Pandas**
