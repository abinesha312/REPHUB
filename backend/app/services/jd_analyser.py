# backend/app/services/jd_analyzer.py
import spacy
import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
import pytesseract
from pdf2image import convert_from_path
import docx2txt

class JobDescriptionAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        
        # Common skill terms to look for
        self.common_skills = [
            "python", "java", "javascript", "typescript", "html", "css", 
            "react", "angular", "vue", "node.js", "express", "django",
            "flask", "sql", "mysql", "postgresql", "mongodb", "nosql",
            "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd",
            "git", "jenkins", "machine learning", "deep learning", "nlp",
            "data analysis", "big data", "hadoop", "spark", "tensorflow",
            "pytorch", "keras", "scikit-learn", "pandas", "numpy",
            "project management", "agile", "scrum", "jira", "confluence"
        ]
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using OCR if needed"""
        try:
            images = convert_from_path(pdf_path)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img)
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_docx(self, docx_path):
        """Extract text from DOCX file"""
        try:
            text = docx2txt.process(docx_path)
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""
    
    def extract_text_from_file(self, file_path):
        """Extract text from uploaded file"""
        if file_path.endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        elif file_path.endswith(('.docx', '.doc')):
            return self.extract_text_from_docx(file_path)
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    
    def scrape_job_description(self, url):
        """Scrape job description from URL"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try common job description containers
            job_description = ""
            
            # LinkedIn
            if "linkedin.com" in url:
                job_section = soup.find('div', {'class': 'description__text'})
                if job_section:
                    job_description = job_section.get_text()
            
            # Indeed
            elif "indeed.com" in url:
                job_section = soup.find('div', {'id': 'jobDescriptionText'})
                if job_section:
                    job_description = job_section.get_text()
            
            # Glassdoor
            elif "glassdoor.com" in url:
                job_section = soup.find('div', {'class': 'jobDescriptionContent'})
                if job_section:
                    job_description = job_section.get_text()
            
            # Generic fallback
            if not job_description:
                # Try to find the largest text block on the page
                paragraphs = soup.find_all(['p', 'div', 'section'])
                if paragraphs:
                    # Sort by text length and take the top 5
                    paragraphs = sorted(paragraphs, key=lambda x: len(x.get_text()), reverse=True)[:5]
                    for p in paragraphs:
                        job_description += p.get_text() + "\n\n"
            
            return job_description.strip()
            
        except Exception as e:
            print(f"Error scraping job description: {e}")
            return ""
    
    def extract_requirements(self, text):
        """Extract job requirements from text"""
        doc = self.nlp(text)
        
        # Find requirements section
        requirements_section = ""
        lines = text.lower().split('\n')
        
        requirements_keywords = ["requirements", "qualifications", "what you'll need", 
                                "what we're looking for", "skills", "experience required"]
        
        in_requirements = False
        for line in lines:
            if any(keyword in line.lower() for keyword in requirements_keywords):
                in_requirements = True
                requirements_section += line + "\n"
            elif in_requirements and line.strip():
                if any(keyword in line.lower() for keyword in ["about us", "about the company", 
                                                             "benefits", "what we offer"]):
                    in_requirements = False
                else:
                    requirements_section += line + "\n"
        
        # If no clear requirements section, use the whole text
        if not requirements_section:
            requirements_section = text
        
        # Extract skills
        skills = []
        for skill in self.common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text.lower()):
                skills.append(skill)
        
        # Extract education requirements
        education_keywords = ["bachelor", "master", "phd", "degree", "diploma", "certification"]
        education = []
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in education_keywords):
                education.append(sent.text.strip())
        
        # Extract experience requirements
        experience_pattern = r'\b(\d+[\+\-]?\s*(?:year|yr)s?\s*(?:of)?\s*experience)\b'
        experience_matches = re.findall(experience_pattern, text.lower())
        experience = list(set(experience_matches))
        
        # Extract key phrases using noun chunks
        key_phrases = []
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:  # Only multi-word phrases
                key_phrases.append(chunk.text)
        
        # Get most frequent words (excluding stop words)
        words = [token.text.lower() for token in doc if not token.is_stop and token.is_alpha]
        word_freq = Counter(words).most_common(20)
        
        return {
            "skills": skills,
            "education": education,
            "experience": experience,
            "key_phrases": key_phrases[:20],  # Top 20 phrases
            "frequent_words": word_freq,
            "requirements_section": requirements_section
        }
    
    def analyze_job_description(self, source, is_url=False):
        """Analyze job description from file or URL"""
        if is_url:
            text = self.scrape_job_description(source)
        else:
            text = self.extract_text_from_file(source)
        
        if not text:
            return {"error": "Failed to extract text from the job description"}
        
        requirements = self.extract_requirements(text)
        
        return {
            "full_text": text,
            "requirements": requirements
        }
