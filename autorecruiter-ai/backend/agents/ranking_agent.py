"""
Candidate Ranking Agent - ML-based scoring and ranking
"""
from typing import Dict, List, Any
import numpy as np


class RankingAgent:
    """Ranks candidates using multi-factor scoring"""

    def __init__(self):
        self.weights = {
            "skills_match": 0.40,
            "experience_match": 0.30,
            "education_match": 0.15,
            "fake_detection_score": 0.15
        }

    def rank_candidates(
        self,
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank candidates and assign scores"""
        
        for candidate in candidates:
            candidate["ranking_score"] = self._calculate_ranking_score(candidate)
        
        # Sort by ranking score
        ranked = sorted(candidates, key=lambda x: x["ranking_score"], reverse=True)
        
        # Assign ranks
        for rank, candidate in enumerate(ranked, 1):
            candidate["rank"] = rank
        
        return ranked

    def _calculate_ranking_score(self, candidate: Dict[str, Any]) -> float:
        """Calculate overall ranking score"""
        screening = candidate.get("screening_results", {})
        fake_detection = candidate.get("fake_detection", {})
        
        skills_score = screening.get("skills_match", {}).get("score", 0)
        exp_score = screening.get("experience_match", {}).get("score", 0)
        edu_score = screening.get("education_match", {}).get("score", 0)
        
        # Invert fake detection score (lower is better)
        fake_score = (1 - fake_detection.get("suspicion_score", 0)) * 100
        
        ranking_score = (
            skills_score * self.weights["skills_match"] +
            exp_score * self.weights["experience_match"] +
            edu_score * self.weights["education_match"] +
            fake_score * self.weights["fake_detection_score"]
        )
        
        return round(ranking_score, 2)
