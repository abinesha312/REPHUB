# backend/app/services/matcher.py
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from sentence_transformers import SentenceTransformer

class ResumeMatcher:
    def __init__(self):
        # Load NLP models
        self.nlp = spacy.load("en_core_web_lg")
        self.sentence_transformer = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    
    def calculate_keyword_match_score(self, resume_text, job_skills):
        """Calculate keyword match score between resume and job skills"""
        resume_text = resume_text.lower()
        match_count = 0
        
        for skill in job_skills:
            if skill.lower() in resume_text:
                match_count += 1
        
        # Calculate percentage match
        if job_skills:
            score = match_count / len(job_skills)
        else:
            score = 0
            
        return score
    
    def calculate_tfidf_similarity(self, resume_text, job_text):
        """Calculate TF-IDF based cosine similarity"""
        documents = [resume_text, job_text]
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity
        except:
            return 0
    
    def calculate_semantic_similarity(self, resume_text, job_text):
        """Calculate semantic similarity using sentence transformers"""
        try:
            # Generate embeddings
            resume_embedding = self.sentence_transformer.encode(resume_text, convert_to_tensor=True)
            job_embedding = self.sentence_transformer.encode(job_text, convert_to_tensor=True)
            
            # Calculate cosine similarity
            similarity = np.dot(resume_embedding, job_embedding) / (np.linalg.norm(resume_embedding) * np.linalg.norm(job_embedding))
            return float(similarity)
        except:
            return 0
    
    def match_resume_with_job(self, resume_data, job_data):
        """Match resume with job description and return score and details"""
        # Extract texts
        resume_text = resume_data.get("full_text", "")
        job_text = job_data.get("full_text", "")
        job_skills = job_data.get("requirements", {}).get("skills", [])
        
        # Skip if texts are empty
        if not resume_text or not job_text:
            return {
                "overall_score": 0,
                "details": {
                    "keyword_match": 0,
                    "tfidf_similarity": 0,
                    "semantic_similarity": 0
                }
            }
        
        # Calculate different similarity scores
        keyword_match = self.calculate_keyword_match_score(resume_text, job_skills)
        tfidf_similarity = self.calculate_tfidf_similarity(resume_text, job_text)
        semantic_similarity = self.calculate_semantic_similarity(resume_text, job_text)
        
        # Calculate overall score (weighted average)
        overall_score = (
            keyword_match * 0.4 +
            tfidf_similarity * 0.3 +
            semantic_similarity * 0.3
        )
        
        return {
            "overall_score": overall_score,
            "details": {
                "keyword_match": keyword_match,
                "tfidf_similarity": tfidf_similarity,
                "semantic_similarity": semantic_similarity
            }
        }
    
    def rank_resumes(self, resumes_data, job_data):
        """Rank multiple resumes against a job description"""
        results = []
        
        for resume in resumes_data:
            match_result = self.match_resume_with_job(resume["parsed_data"], job_data)
            results.append({
                "resume_id": resume["id"],
                "version": resume["version"],
                "upload_date": resume["upload_date"],
                "overall_score": match_result["overall_score"],
                "details": match_result["details"]
            })
        
        # Sort by overall score (descending)
        results = sorted(results, key=lambda x: x["overall_score"], reverse=True)
        
        return results
