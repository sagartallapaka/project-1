import re
import spacy
from typing import Dict, Any, List, Optional
from pathlib import Path
import PyPDF2
import docx
import pdfplumber
from datetime import datetime


class ResumeParserAgent:
    """Agent for parsing resumes and extracting structured information"""
    
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # Fallback if model not downloaded
            self.nlp = None
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Main method to parse resume from file"""
        # Extract text from file
        text = self._extract_text(file_path)
        
        # Parse different sections
        parsed_data = {
            "resume_text": text,
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "skills": self._extract_skills(text),
            "experience_years": self._calculate_experience(text),
            "education": self._extract_education(text),
            "work_history": self._extract_work_history(text),
            "certifications": self._extract_certifications(text),
            "projects": self._extract_projects(text),
            "linkedin_url": self._extract_linkedin(text),
            "github_url": self._extract_github(text)
        }
        
        return parsed_data
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX file"""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.pdf':
            return self._extract_from_pdf(str(file_path))
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            return self._extract_from_docx(str(file_path))
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except:
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
            except Exception as e:
                raise Exception(f"Failed to extract text from PDF: {str(e)}")
        
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number"""
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?\d{10,15}'
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical and soft skills"""
        # Common technical skills
        tech_skills = [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'php',
            'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'fastapi', 'spring',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
            'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch',
            'data analysis', 'data science', 'pandas', 'numpy', 'scikit-learn',
            'html', 'css', 'sass', 'tailwind', 'bootstrap',
            'rest api', 'graphql', 'microservices', 'agile', 'scrum',
            'linux', 'bash', 'powershell'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in tech_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        # Remove duplicates and return
        return list(set(found_skills))
    
    def _calculate_experience(self, text: str) -> float:
        """Calculate years of experience"""
        # Look for patterns like "5 years of experience", "3+ years", etc.
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience\s+(?:of\s+)?(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s+(?:of\s+)?experience'
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            years.extend([int(match) for match in matches])
        
        if years:
            return max(years)
        
        # Try to calculate from work history dates
        date_pattern = r'(20\d{2}|19\d{2})'
        dates = re.findall(date_pattern, text)
        if len(dates) >= 2:
            dates = [int(d) for d in dates]
            return datetime.now().year - min(dates)
        
        return 0.0
    
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information"""
        education = []
        
        # Common degree patterns
        degree_patterns = [
            r'(Bachelor|B\.?S\.?|B\.?A\.?|B\.?Tech|B\.?E\.?)\s+(?:of\s+)?(?:Science\s+)?(?:in\s+)?([A-Za-z\s]+)',
            r'(Master|M\.?S\.?|M\.?A\.?|M\.?Tech|MBA)\s+(?:of\s+)?(?:Science\s+)?(?:in\s+)?([A-Za-z\s]+)',
            r'(Ph\.?D\.?|Doctorate)\s+(?:in\s+)?([A-Za-z\s]+)',
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    "degree": match[0],
                    "field": match[1].strip() if len(match) > 1 else "",
                })
        
        return education
    
    def _extract_work_history(self, text: str) -> List[Dict[str, Any]]:
        """Extract work history"""
        work_history = []
        
        # Look for job titles and companies
        # This is a simplified version - in production, use more sophisticated NLP
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            # Look for date ranges (e.g., "2020 - 2023", "Jan 2020 - Present")
            date_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4}).*?(?:Present|Current|\d{4}))'
            if re.search(date_pattern, line, re.IGNORECASE):
                # Previous line might be job title
                if i > 0:
                    work_history.append({
                        "title": lines[i-1].strip(),
                        "duration": line.strip(),
                        "company": lines[i+1].strip() if i+1 < len(lines) else ""
                    })
        
        return work_history[:5]  # Return top 5
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        
        # Common certification keywords
        cert_keywords = [
            'AWS Certified', 'Azure Certified', 'Google Cloud Certified',
            'PMP', 'CISSP', 'CompTIA', 'Cisco', 'CCNA', 'CCNP',
            'Certified Kubernetes', 'CKA', 'CKAD',
            'Scrum Master', 'CSM', 'PSM'
        ]
        
        for keyword in cert_keywords:
            if keyword.lower() in text.lower():
                certifications.append(keyword)
        
        return certifications
    
    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract project information"""
        projects = []
        
        # Look for "Projects" section
        project_section_pattern = r'(?:Projects?|Personal Projects?|Academic Projects?)[:\s]+(.*?)(?=\n\n|\Z)'
        matches = re.findall(project_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if matches:
            project_text = matches[0]
            # Split by bullet points or numbers
            project_items = re.split(r'[\n•\-\*]\s*', project_text)
            
            for item in project_items[:5]:  # Top 5 projects
                if item.strip():
                    projects.append({
                        "description": item.strip()[:200]  # Limit length
                    })
        
        return projects
    
    def _extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn URL"""
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+'
        matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        return matches[0] if matches else None
    
    def _extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub URL"""
        github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[\w\-]+'
        matches = re.findall(github_pattern, text, re.IGNORECASE)
        return matches[0] if matches else None
