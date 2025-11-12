"""
Resume Parser Agent - Extracts structured data from PDF/DOCX resumes
Uses NLP, regex patterns, and AI to parse resumes accurately
"""
import re
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import PyPDF2
import docx
import spacy
from pathlib import Path


class ResumeParserAgent:
    """
    Intelligent Resume Parser that extracts structured information from resumes
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the resume parser with NLP models"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("⚠️  Spacy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None

        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        # Common email pattern
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

        # Phone patterns (Indian and international)
        self.phone_patterns = [
            re.compile(r'\+?91[-.\s]?\d{10}'),  # Indian
            re.compile(r'\+?1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),  # US
            re.compile(r'\b\d{10}\b'),  # 10 digits
            re.compile(r'\+?\d{1,4}[-.\s]?\d{6,}'),  # International
        ]

        # LinkedIn URL pattern
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/[\w-]+', re.IGNORECASE)

        # GitHub URL pattern
        self.github_pattern = re.compile(r'github\.com/[\w-]+', re.IGNORECASE)

        # Education keywords
        self.education_keywords = [
            'B.Tech', 'B.E.', 'M.Tech', 'M.E.', 'MBA', 'MCA', 'BCA',
            'B.Sc', 'M.Sc', 'Ph.D', 'Bachelor', 'Master', 'Diploma',
            'Engineering', 'Computer Science', 'Information Technology'
        ]

        # Skills database (can be extended)
        self.common_skills = {
            'programming': ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'Go', 'Rust', 'Ruby', 'PHP', 'Swift', 'Kotlin'],
            'web': ['React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'FastAPI', 'Express', 'Spring Boot'],
            'database': ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'Cassandra', 'DynamoDB'],
            'cloud': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins', 'CI/CD'],
            'ai_ml': ['Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'NLP', 'Computer Vision', 'scikit-learn'],
            'tools': ['Git', 'JIRA', 'Agile', 'Scrum', 'Linux', 'REST API', 'GraphQL', 'Microservices']
        }

    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        Main method to parse resume from file
        """
        # Extract text based on file type
        text = self._extract_text(file_path)

        if not text:
            return {"error": "Could not extract text from resume"}

        # Parse structured information
        parsed_data = {
            "raw_text": text,
            "contact_info": self._extract_contact_info(text),
            "summary": self._extract_summary(text),
            "skills": self._extract_skills(text),
            "work_experience": self._extract_work_experience(text),
            "education": self._extract_education(text),
            "certifications": self._extract_certifications(text),
            "projects": self._extract_projects(text),
            "languages": self._extract_languages(text),
            "total_experience_years": self._calculate_experience(text),
        }

        return parsed_data

    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX file"""
        file_extension = Path(file_path).suffix.lower()

        try:
            if file_extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_extension in ['.docx', '.doc']:
                return self._extract_from_docx(file_path)
            elif file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return ""
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
        return text

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX: {e}")
        return text

    def _extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information"""
        # Email
        email_match = self.email_pattern.search(text)
        email = email_match.group(0) if email_match else None

        # Phone
        phone = None
        for pattern in self.phone_patterns:
            phone_match = pattern.search(text)
            if phone_match:
                phone = phone_match.group(0)
                break

        # LinkedIn
        linkedin_match = self.linkedin_pattern.search(text)
        linkedin = f"https://{linkedin_match.group(0)}" if linkedin_match else None

        # GitHub
        github_match = self.github_pattern.search(text)
        github = f"https://{github_match.group(0)}" if github_match else None

        # Name extraction using NER
        name = self._extract_name(text)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin_url": linkedin,
            "github_url": github,
        }

    def _extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name using NER"""
        if not self.nlp:
            # Fallback: assume first line is name
            lines = text.strip().split('\n')
            return lines[0].strip() if lines else None

        # Use first 3 lines for name detection
        first_lines = '\n'.join(text.strip().split('\n')[:3])
        doc = self.nlp(first_lines)

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text

        return None

    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract professional summary/objective"""
        summary_patterns = [
            r'(?:professional\s+)?summary[:\s]+(.*?)(?:\n\n|\nexperience|\neducation)',
            r'(?:career\s+)?objective[:\s]+(.*?)(?:\n\n|\nexperience|\neducation)',
            r'about\s+me[:\s]+(.*?)(?:\n\n|\nexperience|\neducation)',
        ]

        for pattern in summary_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()

        return None

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume"""
        skills = []

        # Look for skills section
        skills_section_pattern = r'(?:skills?|technical skills?|core competencies)[:\s]+(.*?)(?:\n\n|\nexperience|\neducation|$)'
        match = re.search(skills_section_pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            skills_text = match.group(1)

            # Find known skills in the skills section
            for category, skill_list in self.common_skills.items():
                for skill in skill_list:
                    if re.search(r'\b' + re.escape(skill) + r'\b', skills_text, re.IGNORECASE):
                        if skill not in skills:
                            skills.append(skill)

        # Also search entire document for skills
        for category, skill_list in self.common_skills.items():
            for skill in skill_list:
                if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                    if skill not in skills:
                        skills.append(skill)

        return skills

    def _extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience"""
        experiences = []

        # Find experience section
        exp_pattern = r'(?:work\s+)?experience[:\s]+(.*?)(?:\neducation|\nskills|\ncertifications|\nprojects|$)'
        match = re.search(exp_pattern, text, re.IGNORECASE | re.DOTALL)

        if not match:
            return experiences

        exp_text = match.group(1)

        # Split by common company/role patterns
        # This is a simplified version; in production, use more sophisticated parsing
        lines = exp_text.split('\n')

        current_job = {}
        for line in lines:
            line = line.strip()
            if not line:
                if current_job:
                    experiences.append(current_job)
                    current_job = {}
                continue

            # Try to detect company, role, dates
            # This is a placeholder - real implementation would be more complex
            if not current_job.get('company'):
                current_job['company'] = line
                current_job['role'] = ''
                current_job['duration'] = ''
                current_job['description'] = []

        if current_job:
            experiences.append(current_job)

        return experiences

    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education details"""
        education = []

        # Find education section
        edu_pattern = r'education[:\s]+(.*?)(?:\nexperience|\nskills|\ncertifications|\nprojects|$)'
        match = re.search(edu_pattern, text, re.IGNORECASE | re.DOTALL)

        if not match:
            return education

        edu_text = match.group(1)

        # Look for degree keywords
        for keyword in self.education_keywords:
            if keyword.lower() in edu_text.lower():
                # Extract context around the keyword
                pattern = rf'.{{0,100}}{re.escape(keyword)}.{{0,100}}'
                matches = re.finditer(pattern, edu_text, re.IGNORECASE)
                for m in matches:
                    education.append({
                        'degree': keyword,
                        'details': m.group(0).strip()
                    })

        return education

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []

        cert_pattern = r'certifications?[:\s]+(.*?)(?:\n\n|\nexperience|\neducation|\nskills|$)'
        match = re.search(cert_pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            cert_text = match.group(1)
            # Split by newlines and bullet points
            lines = re.split(r'\n|•|·|-', cert_text)
            for line in lines:
                line = line.strip()
                if len(line) > 5:  # Avoid empty or very short lines
                    certifications.append(line)

        return certifications

    def _extract_projects(self, text: str) -> List[Dict[str, str]]:
        """Extract project details"""
        projects = []

        proj_pattern = r'projects?[:\s]+(.*?)(?:\n\n|\nexperience|\neducation|\nskills|\ncertifications|$)'
        match = re.search(proj_pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            proj_text = match.group(1)
            # Simple parsing - split by double newlines or bullet points
            project_blocks = re.split(r'\n\n|(?=^[•·-])', proj_text, flags=re.MULTILINE)

            for block in project_blocks:
                block = block.strip()
                if len(block) > 10:
                    projects.append({
                        'title': block.split('\n')[0].strip('•·- '),
                        'description': block
                    })

        return projects

    def _extract_languages(self, text: str) -> List[str]:
        """Extract known languages"""
        languages = []
        common_languages = ['English', 'Hindi', 'Spanish', 'French', 'German', 'Chinese', 'Japanese']

        lang_pattern = r'languages?[:\s]+(.*?)(?:\n\n|\nexperience|\neducation|\nskills|$)'
        match = re.search(lang_pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            lang_text = match.group(1)
            for lang in common_languages:
                if re.search(r'\b' + lang + r'\b', lang_text, re.IGNORECASE):
                    languages.append(lang)

        return languages

    def _calculate_experience(self, text: str) -> float:
        """Calculate total years of experience"""
        # Look for patterns like "5 years", "5+ years", "5-7 years"
        exp_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience)?',
            r'experience[:\s]+(\d+)\+?\s*(?:years?|yrs?)',
        ]

        for pattern in exp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))

        return 0.0

    async def parse_with_ai(self, text: str) -> Dict[str, Any]:
        """
        Use OpenAI GPT to parse resume (more accurate but requires API)
        This is an enhanced version using AI
        """
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not provided")

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)

            prompt = f"""
            Extract the following information from this resume in JSON format:
            - name
            - email
            - phone
            - summary
            - skills (list)
            - work_experience (list with company, role, duration, description)
            - education (list with degree, institution, year)
            - certifications (list)
            - total_experience_years

            Resume:
            {text[:4000]}  # Limit text length

            Return only valid JSON.
            """

            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert resume parser. Extract information accurately and return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"AI parsing error: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    parser = ResumeParserAgent()
    # result = parser.parse_resume("path/to/resume.pdf")
    # print(result)
