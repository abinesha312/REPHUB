"""Text extraction from various document formats."""
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TextExtractor:
    """Extract text from different document formats."""
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF using pdfplumber."""
        try:
            import pdfplumber
            
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    def extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX."""
        try:
            import docx2txt
            text = docx2txt.process(file_path)
            return text or ""
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")
    
    @staticmethod
    def extract_from_text(file_path: str) -> str:
        """Extract text from plain text files (LaTeX, etc.)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with latin-1 encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise ValueError(f"Failed to extract text: {str(e)}")
    
    @classmethod
    def extract(cls, file_path: str, format_hint: str) -> str:
        """
        Extract text from a document.
        
        Args:
            file_path: Path to the file
            format_hint: Format hint (pdf, latex, doc, docx)
            
        Returns:
            Extracted text content
        """
        format_hint = format_hint.lower()
        
        if format_hint == "pdf":
            return cls.extract_from_pdf(file_path)
        elif format_hint == "docx":
            return cls.extract_from_docx(file_path)
        elif format_hint in ("latex", "tex", "txt", "doc"):
            return cls.extract_from_text(file_path)
        else:
            # Try to guess from extension
            ext = Path(file_path).suffix.lower()
            if ext == ".pdf":
                return cls.extract_from_pdf(file_path)
            elif ext in (".docx",):
                return cls.extract_from_docx(file_path)
            else:
                return cls.extract_from_text(file_path)
