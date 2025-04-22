# backend/app/services/resume_parser.py
import spacy
import pytesseract
from pdf2image import convert_from_path
import docx2txt
import re
import json
from pathlib import Path

class ResumeParser:
    def __init__(self):
        # Load NLP model
        self.nlp = spacy.load("en_core_web_lg")
        
        # Define entity patterns for resume sections
        self.section_patterns = {
            "education": ["education", "academic", "degree", "university", "college"],
            "experience": ["experience", "employment", "work history", "job history"],
            "skills": ["skills", "technical skills", "competencies", "proficiencies"],
            "contact": ["contact", "phone", "email", "address"]
        }
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using OCR if needed"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            text = ""
            
            # Extract text from each image
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
    
    def extract_text(self, file_path):
        """Extract text from various file formats"""
        file_path = Path(file_path)
        if file_path.suffix.lower() == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() in [".docx", ".doc"]:
            return self.extract_text_from_docx(file_path)
        elif file_path.suffix.lower() in [".txt"]:
            return file_path.read_text()
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def identify_sections(self, text):
        """Identify different sections in the resume"""
        sections = {}
        lines = text.split('\n')
        current_section = "header"
        sections[current_section] = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            lower_line = line.lower()
            matched_section = None
            
            for section, keywords in self.section_patterns.items():
                if any(keyword in lower_line for keyword in keywords):
                    matched_section = section
                    break
            
            if matched_section:
                current_section = matched_section
                sections[current_section] = []
            else:
                sections[current_section].append(line)
        
        return sections
    
    def extract_entities(self, text):
        """Extract entities like name, email, phone, etc."""
        doc = self.nlp(text)
        entities = {
            "name": [],
            "email": [],
            "phone": [],
            "location": [],
            "organizations": [],
            "dates": [],
            "skills": []
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            entities["email"] = emails
        
        # Extract phone
        phone_pattern = r'\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        if phones:
            entities["phone"] = phones
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["name"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["organizations"].append(ent.text)
            elif ent.label_ == "GPE" or ent.label_ == "LOC":
                entities["location"].append(ent.text)
            elif ent.label_ == "DATE":
                entities["dates"].append(ent.text)
        
        # Extract skills (requires custom approach or a skills database)
        # This is a simplified version
        common_skills = ["python", "java", "javascript", "sql", "machine learning", 
                         "data analysis", "project management", "agile", "scrum"]
        
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text.lower()):
                entities["skills"].append(skill)
        
        return entities
    
    def parse_resume(self, file_path):
        """Parse resume from file path and return structured data"""
        text = self.extract_text(file_path)
        sections = self.identify_sections(text)
        entities = self.extract_entities(text)
        
        # Combine sections and entities
        parsed_data = {
            "sections": sections,
            "entities": entities,
            "full_text": text
        }
        
        return parsed_data
