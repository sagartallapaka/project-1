from typing import Dict, Any, List, Tuple
import re
from datetime import datetime


class FakeDetectionAgent:
    """Agent for detecting fake or suspicious claims in resumes"""
    
    def __init__(self):
        self.suspicious_patterns = {
            "unrealistic_experience": {
                "description": "Experience claims that seem unrealistic",
                "weight": 0.3
            },
            "inconsistent_dates": {
                "description": "Date inconsistencies in work history",
                "weight": 0.25
            },
            "skill_overload": {
                "description": "Unrealistic number of skills claimed",
                "weight": 0.15
            },
            "generic_descriptions": {
                "description": "Generic or template-like descriptions",
                "weight": 0.15
            },
            "missing_details": {
                "description": "Lack of specific details in claims",
                "weight": 0.15
            }
        }
    
    def detect_fake_claims(
        self,
        candidate_data: Dict[str, Any],
        resume_text: str
    ) -> Dict[str, Any]:
        """Analyze resume for fake or suspicious claims"""
        
        flags = []
        suspicion_scores = {}
        details = {}
        
        # Run all detection checks
        checks = [
            self._check_unrealistic_experience,
            self._check_date_inconsistencies,
            self._check_skill_overload,
            self._check_generic_content,
            self._check_missing_details,
            self._check_education_claims,
            self._check_certification_claims
        ]
        
        for check in checks:
            flag, score, detail = check(candidate_data, resume_text)
            if flag:
                flags.append(flag)
                suspicion_scores[flag] = score
                details[flag] = detail
        
        # Calculate overall fake detection score
        overall_score = self._calculate_overall_score(suspicion_scores)
        
        # Determine if suspicious
        is_suspicious = overall_score >= 60  # Threshold for suspicion
        
        return {
            "fake_detection_score": round(overall_score, 2),
            "is_suspicious": is_suspicious,
            "flags": flags,
            "details": details,
            "recommendation": self._generate_recommendation(overall_score, flags)
        }
    
    def _check_unrealistic_experience(
        self,
        candidate_data: Dict[str, Any],
        resume_text: str
    ) -> Tuple[str, float, str]:
        """Check for unrealistic experience claims"""
        experience_years = candidate_data.get('experience_years', 0)
        skills = candidate_data.get('skills', [])
        work_history = candidate_data.get('work_history', [])
        
        issues = []
        score = 0
        
        # Check 1: Too many years of experience for age
        # Assuming minimum age to start working is 18
        current_year = datetime.now().year
        if experience_years > 40:
            issues.append(f"Claimed {experience_years} years of experience (unusually high)")
            score += 30
        
        # Check 2: Too many skills for experience level
        if experience_years < 2 and len(skills) > 20:
            issues.append(f"Junior candidate claiming {len(skills)} skills (suspicious)")
            score += 25
        
        # Check 3: Senior position claims with minimal experience
        if experience_years < 3:
            senior_keywords = ['senior', 'lead', 'principal', 'architect', 'director']
            for work in work_history:
                title = work.get('title', '').lower()
                if any(keyword in title for keyword in senior_keywords):
                    issues.append(f"Senior title '{work.get('title')}' with only {experience_years} years experience")
                    score += 35
        
        # Check 4: Overlapping work experiences
        if len(work_history) >= 2:
            # Simple check for overlapping dates (would need more sophisticated parsing)
            dates_mentioned = re.findall(r'20\d{2}', resume_text)
            if len(dates_mentioned) < len(work_history):
                issues.append("Insufficient date information for work history")
                score += 15
        
        if issues:
            return (
                "unrealistic_experience",
                min(score, 100),
                " | ".join(issues)
            )
        
        return (None, 0, "")
    
    def _check_date_inconsistencies(
        self,
        candidate_data: Dict[str, Any],
        resume_text: str
    ) -> Tuple[str, float, str]:
        """Check for date inconsistencies"""
        work_history = candidate_data.get('work_history', [])
        education = candidate_data.get('education', [])
        
        issues = []
        score = 0
        
        # Extract all years from resume
        years = re.findall(r'(19|20)\d{2}', resume_text)
        years = [int(y) for y in years]
        
        if years:
            min_year = min(years)
            max_year = max(years)
            current_year = datetime.now().year
            
            # Check 1: Future dates
            if max_year > current_year:
                issues.append(f"Future date found: {max_year}")
                score += 40
            
            # Check 2: Very old start dates for young professionals
            experience_years = candidate_data.get('experience_years', 0)
            if experience_years < 5 and (current_year - min_year) > 10:
                issues.append(f"Date range inconsistent with claimed experience")
                score += 30
            
            # Check 3: Gaps in work history
            if len(work_history) >= 2:
                # This is simplified - would need proper date parsing
                if len(years) < len(work_history) * 2:
                    issues.append("Incomplete date information in work history")
                    score += 20
        
        if issues:
            return (
                "inconsistent_dates",
                min(score, 100),
                " | ".join(issues)
            )
        
        return (None, 0, "")
    
    def _check_skill_overload(
        self,
        candidate_data: Dict[str, Any],
        resume_text: str
    ) -> Tuple[str, float, str]:
        """Check for unrealistic number of skills"""
        skills = candidate_data.get('skills', [])
        experience_years = candidate_data.get('experience_years', 0)
        
        issues = []
        score = 0
        
        # Expected skills based on experience
        expected_max_skills = {
            0: 10,   # Entry level
            2: 15,   # Junior
            5: 25,   # Mid-level
            10: 35,  # Senior
            15: 45   # Very senior
        }
        
        # Find appropriate threshold
        threshold = 10
        for years, max_skills in sorted(expected_max_skills.items()):
            if experience_years >= years:
                threshold = max_skills
        
        if len(skills) > threshold * 1.5:  # 50% over expected
            issues.append(f"Claiming {len(skills)} skills with {experience_years} years experience (unusually high)")
            score += 40
        
        # Check for too many diverse skill categories
        skill_categories = self._categorize_skills(skills)
        if len(skill_categories) > 6 and experience_years < 5:
            issues.append(f"Too many diverse skill categories ({len(skill_categories)}) for experience level")
            score += 30
        
        if issues:
            return (
                "skill_overload",
                min(score, 100),
                " | ".join(issues)
            )
        
        return (None, 0, "")
    
    def _check_generic_content(
        self,
        candidate_data: Dict[str, Any],
        resume_text: str
    ) -> Tuple[str, float, str]:
        """Check for generic or template-like content"""
        issues = []
        score = 0
        
        # Common generic phrases
        generic_phrases = [
            'team player',
            'hard worker',
            'fast learner',
            'detail oriented',
            'self motivated',
            'excellent communication skills',
            'responsible for',
            'duties included'
        ]
        
        text_lower = resume_text.lower()
        generic_count = sum(1 for phrase in generic_phrases if phrase in text_lower)
        
        if generic_count >= 5:
            issues.append(f"High use of generic phrases ({generic_count} found)")
            score += 35
        
        # Check for very short descriptions
        work_history = candidate_data.get('work_history', [])
        if work_history:
            short_descriptions = sum(1 for work in work_history 
                                    if len(work.get('title', '')) < 10)
            if short_descriptions > len(work_history) / 2:
                issues.append("Work history lacks detailed descriptions")
                score += 25
        
        # Check for lack of specific achievements
        achievement_keywords = ['achieved', 'improved', 'increased', 'reduced', 'developed', 'led', 'managed']
        achievement_count = sum(1 for keyword in achievement_keywords if keyword in text_lower)
        
        if len(resume_text) > 500 and achievement_count < 2:
            issues.append("Lack of specific achievements or quantifiable results")
            score += 30
        
        if issues:
            return (
                "generic_descriptions",
                min(score, 100),
                " | ".join(issues)
            )
        
        return (None, 0, "")
    
    def _check_missing_details(
        self,
        candidate_data: Dict[str, Any],
        resume_text: str
    ) -> Tuple[str, float, str]:
        """Check for missing important details"""
        issues = []
        score = 0
        
        # Check for missing contact information
        if not candidate_data.get('email'):
            issues.append("Email address not found")
            score += 20
        
        if not candidate_data.get('phone'):
            issues.append("Phone number not found")
            score += 15
        
        # Check for missing work details
        work_history = candidate_data.get('work_history', [])
        if not work_history:
            issues.append("No work history provided")
            score += 30
        else:
            for work in work_history:
                if not work.get('company'):
                    issues.append("Work experience missing company names")
                    score += 20
                    break
        
        # Check for missing education details
        education = candidate_data.get('education', [])
        if not education:
            issues.append("No education information provided")
            score += 25
        
        if issues:
            return (
                "missing_details",
                min(score, 100),
                " | ".join(issues)
            )
        
        return (None, 0, "")
    
    def _check_education_claims(
        self,
        candidate_data: Dict[str, Any],
        resume_text: str
    ) -> Tuple[str, float, str]:
        """Check education claims for inconsistencies"""
        education = candidate_data.get('education', [])
        experience_years = candidate_data.get('experience_years', 0)
        
        issues = []
        score = 0
        
        # Check for multiple advanced degrees in short time
        advanced_degrees = ['phd', 'doctorate', 'master', 'mba']
        advanced_count = sum(1 for edu in education 
                           if any(deg in edu.get('degree', '').lower() for deg in advanced_degrees))
        
        if advanced_count >= 2 and experience_years < 8:
            issues.append(f"Multiple advanced degrees ({advanced_count}) with limited experience")
            score += 35
        
        # Check for PhD with very little experience
        has_phd = any('phd' in edu.get('degree', '').lower() or 'doctorate' in edu.get('degree', '').lower() 
                     for edu in education)
        if has_phd and experience_years < 3:
            issues.append("PhD claimed with minimal work experience (unusual)")
            score += 25
        
        if issues:
            return (
                "education_inconsistency",
                min(score, 100),
                " | ".join(issues)
            )
        
        return (None, 0, "")
    
    def _check_certification_claims(
        self,
        candidate_data: Dict[str, Any],
        resume_text: str
    ) -> Tuple[str, float, str]:
        """Check certification claims"""
        certifications = candidate_data.get('certifications', [])
        experience_years = candidate_data.get('experience_years', 0)
        
        issues = []
        score = 0
        
        # Too many certifications for experience level
        if len(certifications) > 10 and experience_years < 5:
            issues.append(f"Unusually high number of certifications ({len(certifications)}) for experience level")
            score += 30
        
        # Advanced certifications with minimal experience
        advanced_certs = ['architect', 'professional', 'expert', 'advanced']
        advanced_cert_count = sum(1 for cert in certifications 
                                 if any(adv in cert.lower() for adv in advanced_certs))
        
        if advanced_cert_count >= 3 and experience_years < 3:
            issues.append(f"Multiple advanced certifications with limited experience")
            score += 35
        
        if issues:
            return (
                "certification_inconsistency",
                min(score, 100),
                " | ".join(issues)
            )
        
        return (None, 0, "")
    
    def _calculate_overall_score(self, suspicion_scores: Dict[str, float]) -> float:
        """Calculate weighted overall suspicion score"""
        if not suspicion_scores:
            return 0.0
        
        total_weighted_score = 0
        total_weight = 0
        
        for flag, score in suspicion_scores.items():
            weight = self.suspicious_patterns.get(flag, {}).get('weight', 0.1)
            total_weighted_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return (total_weighted_score / total_weight) * 100
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into different domains"""
        categories = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#'],
            'web': ['react', 'angular', 'vue', 'html', 'css'],
            'database': ['sql', 'mongodb', 'postgresql', 'mysql'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'ai_ml': ['machine learning', 'deep learning', 'tensorflow', 'pytorch'],
            'mobile': ['android', 'ios', 'react native', 'flutter']
        }
        
        categorized = {}
        skills_lower = [s.lower() for s in skills]
        
        for category, keywords in categories.items():
            matched = [s for s in skills_lower if any(k in s for k in keywords)]
            if matched:
                categorized[category] = matched
        
        return categorized
    
    def _generate_recommendation(self, score: float, flags: List[str]) -> str:
        """Generate recommendation based on detection results"""
        if score >= 80:
            return "HIGH RISK: Manual verification strongly recommended. Multiple red flags detected."
        elif score >= 60:
            return "MEDIUM RISK: Additional verification recommended. Some suspicious patterns found."
        elif score >= 40:
            return "LOW RISK: Minor concerns detected. Standard verification should suffice."
        else:
            return "MINIMAL RISK: No significant concerns detected."
