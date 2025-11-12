from typing import Dict, Any, List
from .job_analyzer_agent import JobAnalyzerAgent


class ScreeningAgent:
    """Agent for screening candidates against job requirements"""
    
    def __init__(self):
        self.job_analyzer = JobAnalyzerAgent()
    
    def screen_candidate(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any],
        job_description: str
    ) -> Dict[str, Any]:
        """Screen a candidate against job requirements"""
        
        # Calculate individual scores
        skill_score = self._calculate_skill_match(
            candidate_data.get('skills', []),
            job_requirements.get('required_skills', []),
            job_requirements.get('preferred_skills', [])
        )
        
        experience_score = self._calculate_experience_match(
            candidate_data.get('experience_years', 0),
            job_requirements.get('experience_required', {})
        )
        
        education_score = self._calculate_education_match(
            candidate_data.get('education', []),
            job_requirements.get('education_required', [])
        )
        
        # Calculate overall screening score (weighted average)
        overall_score = (
            skill_score * 0.5 +  # Skills are most important
            experience_score * 0.3 +
            education_score * 0.2
        )
        
        # Generate screening notes
        notes = self._generate_screening_notes(
            skill_score,
            experience_score,
            education_score,
            candidate_data,
            job_requirements
        )
        
        # Determine recommended action
        recommended_action = self._determine_action(overall_score)
        
        return {
            "screening_score": round(overall_score, 2),
            "skill_match_score": round(skill_score, 2),
            "experience_match_score": round(experience_score, 2),
            "education_match_score": round(education_score, 2),
            "screening_notes": notes,
            "recommended_action": recommended_action,
            "strengths": self._identify_strengths(candidate_data, job_requirements),
            "gaps": self._identify_gaps(candidate_data, job_requirements)
        }
    
    def _calculate_skill_match(
        self,
        candidate_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str]
    ) -> float:
        """Calculate skill match score"""
        if not required_skills and not preferred_skills:
            return 100.0
        
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        
        # Required skills matching
        required_score = 0
        if required_skills:
            required_skills_lower = [s.lower() for s in required_skills]
            matched_required = sum(1 for skill in required_skills_lower if skill in candidate_skills_lower)
            required_score = (matched_required / len(required_skills)) * 100
        else:
            required_score = 100
        
        # Preferred skills matching (bonus)
        preferred_score = 0
        if preferred_skills:
            preferred_skills_lower = [s.lower() for s in preferred_skills]
            matched_preferred = sum(1 for skill in preferred_skills_lower if skill in candidate_skills_lower)
            preferred_score = (matched_preferred / len(preferred_skills)) * 20  # Max 20 bonus points
        
        # Total score (required is mandatory, preferred is bonus)
        total_score = min(required_score + preferred_score, 100)
        
        return total_score
    
    def _calculate_experience_match(
        self,
        candidate_experience: float,
        experience_required: Dict[str, Any]
    ) -> float:
        """Calculate experience match score"""
        min_years = experience_required.get('min_years', 0)
        max_years = experience_required.get('max_years')
        
        if min_years == 0:
            return 100.0  # No experience requirement
        
        if candidate_experience >= min_years:
            # Candidate meets minimum requirement
            if max_years and candidate_experience > max_years:
                # Overqualified - slight penalty
                excess = candidate_experience - max_years
                penalty = min(excess * 5, 20)  # Max 20% penalty
                return 100 - penalty
            else:
                return 100.0
        else:
            # Candidate doesn't meet minimum
            gap = min_years - candidate_experience
            score = max(0, 100 - (gap * 20))  # 20% penalty per year gap
            return score
    
    def _calculate_education_match(
        self,
        candidate_education: List[Dict[str, Any]],
        required_education: List[str]
    ) -> float:
        """Calculate education match score"""
        if not required_education:
            return 100.0  # No education requirement
        
        if not candidate_education:
            return 50.0  # No education info provided
        
        # Extract degree levels
        degree_hierarchy = {
            'phd': 4, 'doctorate': 4,
            'master': 3, 'mba': 3, 'ms': 3, 'ma': 3,
            'bachelor': 2, 'bs': 2, 'ba': 2, 'btech': 2, 'be': 2,
            'associate': 1, 'diploma': 1
        }
        
        # Get candidate's highest degree
        candidate_level = 0
        for edu in candidate_education:
            degree = edu.get('degree', '').lower()
            for key, level in degree_hierarchy.items():
                if key in degree:
                    candidate_level = max(candidate_level, level)
        
        # Get required degree level
        required_level = 0
        for req in required_education:
            req_lower = req.lower()
            for key, level in degree_hierarchy.items():
                if key in req_lower:
                    required_level = max(required_level, level)
        
        if candidate_level >= required_level:
            return 100.0
        elif candidate_level == required_level - 1:
            return 75.0  # One level below
        elif candidate_level > 0:
            return 50.0  # Has some education
        else:
            return 25.0  # No matching education
    
    def _generate_screening_notes(
        self,
        skill_score: float,
        experience_score: float,
        education_score: float,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> str:
        """Generate human-readable screening notes"""
        notes = []
        
        # Skills assessment
        if skill_score >= 80:
            notes.append("✓ Strong skill match with job requirements")
        elif skill_score >= 60:
            notes.append("○ Moderate skill match, some gaps present")
        else:
            notes.append("✗ Significant skill gaps identified")
        
        # Experience assessment
        candidate_exp = candidate_data.get('experience_years', 0)
        required_exp = job_requirements.get('experience_required', {}).get('min_years', 0)
        
        if experience_score >= 90:
            notes.append(f"✓ Experience level ({candidate_exp} years) meets/exceeds requirements ({required_exp}+ years)")
        elif experience_score >= 60:
            notes.append(f"○ Experience level ({candidate_exp} years) is close to requirements ({required_exp}+ years)")
        else:
            notes.append(f"✗ Experience level ({candidate_exp} years) below requirements ({required_exp}+ years)")
        
        # Education assessment
        if education_score >= 90:
            notes.append("✓ Education requirements met")
        elif education_score >= 60:
            notes.append("○ Education partially meets requirements")
        else:
            notes.append("✗ Education requirements not fully met")
        
        return " | ".join(notes)
    
    def _determine_action(self, overall_score: float) -> str:
        """Determine recommended action based on score"""
        if overall_score >= 75:
            return "shortlist"
        elif overall_score >= 50:
            return "review"
        else:
            return "reject"
    
    def _identify_strengths(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> List[str]:
        """Identify candidate's strengths for this role"""
        strengths = []
        
        candidate_skills = [s.lower() for s in candidate_data.get('skills', [])]
        required_skills = [s.lower() for s in job_requirements.get('required_skills', [])]
        
        # Check for matching skills
        matched_skills = [s for s in required_skills if s in candidate_skills]
        if len(matched_skills) >= 3:
            strengths.append(f"Strong technical skills: {', '.join(matched_skills[:3])}")
        
        # Check experience
        exp = candidate_data.get('experience_years', 0)
        if exp >= job_requirements.get('experience_required', {}).get('min_years', 0):
            strengths.append(f"Relevant experience: {exp} years")
        
        # Check certifications
        certs = candidate_data.get('certifications', [])
        if certs:
            strengths.append(f"Certifications: {', '.join(certs[:2])}")
        
        # Check projects
        projects = candidate_data.get('projects', [])
        if len(projects) >= 2:
            strengths.append(f"Demonstrated project experience ({len(projects)} projects)")
        
        return strengths[:4]  # Top 4 strengths
    
    def _identify_gaps(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> List[str]:
        """Identify gaps in candidate's profile"""
        gaps = []
        
        candidate_skills = [s.lower() for s in candidate_data.get('skills', [])]
        required_skills = [s.lower() for s in job_requirements.get('required_skills', [])]
        
        # Missing required skills
        missing_skills = [s for s in required_skills if s not in candidate_skills]
        if missing_skills:
            gaps.append(f"Missing skills: {', '.join(missing_skills[:3])}")
        
        # Experience gap
        candidate_exp = candidate_data.get('experience_years', 0)
        required_exp = job_requirements.get('experience_required', {}).get('min_years', 0)
        if candidate_exp < required_exp:
            gap_years = required_exp - candidate_exp
            gaps.append(f"Experience gap: {gap_years} years below requirement")
        
        # Education gap
        if not candidate_data.get('education') and job_requirements.get('education_required'):
            gaps.append("Education information not provided")
        
        return gaps[:3]  # Top 3 gaps
