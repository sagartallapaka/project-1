"""
Fake Detection Agent
Detects fraudulent or exaggerated claims in resumes
Uses pattern matching, consistency checks, and AI analysis
"""
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime
from dateutil import parser as date_parser
import os


class FakeDetectionAgent:
    """
    Detects fake/suspicious information in resumes
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize fake detector"""
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        # Suspicious patterns
        self.suspicious_keywords = [
            'expert in all', 'master of everything', 'guru', 'ninja',
            'rockstar', '100%', 'perfect', 'best in'
        ]

    def analyze_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to detect fake/suspicious information
        """
        flags = []
        suspicion_score = 0.0

        # Check 1: Employment date consistency
        date_issues = self._check_employment_dates(resume_data.get("work_experience", []))
        if date_issues:
            flags.extend(date_issues)
            suspicion_score += 0.2 * len(date_issues)

        # Check 2: Skills vs Experience alignment
        skills_issues = self._check_skills_experience_alignment(
            resume_data.get("skills", []),
            resume_data.get("total_experience_years", 0)
        )
        if skills_issues:
            flags.extend(skills_issues)
            suspicion_score += 0.15 * len(skills_issues)

        # Check 3: Overly exaggerated claims
        exaggeration_issues = self._check_exaggerations(resume_data.get("raw_text", ""))
        if exaggeration_issues:
            flags.extend(exaggeration_issues)
            suspicion_score += 0.1 * len(exaggeration_issues)

        # Check 4: Education verification
        education_issues = self._check_education_consistency(resume_data.get("education", []))
        if education_issues:
            flags.extend(education_issues)
            suspicion_score += 0.15 * len(education_issues)

        # Check 5: Too many skills for experience level
        skill_overload = self._check_skill_overload(
            len(resume_data.get("skills", [])),
            resume_data.get("total_experience_years", 0)
        )
        if skill_overload:
            flags.append(skill_overload)
            suspicion_score += 0.15

        # Check 6: Generic/copied content
        generic_content = self._check_generic_content(resume_data.get("raw_text", ""))
        if generic_content:
            flags.append(generic_content)
            suspicion_score += 0.1

        # Normalize score to 0-1
        suspicion_score = min(1.0, suspicion_score)

        return {
            "suspicion_score": round(suspicion_score, 3),
            "is_suspicious": suspicion_score > 0.7,
            "risk_level": self._determine_risk_level(suspicion_score),
            "flags": flags,
            "flag_count": len(flags),
            "recommendation": self._generate_recommendation(suspicion_score),
            "detailed_analysis": self._generate_detailed_analysis(flags)
        }

    def _check_employment_dates(self, work_experience: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Check for date inconsistencies in employment history"""
        issues = []

        if not work_experience or len(work_experience) < 2:
            return issues

        # Check for overlapping employment
        for i, job1 in enumerate(work_experience):
            for job2 in work_experience[i+1:]:
                # Simplified check - in production, parse actual dates
                duration1 = job1.get("duration", "")
                duration2 = job2.get("duration", "")

                # Check if both contain years
                years1 = re.findall(r'\d{4}', duration1)
                years2 = re.findall(r'\d{4}', duration2)

                if len(years1) >= 2 and len(years2) >= 2:
                    # Check for overlap
                    start1, end1 = int(years1[0]), int(years1[-1])
                    start2, end2 = int(years2[0]), int(years2[-1])

                    if (start1 <= start2 <= end1) or (start2 <= start1 <= end2):
                        issues.append({
                            "type": "OVERLAPPING_EMPLOYMENT",
                            "severity": "HIGH",
                            "description": f"Overlapping employment periods detected between {job1.get('company')} and {job2.get('company')}"
                        })

        # Check for future dates
        current_year = datetime.now().year
        for job in work_experience:
            years = re.findall(r'\d{4}', job.get("duration", ""))
            for year in years:
                if int(year) > current_year:
                    issues.append({
                        "type": "FUTURE_DATE",
                        "severity": "HIGH",
                        "description": f"Employment date in the future: {year}"
                    })

        # Check for unrealistic duration
        for job in work_experience:
            years = re.findall(r'\d{4}', job.get("duration", ""))
            if len(years) >= 2:
                duration_years = int(years[-1]) - int(years[0])
                if duration_years > 15:
                    issues.append({
                        "type": "UNREALISTIC_DURATION",
                        "severity": "MEDIUM",
                        "description": f"Very long employment duration ({duration_years} years) at {job.get('company')}"
                    })

        return issues

    def _check_skills_experience_alignment(self, skills: List[str], experience_years: float) -> List[Dict[str, str]]:
        """Check if skills align with experience level"""
        issues = []

        if not skills or experience_years == 0:
            return issues

        # Check for too many skills relative to experience
        expected_skills = experience_years * 3  # Rough estimate: 3 new skills per year

        if len(skills) > expected_skills * 2:
            issues.append({
                "type": "EXCESSIVE_SKILLS",
                "severity": "MEDIUM",
                "description": f"{len(skills)} skills listed for {experience_years} years of experience seems excessive"
            })

        # Check for freshers claiming senior-level skills
        if experience_years < 2:
            senior_keywords = ['architect', 'lead', 'expert', 'advanced', 'senior']
            for skill in skills:
                if any(keyword in skill.lower() for keyword in senior_keywords):
                    issues.append({
                        "type": "EXPERIENCE_SKILL_MISMATCH",
                        "severity": "MEDIUM",
                        "description": f"Senior-level skill '{skill}' claimed with only {experience_years} years experience"
                    })
                    break

        return issues

    def _check_exaggerations(self, text: str) -> List[Dict[str, str]]:
        """Check for exaggerated or overly promotional language"""
        issues = []
        text_lower = text.lower()

        for keyword in self.suspicious_keywords:
            if keyword in text_lower:
                issues.append({
                    "type": "EXAGGERATED_CLAIM",
                    "severity": "LOW",
                    "description": f"Suspicious keyword found: '{keyword}'"
                })

        # Check for excessive use of superlatives
        superlatives = ['best', 'greatest', 'perfect', 'flawless', 'unmatched']
        superlative_count = sum(text_lower.count(word) for word in superlatives)

        if superlative_count > 3:
            issues.append({
                "type": "EXCESSIVE_SUPERLATIVES",
                "severity": "LOW",
                "description": f"Excessive use of superlatives ({superlative_count} instances)"
            })

        return issues

    def _check_education_consistency(self, education: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Check education details for inconsistencies"""
        issues = []

        for edu in education:
            details = edu.get("details", "")

            # Check for future graduation dates
            years = re.findall(r'\d{4}', details)
            current_year = datetime.now().year

            for year in years:
                if int(year) > current_year:
                    issues.append({
                        "type": "FUTURE_GRADUATION",
                        "severity": "HIGH",
                        "description": f"Graduation year in the future: {year}"
                    })

                # Check for too old graduation (might be typo)
                if int(year) < 1970:
                    issues.append({
                        "type": "SUSPICIOUS_GRADUATION_YEAR",
                        "severity": "MEDIUM",
                        "description": f"Unusual graduation year: {year}"
                    })

        return issues

    def _check_skill_overload(self, skill_count: int, experience_years: float) -> Optional[Dict[str, str]]:
        """Check if candidate claims too many skills"""
        if experience_years == 0:
            return None

        skills_per_year = skill_count / max(experience_years, 0.5)

        # More than 10 skills per year of experience is suspicious
        if skills_per_year > 10:
            return {
                "type": "SKILL_OVERLOAD",
                "severity": "MEDIUM",
                "description": f"Lists {skill_count} skills with only {experience_years} years experience ({skills_per_year:.1f} skills/year)"
            }

        return None

    def _check_generic_content(self, text: str) -> Optional[Dict[str, str]]:
        """Check for generic/template content"""
        generic_phrases = [
            'hard-working professional',
            'team player with excellent communication skills',
            'seeking challenging opportunity',
            'results-oriented professional',
            'dynamic and motivated'
        ]

        text_lower = text.lower()
        generic_count = sum(1 for phrase in generic_phrases if phrase in text_lower)

        if generic_count >= 3:
            return {
                "type": "GENERIC_CONTENT",
                "severity": "LOW",
                "description": f"Contains {generic_count} generic phrases commonly found in templates"
            }

        return None

    def _determine_risk_level(self, suspicion_score: float) -> str:
        """Determine risk level based on suspicion score"""
        if suspicion_score >= 0.8:
            return "CRITICAL"
        elif suspicion_score >= 0.6:
            return "HIGH"
        elif suspicion_score >= 0.4:
            return "MEDIUM"
        elif suspicion_score >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"

    def _generate_recommendation(self, suspicion_score: float) -> str:
        """Generate recommendation based on suspicion score"""
        if suspicion_score >= 0.8:
            return "REJECT - Multiple red flags detected. Manual verification strongly recommended."
        elif suspicion_score >= 0.6:
            return "REVIEW - Significant concerns identified. Thorough interview and verification needed."
        elif suspicion_score >= 0.4:
            return "PROCEED_WITH_CAUTION - Some concerns present. Verify during interview."
        elif suspicion_score >= 0.2:
            return "MINOR_CONCERNS - A few flags raised but generally acceptable."
        else:
            return "CLEAR - No significant red flags detected."

    def _generate_detailed_analysis(self, flags: List[Dict[str, str]]) -> str:
        """Generate detailed human-readable analysis"""
        if not flags:
            return "Resume appears genuine with no major red flags detected."

        high_severity = [f for f in flags if f.get("severity") == "HIGH"]
        medium_severity = [f for f in flags if f.get("severity") == "MEDIUM"]
        low_severity = [f for f in flags if f.get("severity") == "LOW"]

        analysis = []

        if high_severity:
            analysis.append(f"⚠️  {len(high_severity)} HIGH severity issues detected")
        if medium_severity:
            analysis.append(f"⚡ {len(medium_severity)} MEDIUM severity issues detected")
        if low_severity:
            analysis.append(f"ℹ️  {len(low_severity)} LOW severity issues detected")

        return " | ".join(analysis)

    async def analyze_with_ai(self, resume_text: str) -> Dict[str, Any]:
        """
        Use AI to detect fake/suspicious content (more sophisticated)
        """
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not provided")

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)

            prompt = f"""
            Analyze this resume for fake, exaggerated, or suspicious information.
            Look for:
            1. Date inconsistencies
            2. Overly exaggerated claims
            3. Too many skills for experience level
            4. Generic/copied content
            5. Unrealistic achievements

            Return analysis in JSON format with:
            - suspicion_score (0-1)
            - red_flags (list)
            - concerns (list)
            - recommendation

            Resume:
            {resume_text[:3000]}

            Return only valid JSON.
            """

            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert at detecting fraudulent resumes. Be thorough but fair."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"AI analysis error: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    detector = FakeDetectionAgent()

    resume = {
        "raw_text": "Expert rockstar developer with perfect skills in all technologies...",
        "skills": ["Python", "Java", "C++", "React", "Angular", "Vue", "Node", "Django", "Flask"] * 5,
        "total_experience_years": 2.0,
        "work_experience": [
            {"company": "ABC Corp", "duration": "2020-2023"},
            {"company": "XYZ Inc", "duration": "2021-2024"}
        ],
        "education": [{"details": "B.Tech 2028"}]
    }

    result = detector.analyze_resume(resume)
    print(result)
