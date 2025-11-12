"""
Job Description Analyzer Agent
Parses job descriptions and extracts requirements, skills, experience level
"""
import re
import os
from typing import Dict, List, Optional, Any
import spacy


class JobDescriptionAnalyzerAgent:
    """
    Analyzes job descriptions to extract structured requirements
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize JD analyzer"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = None

        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        # Common skills taxonomy
        self.skills_taxonomy = {
            'programming_languages': [
                'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go',
                'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'Rust'
            ],
            'frameworks': [
                'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask',
                'FastAPI', 'Spring Boot', 'Express', '.NET', 'Laravel'
            ],
            'databases': [
                'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Cassandra',
                'Oracle', 'DynamoDB', 'Elasticsearch'
            ],
            'cloud_devops': [
                'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform',
                'Jenkins', 'CI/CD', 'Ansible', 'GitLab CI'
            ],
            'ai_ml': [
                'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision',
                'TensorFlow', 'PyTorch', 'scikit-learn', 'Keras'
            ],
            'soft_skills': [
                'Communication', 'Leadership', 'Problem Solving', 'Teamwork',
                'Critical Thinking', 'Time Management', 'Adaptability'
            ]
        }

        # Experience level keywords
        self.experience_levels = {
            'entry': ['entry level', 'junior', 'graduate', 'fresher', '0-2 years'],
            'mid': ['mid level', 'intermediate', 'experienced', '2-5 years', '3-5 years'],
            'senior': ['senior', 'lead', 'principal', '5+ years', '7+ years'],
            'expert': ['expert', 'architect', 'staff', 'distinguished', '10+ years']
        }

        # Education level keywords
        self.education_levels = [
            'B.Tech', 'B.E.', 'M.Tech', 'M.E.', 'MBA', 'MCA', 'BCA',
            "Bachelor's", "Master's", 'PhD', 'Diploma'
        ]

    def analyze(self, job_description: str) -> Dict[str, Any]:
        """
        Main method to analyze job description
        """
        return {
            "required_skills": self._extract_skills(job_description, required=True),
            "nice_to_have_skills": self._extract_skills(job_description, required=False),
            "experience_requirements": self._extract_experience_requirements(job_description),
            "education_requirements": self._extract_education_requirements(job_description),
            "responsibilities": self._extract_responsibilities(job_description),
            "qualifications": self._extract_qualifications(job_description),
            "job_title_analysis": self._analyze_job_title(job_description),
            "experience_level": self._determine_experience_level(job_description),
            "key_keywords": self._extract_key_keywords(job_description),
            "remote_flexibility": self._detect_remote_flexibility(job_description),
        }

    def _extract_skills(self, text: str, required: bool = True) -> List[Dict[str, Any]]:
        """Extract required and nice-to-have skills"""
        skills = []

        # Determine which section to look at
        if required:
            # Look in requirements/qualifications section
            section_patterns = [
                r'(?:required|requirements|must have|qualifications)[:\s]+(.*?)(?:\n\n|nice to have|preferred|$)',
            ]
        else:
            # Look in nice-to-have/preferred section
            section_patterns = [
                r'(?:nice to have|preferred|optional|plus)[:\s]+(.*?)(?:\n\n|$)',
            ]

        relevant_text = text
        for pattern in section_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                relevant_text = match.group(1)
                break

        # Find skills from taxonomy
        for category, skill_list in self.skills_taxonomy.items():
            for skill in skill_list:
                if re.search(r'\b' + re.escape(skill) + r'\b', relevant_text, re.IGNORECASE):
                    skills.append({
                        "skill": skill,
                        "category": category,
                        "is_required": required
                    })

        return skills

    def _extract_experience_requirements(self, text: str) -> Dict[str, Any]:
        """Extract years of experience required"""
        # Patterns for experience requirements
        patterns = [
            r'(\d+)\+?\s*(?:to|-)\s*(\d+)\s*years',  # 3-5 years
            r'(\d+)\+\s*years',  # 5+ years
            r'minimum\s*(\d+)\s*years',  # minimum 3 years
            r'at least\s*(\d+)\s*years',  # at least 2 years
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    return {
                        "min_years": int(groups[0]),
                        "max_years": int(groups[1]),
                        "text": match.group(0)
                    }
                elif len(groups) == 1:
                    years = int(groups[0])
                    return {
                        "min_years": years,
                        "max_years": None,
                        "text": match.group(0)
                    }

        return {"min_years": None, "max_years": None, "text": None}

    def _extract_education_requirements(self, text: str) -> List[str]:
        """Extract education requirements"""
        education = []

        for edu_level in self.education_levels:
            if re.search(r'\b' + re.escape(edu_level) + r'\b', text, re.IGNORECASE):
                education.append(edu_level)

        return education

    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities"""
        responsibilities = []

        # Look for responsibilities section
        resp_patterns = [
            r'(?:responsibilities|what you.?ll do|key duties)[:\s]+(.*?)(?:\n\n|requirements|qualifications|$)',
            r'(?:you will|you.?ll)[:\s]+(.*?)(?:\n\n|requirements|qualifications|$)',
        ]

        for pattern in resp_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                resp_text = match.group(1)

                # Split by bullet points or newlines
                lines = re.split(r'\n|•|·|-', resp_text)
                for line in lines:
                    line = line.strip()
                    if len(line) > 15 and not line.endswith(':'):
                        responsibilities.append(line)

                break

        return responsibilities[:10]  # Limit to top 10

    def _extract_qualifications(self, text: str) -> List[str]:
        """Extract qualifications"""
        qualifications = []

        # Look for qualifications section
        qual_patterns = [
            r'(?:qualifications|requirements|what we.?re looking for)[:\s]+(.*?)(?:\n\n|responsibilities|$)',
        ]

        for pattern in qual_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                qual_text = match.group(1)

                # Split by bullet points or newlines
                lines = re.split(r'\n|•|·|-', qual_text)
                for line in lines:
                    line = line.strip()
                    if len(line) > 15 and not line.endswith(':'):
                        qualifications.append(line)

                break

        return qualifications[:10]  # Limit to top 10

    def _analyze_job_title(self, text: str) -> Dict[str, Any]:
        """Analyze job title from JD"""
        # Extract first line or look for "Position:" pattern
        lines = text.strip().split('\n')
        potential_title = lines[0] if lines else ""

        title_pattern = r'(?:position|role|job title)[:\s]+(.+?)(?:\n|$)'
        match = re.search(title_pattern, text, re.IGNORECASE)
        if match:
            potential_title = match.group(1).strip()

        # Analyze seniority from title
        seniority = "mid"
        if re.search(r'\b(senior|lead|principal|staff)\b', potential_title, re.IGNORECASE):
            seniority = "senior"
        elif re.search(r'\b(junior|associate|entry)\b', potential_title, re.IGNORECASE):
            seniority = "entry"
        elif re.search(r'\b(architect|fellow|distinguished)\b', potential_title, re.IGNORECASE):
            seniority = "expert"

        return {
            "title": potential_title,
            "seniority_level": seniority
        }

    def _determine_experience_level(self, text: str) -> str:
        """Determine overall experience level"""
        text_lower = text.lower()

        for level, keywords in self.experience_levels.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return level

        return "mid"  # Default

    def _extract_key_keywords(self, text: str) -> List[str]:
        """Extract most important keywords using frequency"""
        if not self.nlp:
            return []

        doc = self.nlp(text.lower())

        # Extract nouns and proper nouns
        keywords = []
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop:
                if len(token.text) > 3:
                    keywords.append(token.text)

        # Get top keywords by frequency
        from collections import Counter
        keyword_freq = Counter(keywords)
        top_keywords = [word for word, count in keyword_freq.most_common(20)]

        return top_keywords

    def _detect_remote_flexibility(self, text: str) -> Dict[str, bool]:
        """Detect if job offers remote work"""
        text_lower = text.lower()

        remote_keywords = ['remote', 'work from home', 'wfh', 'distributed']
        hybrid_keywords = ['hybrid', 'flexible']
        onsite_keywords = ['on-site', 'onsite', 'in-office']

        return {
            "is_remote": any(keyword in text_lower for keyword in remote_keywords),
            "is_hybrid": any(keyword in text_lower for keyword in hybrid_keywords),
            "is_onsite": any(keyword in text_lower for keyword in onsite_keywords),
        }

    async def analyze_with_ai(self, job_description: str) -> Dict[str, Any]:
        """
        Use AI to analyze job description (more accurate)
        """
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not provided")

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)

            prompt = f"""
            Analyze this job description and extract the following in JSON format:
            - job_title
            - required_skills (list with skill name and importance level 1-5)
            - nice_to_have_skills (list)
            - min_experience_years
            - max_experience_years
            - experience_level (entry/mid/senior/expert)
            - required_education (list)
            - responsibilities (list of top 5)
            - key_qualifications (list of top 5)
            - remote_type (remote/hybrid/onsite)

            Job Description:
            {job_description[:4000]}

            Return only valid JSON.
            """

            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert HR analyst. Extract job requirements accurately and return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"AI analysis error: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    analyzer = JobDescriptionAnalyzerAgent()
    sample_jd = """
    Senior Software Engineer - AI/ML

    We are looking for an experienced software engineer with 5+ years of experience
    in building scalable machine learning systems.

    Requirements:
    - Strong programming skills in Python
    - Experience with TensorFlow or PyTorch
    - Knowledge of AWS cloud services
    - Bachelor's degree in Computer Science

    Nice to have:
    - Experience with React
    - Knowledge of Kubernetes
    """
    result = analyzer.analyze(sample_jd)
    print(result)
