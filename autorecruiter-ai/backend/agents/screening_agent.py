"""
Resume Screening Agent
Matches candidate resumes with job requirements using NLP and semantic similarity
"""
import os
from typing import Dict, List, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer


class ScreeningAgent:
    """
    Intelligent screening agent that matches resumes to job descriptions
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize screening agent with sentence transformer"""
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    def screen_candidate(
        self,
        resume_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Screen a candidate against job requirements
        Returns match score and detailed analysis
        """
        # Calculate various match scores
        skills_match = self._calculate_skills_match(
            resume_data.get("skills", []),
            job_requirements.get("required_skills", [])
        )

        experience_match = self._calculate_experience_match(
            resume_data.get("total_experience_years", 0),
            job_requirements.get("experience_requirements", {})
        )

        education_match = self._calculate_education_match(
            resume_data.get("education", []),
            job_requirements.get("education_requirements", [])
        )

        semantic_match = self._calculate_semantic_match(
            resume_data.get("raw_text", ""),
            job_requirements.get("description", "")
        )

        # Calculate weighted overall score
        overall_score = (
            skills_match["score"] * 0.40 +
            experience_match["score"] * 0.30 +
            education_match["score"] * 0.15 +
            semantic_match["score"] * 0.15
        )

        return {
            "overall_match_score": round(overall_score, 2),
            "passed_screening": overall_score >= job_requirements.get("minimum_match_score", 60.0),
            "skills_match": skills_match,
            "experience_match": experience_match,
            "education_match": education_match,
            "semantic_match": semantic_match,
            "recommendation": self._generate_recommendation(overall_score),
            "screening_notes": self._generate_screening_notes(
                skills_match, experience_match, education_match
            )
        }

    def _calculate_skills_match(
        self,
        candidate_skills: List[str],
        required_skills: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate skills match percentage"""
        if not required_skills:
            return {"score": 100.0, "matched": [], "missing": [], "additional": candidate_skills}

        candidate_skills_lower = [s.lower() for s in candidate_skills]
        matched_skills = []
        missing_skills = []

        for req_skill in required_skills:
            skill_name = req_skill.get("skill", "").lower()
            is_required = req_skill.get("is_required", True)

            if skill_name in candidate_skills_lower:
                matched_skills.append(skill_name)
            elif is_required:
                missing_skills.append(skill_name)

        # Calculate score
        required_count = sum(1 for s in required_skills if s.get("is_required", True))
        if required_count == 0:
            score = 100.0
        else:
            score = (len(matched_skills) / required_count) * 100

        # Additional skills
        additional_skills = [
            s for s in candidate_skills_lower
            if s not in [req.get("skill", "").lower() for req in required_skills]
        ]

        return {
            "score": round(score, 2),
            "matched": matched_skills,
            "missing": missing_skills,
            "additional": additional_skills,
            "match_percentage": f"{len(matched_skills)}/{required_count}"
        }

    def _calculate_experience_match(
        self,
        candidate_experience: float,
        experience_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate experience match score"""
        min_years = experience_requirements.get("min_years")
        max_years = experience_requirements.get("max_years")

        if min_years is None:
            return {"score": 100.0, "meets_requirement": True, "details": "No specific requirement"}

        # Calculate score based on how well experience matches
        if candidate_experience >= min_years:
            if max_years is None or candidate_experience <= max_years:
                score = 100.0
                meets_requirement = True
            elif candidate_experience <= max_years + 2:
                # Slightly over-qualified
                score = 90.0
                meets_requirement = True
            else:
                # Significantly over-qualified
                score = 80.0
                meets_requirement = True
        else:
            # Under-qualified
            gap = min_years - candidate_experience
            score = max(0, 100 - (gap * 20))  # Reduce 20 points per year gap
            meets_requirement = False

        return {
            "score": round(score, 2),
            "meets_requirement": meets_requirement,
            "candidate_years": candidate_experience,
            "required_min": min_years,
            "required_max": max_years,
            "details": self._generate_experience_details(candidate_experience, min_years, max_years)
        }

    def _generate_experience_details(self, candidate: float, min_req: float, max_req: Optional[float]) -> str:
        """Generate human-readable experience comparison"""
        if candidate >= min_req:
            if max_req and candidate > max_req:
                return f"Over-qualified: {candidate} years (required: {min_req}-{max_req})"
            return f"Meets requirement: {candidate} years (required: {min_req}+)"
        else:
            gap = min_req - candidate
            return f"Under-qualified by {gap} years (has {candidate}, needs {min_req}+)"

    def _calculate_education_match(
        self,
        candidate_education: List[Dict[str, Any]],
        required_education: List[str]
    ) -> Dict[str, Any]:
        """Calculate education match score"""
        if not required_education:
            return {"score": 100.0, "meets_requirement": True, "details": "No specific requirement"}

        candidate_degrees = [
            edu.get("degree", "").lower() for edu in candidate_education
        ]

        # Check if any required education is present
        meets_requirement = any(
            any(req.lower() in degree for degree in candidate_degrees)
            for req in required_education
        )

        score = 100.0 if meets_requirement else 50.0

        return {
            "score": score,
            "meets_requirement": meets_requirement,
            "candidate_education": candidate_degrees,
            "required_education": required_education,
            "details": "Education requirement met" if meets_requirement else "Education requirement not met"
        }

    def _calculate_semantic_match(
        self,
        resume_text: str,
        job_description: str
    ) -> Dict[str, Any]:
        """Calculate semantic similarity between resume and JD"""
        if not self.model or not resume_text or not job_description:
            return {"score": 50.0, "similarity": 0.5, "details": "Semantic analysis unavailable"}

        try:
            # Get embeddings
            resume_embedding = self.model.encode(resume_text[:2000])  # Limit length
            jd_embedding = self.model.encode(job_description[:2000])

            # Calculate cosine similarity
            similarity = np.dot(resume_embedding, jd_embedding) / (
                np.linalg.norm(resume_embedding) * np.linalg.norm(jd_embedding)
            )

            # Convert similarity (-1 to 1) to score (0 to 100)
            score = ((similarity + 1) / 2) * 100

            return {
                "score": round(score, 2),
                "similarity": round(float(similarity), 4),
                "details": f"Semantic similarity: {similarity:.2%}"
            }

        except Exception as e:
            print(f"Semantic match error: {e}")
            return {"score": 50.0, "similarity": 0.5, "details": f"Error: {str(e)}"}

    def _generate_recommendation(self, score: float) -> str:
        """Generate hiring recommendation based on score"""
        if score >= 85:
            return "STRONG_MATCH"
        elif score >= 70:
            return "GOOD_MATCH"
        elif score >= 60:
            return "MODERATE_MATCH"
        elif score >= 40:
            return "WEAK_MATCH"
        else:
            return "NO_MATCH"

    def _generate_screening_notes(
        self,
        skills_match: Dict,
        experience_match: Dict,
        education_match: Dict
    ) -> str:
        """Generate detailed screening notes"""
        notes = []

        # Skills analysis
        if skills_match["missing"]:
            notes.append(f"Missing required skills: {', '.join(skills_match['missing'][:3])}")
        if skills_match["matched"]:
            notes.append(f"Strong skills match: {skills_match['match_percentage']}")

        # Experience analysis
        if not experience_match["meets_requirement"]:
            notes.append(experience_match["details"])

        # Education analysis
        if not education_match["meets_requirement"]:
            notes.append("Does not meet education requirements")

        return " | ".join(notes) if notes else "Good overall match"

    def batch_screen_candidates(
        self,
        resumes: List[Dict[str, Any]],
        job_requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Screen multiple candidates at once
        """
        results = []

        for resume in resumes:
            result = self.screen_candidate(resume, job_requirements)
            result["candidate_id"] = resume.get("candidate_id")
            results.append(result)

        # Sort by overall score
        results.sort(key=lambda x: x["overall_match_score"], reverse=True)

        return results


# Example usage
if __name__ == "__main__":
    agent = ScreeningAgent()

    resume = {
        "candidate_id": 1,
        "skills": ["Python", "Machine Learning", "TensorFlow", "AWS"],
        "total_experience_years": 5.5,
        "education": [{"degree": "B.Tech Computer Science"}],
        "raw_text": "Experienced ML engineer with expertise in deep learning..."
    }

    job_req = {
        "required_skills": [
            {"skill": "Python", "is_required": True},
            {"skill": "Machine Learning", "is_required": True},
            {"skill": "AWS", "is_required": False}
        ],
        "experience_requirements": {"min_years": 5, "max_years": 7},
        "education_requirements": ["B.Tech", "B.E."],
        "description": "Looking for an ML engineer with strong Python skills...",
        "minimum_match_score": 60.0
    }

    result = agent.screen_candidate(resume, job_req)
    print(result)
