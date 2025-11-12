from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from models.models import Application


class RankingAgent:
    """Agent for ranking candidates based on multiple factors"""
    
    def __init__(self):
        self.ranking_weights = {
            "screening_score": 0.35,
            "skill_match": 0.25,
            "experience_match": 0.20,
            "education_match": 0.10,
            "fake_detection_penalty": 0.10  # Negative weight
        }
    
    def rank_candidates(
        self,
        applications: List[Application],
        job_requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Rank all candidates for a job"""
        
        ranked_candidates = []
        
        for application in applications:
            ranking_score = self._calculate_ranking_score(application)
            
            ranked_candidates.append({
                "application_id": application.id,
                "candidate_id": application.candidate_id,
                "ranking_score": ranking_score,
                "strengths": self._identify_strengths(application),
                "weaknesses": self._identify_weaknesses(application)
            })
        
        # Sort by ranking score (descending)
        ranked_candidates.sort(key=lambda x: x['ranking_score'], reverse=True)
        
        # Assign ranks
        for rank, candidate in enumerate(ranked_candidates, start=1):
            candidate['rank'] = rank
        
        return ranked_candidates
    
    def _calculate_ranking_score(self, application: Application) -> float:
        """Calculate composite ranking score for a candidate"""
        
        # Get individual scores
        screening_score = application.screening_score or 0
        skill_match = application.skill_match_score or 0
        experience_match = application.experience_match_score or 0
        education_match = application.education_match_score or 0
        fake_detection = application.fake_detection_score or 0
        
        # Calculate weighted score
        ranking_score = (
            screening_score * self.ranking_weights["screening_score"] +
            skill_match * self.ranking_weights["skill_match"] +
            experience_match * self.ranking_weights["experience_match"] +
            education_match * self.ranking_weights["education_match"] -
            fake_detection * self.ranking_weights["fake_detection_penalty"]
        )
        
        # Ensure score is between 0 and 100
        ranking_score = max(0, min(100, ranking_score))
        
        return round(ranking_score, 2)
    
    def _identify_strengths(self, application: Application) -> List[str]:
        """Identify candidate's key strengths"""
        strengths = []
        
        if application.skill_match_score and application.skill_match_score >= 80:
            strengths.append("Excellent skill match")
        
        if application.experience_match_score and application.experience_match_score >= 90:
            strengths.append("Strong relevant experience")
        
        if application.education_match_score and application.education_match_score >= 90:
            strengths.append("Meets education requirements")
        
        if application.fake_detection_score and application.fake_detection_score < 30:
            strengths.append("Verified credentials")
        
        if application.screening_score and application.screening_score >= 85:
            strengths.append("Top performer in screening")
        
        # Add candidate-specific strengths
        if application.candidate:
            if application.candidate.certifications:
                strengths.append(f"Certified professional")
            
            if application.candidate.github_url:
                strengths.append("Active on GitHub")
            
            if application.candidate.projects and len(application.candidate.projects) >= 3:
                strengths.append("Strong project portfolio")
        
        return strengths[:5]  # Top 5 strengths
    
    def _identify_weaknesses(self, application: Application) -> List[str]:
        """Identify candidate's weaknesses or concerns"""
        weaknesses = []
        
        if application.skill_match_score and application.skill_match_score < 60:
            weaknesses.append("Skill gaps present")
        
        if application.experience_match_score and application.experience_match_score < 70:
            weaknesses.append("Limited relevant experience")
        
        if application.education_match_score and application.education_match_score < 70:
            weaknesses.append("Education requirements not fully met")
        
        if application.fake_detection_score and application.fake_detection_score >= 60:
            weaknesses.append("⚠️ Verification concerns")
        
        if application.screening_score and application.screening_score < 60:
            weaknesses.append("Below average screening score")
        
        # Check for missing information
        if application.candidate:
            if not application.candidate.linkedin_url and not application.candidate.github_url:
                weaknesses.append("Limited online presence")
            
            if not application.candidate.projects or len(application.candidate.projects) == 0:
                weaknesses.append("No projects listed")
        
        return weaknesses[:5]  # Top 5 weaknesses
    
    def get_top_candidates(
        self,
        ranked_candidates: List[Dict[str, Any]],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top N candidates"""
        return ranked_candidates[:top_n]
    
    def get_candidates_by_tier(
        self,
        ranked_candidates: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize candidates into tiers"""
        tiers = {
            "tier_1": [],  # Top performers (score >= 80)
            "tier_2": [],  # Strong candidates (score >= 65)
            "tier_3": [],  # Acceptable candidates (score >= 50)
            "tier_4": []   # Below threshold (score < 50)
        }
        
        for candidate in ranked_candidates:
            score = candidate['ranking_score']
            
            if score >= 80:
                tiers["tier_1"].append(candidate)
            elif score >= 65:
                tiers["tier_2"].append(candidate)
            elif score >= 50:
                tiers["tier_3"].append(candidate)
            else:
                tiers["tier_4"].append(candidate)
        
        return tiers
    
    def generate_ranking_report(
        self,
        ranked_candidates: List[Dict[str, Any]],
        job_id: int
    ) -> Dict[str, Any]:
        """Generate comprehensive ranking report"""
        
        tiers = self.get_candidates_by_tier(ranked_candidates)
        
        report = {
            "job_id": job_id,
            "total_candidates": len(ranked_candidates),
            "tier_distribution": {
                "tier_1": len(tiers["tier_1"]),
                "tier_2": len(tiers["tier_2"]),
                "tier_3": len(tiers["tier_3"]),
                "tier_4": len(tiers["tier_4"])
            },
            "top_10_candidates": self.get_top_candidates(ranked_candidates, 10),
            "average_score": sum(c['ranking_score'] for c in ranked_candidates) / len(ranked_candidates) if ranked_candidates else 0,
            "highest_score": ranked_candidates[0]['ranking_score'] if ranked_candidates else 0,
            "lowest_score": ranked_candidates[-1]['ranking_score'] if ranked_candidates else 0,
            "recommended_for_interview": len(tiers["tier_1"]) + len(tiers["tier_2"])
        }
        
        return report
