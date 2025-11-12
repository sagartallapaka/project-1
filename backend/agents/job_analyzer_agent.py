from typing import Dict, Any, List
import re


class JobAnalyzerAgent:
    """Agent for analyzing job descriptions and extracting requirements"""
    
    def __init__(self):
        self.skill_categories = {
            "programming_languages": [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'php', 'swift', 'kotlin'
            ],
            "frameworks": [
                'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'fastapi', 'spring', 'laravel'
            ],
            "databases": [
                'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb'
            ],
            "cloud": [
                'aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes', 'terraform'
            ],
            "ai_ml": [
                'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch', 'ai'
            ],
            "soft_skills": [
                'leadership', 'communication', 'teamwork', 'problem solving', 'analytical', 'agile', 'scrum'
            ]
        }
    
    def analyze_job_description(self, job_description: str, job_title: str = "") -> Dict[str, Any]:
        """Analyze job description and extract structured requirements"""
        
        analysis = {
            "required_skills": self._extract_required_skills(job_description),
            "preferred_skills": self._extract_preferred_skills(job_description),
            "experience_required": self._extract_experience_requirement(job_description),
            "education_required": self._extract_education_requirement(job_description),
            "responsibilities": self._extract_responsibilities(job_description),
            "qualifications": self._extract_qualifications(job_description),
            "skill_categories": self._categorize_skills(job_description),
            "seniority_level": self._determine_seniority_level(job_description, job_title),
            "key_requirements": self._extract_key_requirements(job_description)
        }
        
        return analysis
    
    def _extract_required_skills(self, text: str) -> List[str]:
        """Extract required skills from job description"""
        skills = []
        text_lower = text.lower()
        
        # Look for "required" section
        required_section = self._extract_section(text, ["required", "must have", "requirements"])
        
        # Extract skills from all categories
        for category, skill_list in self.skill_categories.items():
            for skill in skill_list:
                if skill in text_lower:
                    # Check if it's in required section
                    if required_section and skill in required_section.lower():
                        skills.append(skill.title())
                    elif any(keyword in text_lower for keyword in ['required', 'must have', 'essential']):
                        skills.append(skill.title())
        
        return list(set(skills))
    
    def _extract_preferred_skills(self, text: str) -> List[str]:
        """Extract preferred/nice-to-have skills"""
        skills = []
        text_lower = text.lower()
        
        # Look for "preferred" section
        preferred_section = self._extract_section(text, ["preferred", "nice to have", "bonus", "plus"])
        
        if preferred_section:
            for category, skill_list in self.skill_categories.items():
                for skill in skill_list:
                    if skill in preferred_section.lower():
                        skills.append(skill.title())
        
        return list(set(skills))
    
    def _extract_experience_requirement(self, text: str) -> Dict[str, Any]:
        """Extract experience requirements"""
        # Patterns for experience
        patterns = [
            r'(\d+)\+?\s*(?:to|\-)\s*(\d+)\s*years?\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'minimum\s+(?:of\s+)?(\d+)\s*years?',
            r'at least\s+(\d+)\s*years?'
        ]
        
        min_years = 0
        max_years = None
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                if isinstance(matches[0], tuple):
                    min_years = int(matches[0][0])
                    max_years = int(matches[0][1]) if len(matches[0]) > 1 else None
                else:
                    min_years = int(matches[0])
                break
        
        return {
            "min_years": min_years,
            "max_years": max_years,
            "description": f"{min_years}+ years" if min_years else "Not specified"
        }
    
    def _extract_education_requirement(self, text: str) -> List[str]:
        """Extract education requirements"""
        education = []
        
        degree_patterns = [
            r'(Bachelor|B\.?S\.?|B\.?A\.?|B\.?Tech|B\.?E\.?)',
            r'(Master|M\.?S\.?|M\.?A\.?|M\.?Tech|MBA)',
            r'(Ph\.?D\.?|Doctorate)',
        ]
        
        for pattern in degree_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches = re.findall(pattern, text, re.IGNORECASE)
                education.extend(matches)
        
        return list(set(education))
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities"""
        responsibilities = []
        
        # Look for responsibilities section
        resp_section = self._extract_section(text, ["responsibilities", "duties", "you will"])
        
        if resp_section:
            # Split by bullet points or newlines
            items = re.split(r'[\n•\-\*]\s*', resp_section)
            responsibilities = [item.strip() for item in items if len(item.strip()) > 20][:5]
        
        return responsibilities
    
    def _extract_qualifications(self, text: str) -> List[str]:
        """Extract qualifications"""
        qualifications = []
        
        # Look for qualifications section
        qual_section = self._extract_section(text, ["qualifications", "requirements", "what we're looking for"])
        
        if qual_section:
            # Split by bullet points or newlines
            items = re.split(r'[\n•\-\*]\s*', qual_section)
            qualifications = [item.strip() for item in items if len(item.strip()) > 20][:5]
        
        return qualifications
    
    def _categorize_skills(self, text: str) -> Dict[str, List[str]]:
        """Categorize skills found in job description"""
        categorized = {}
        text_lower = text.lower()
        
        for category, skill_list in self.skill_categories.items():
            found_skills = []
            for skill in skill_list:
                if skill in text_lower:
                    found_skills.append(skill.title())
            
            if found_skills:
                categorized[category] = found_skills
        
        return categorized
    
    def _determine_seniority_level(self, text: str, job_title: str) -> str:
        """Determine seniority level from job description"""
        text_lower = (text + " " + job_title).lower()
        
        if any(keyword in text_lower for keyword in ['senior', 'lead', 'principal', 'staff', 'architect']):
            return "Senior"
        elif any(keyword in text_lower for keyword in ['junior', 'entry', 'associate', 'graduate']):
            return "Junior"
        elif any(keyword in text_lower for keyword in ['intern', 'internship', 'trainee']):
            return "Intern"
        elif any(keyword in text_lower for keyword in ['mid', 'intermediate']):
            return "Mid-Level"
        else:
            # Check experience requirements
            exp = self._extract_experience_requirement(text)
            if exp['min_years'] >= 5:
                return "Senior"
            elif exp['min_years'] >= 2:
                return "Mid-Level"
            elif exp['min_years'] >= 0:
                return "Junior"
        
        return "Mid-Level"  # Default
    
    def _extract_key_requirements(self, text: str) -> List[str]:
        """Extract top key requirements"""
        key_reqs = []
        
        # Look for must-have patterns
        must_have_patterns = [
            r'must have[:\s]+([^\n]+)',
            r'required[:\s]+([^\n]+)',
            r'essential[:\s]+([^\n]+)'
        ]
        
        for pattern in must_have_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            key_reqs.extend(matches)
        
        return [req.strip() for req in key_reqs[:5]]
    
    def _extract_section(self, text: str, keywords: List[str]) -> str:
        """Extract a section from text based on keywords"""
        text_lower = text.lower()
        
        for keyword in keywords:
            # Find the keyword
            start_idx = text_lower.find(keyword)
            if start_idx != -1:
                # Find the end (next section or end of text)
                end_idx = len(text)
                
                # Look for next section header
                next_sections = ['responsibilities', 'qualifications', 'requirements', 'benefits', 'about']
                for next_section in next_sections:
                    next_idx = text_lower.find(next_section, start_idx + len(keyword))
                    if next_idx != -1 and next_idx < end_idx:
                        end_idx = next_idx
                
                return text[start_idx:end_idx]
        
        return ""
    
    def calculate_match_score(self, candidate_skills: List[str], required_skills: List[str]) -> float:
        """Calculate how well candidate skills match job requirements"""
        if not required_skills:
            return 100.0
        
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        required_skills_lower = [s.lower() for s in required_skills]
        
        matched = sum(1 for skill in required_skills_lower if skill in candidate_skills_lower)
        
        return (matched / len(required_skills)) * 100
