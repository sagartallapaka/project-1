from typing import Dict, Any, List, Optional
from datetime import datetime


class ChatbotAgent:
    """Agent for handling candidate queries via chatbot"""
    
    def __init__(self):
        self.knowledge_base = {
            "application_status": {
                "keywords": ["status", "application", "where is my", "track", "progress"],
                "response_template": "Your application for {job_title} is currently in '{status}' stage. {additional_info}"
            },
            "interview_info": {
                "keywords": ["interview", "when", "schedule", "meeting"],
                "response_template": "Your interview is scheduled for {interview_date} at {interview_time}. {interview_details}"
            },
            "company_info": {
                "keywords": ["company", "about", "culture", "values", "mission"],
                "response_template": "We are a leading technology company focused on innovation and excellence. Our mission is to transform the hiring process through AI."
            },
            "job_details": {
                "keywords": ["job", "role", "responsibilities", "requirements", "salary"],
                "response_template": "The {job_title} position involves {job_description}. Required skills include: {required_skills}"
            },
            "timeline": {
                "keywords": ["timeline", "how long", "when will", "decision", "hear back"],
                "response_template": "Our typical hiring process takes 2-3 weeks. You can expect to hear back within {expected_days} days."
            },
            "documents": {
                "keywords": ["document", "resume", "upload", "submit", "certificate"],
                "response_template": "You can upload additional documents through your candidate portal at {portal_url}"
            },
            "contact": {
                "keywords": ["contact", "reach", "email", "phone", "support"],
                "response_template": "You can reach our recruitment team at {contact_email} or call us at {contact_phone}"
            },
            "benefits": {
                "keywords": ["benefits", "perks", "insurance", "vacation", "pto"],
                "response_template": "We offer competitive benefits including health insurance, flexible work arrangements, professional development, and more."
            },
            "location": {
                "keywords": ["location", "office", "remote", "work from home", "hybrid"],
                "response_template": "This position is {work_location}. {location_details}"
            },
            "next_steps": {
                "keywords": ["next", "what happens", "after", "process"],
                "response_template": "The next step in your application process is: {next_step}. {next_step_details}"
            }
        }
        
        self.fallback_responses = [
            "I'm not sure I understand. Could you please rephrase your question?",
            "That's a great question! Let me connect you with our recruitment team for a detailed answer.",
            "I don't have that information right now, but I've noted your query and someone from our team will get back to you soon."
        ]
    
    def process_query(
        self,
        message: str,
        candidate_data: Optional[Dict[str, Any]] = None,
        application_data: Optional[Dict[str, Any]] = None,
        job_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process candidate query and generate response"""
        
        message_lower = message.lower()
        
        # Identify intent
        intent = self._identify_intent(message_lower)
        
        if intent:
            # Generate contextual response
            response = self._generate_response(
                intent,
                candidate_data,
                application_data,
                job_data
            )
        else:
            # Fallback response
            response = self._get_fallback_response()
        
        return {
            "query": message,
            "intent": intent,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "requires_human": intent is None  # Flag for human intervention
        }
    
    def _identify_intent(self, message: str) -> Optional[str]:
        """Identify user intent from message"""
        
        # Score each intent based on keyword matches
        intent_scores = {}
        
        for intent, data in self.knowledge_base.items():
            score = sum(1 for keyword in data["keywords"] if keyword in message)
            if score > 0:
                intent_scores[intent] = score
        
        # Return intent with highest score
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return None
    
    def _generate_response(
        self,
        intent: str,
        candidate_data: Optional[Dict[str, Any]],
        application_data: Optional[Dict[str, Any]],
        job_data: Optional[Dict[str, Any]]
    ) -> str:
        """Generate contextual response based on intent"""
        
        template = self.knowledge_base[intent]["response_template"]
        
        # Prepare context variables
        context = {}
        
        if intent == "application_status" and application_data:
            context = {
                "job_title": job_data.get("title", "the position") if job_data else "the position",
                "status": application_data.get("status", "under review"),
                "additional_info": self._get_status_additional_info(application_data.get("status"))
            }
        
        elif intent == "interview_info" and application_data:
            interview_time = application_data.get("interview_scheduled_at")
            if interview_time:
                context = {
                    "interview_date": interview_time.split("T")[0] if "T" in str(interview_time) else str(interview_time),
                    "interview_time": interview_time.split("T")[1][:5] if "T" in str(interview_time) else "TBD",
                    "interview_details": "Please check your email for the meeting link and additional details."
                }
            else:
                return "Your interview has not been scheduled yet. We'll notify you via email once it's confirmed."
        
        elif intent == "job_details" and job_data:
            context = {
                "job_title": job_data.get("title", "this position"),
                "job_description": job_data.get("description", "various responsibilities")[:200] + "...",
                "required_skills": ", ".join(job_data.get("requirements", {}).get("required_skills", [])[:5])
            }
        
        elif intent == "timeline" and application_data:
            context = {
                "expected_days": self._calculate_expected_days(application_data.get("status"))
            }
        
        elif intent == "documents" and candidate_data:
            context = {
                "portal_url": f"https://autorecruiter.ai/candidate/{candidate_data.get('id', '')}"
            }
        
        elif intent == "contact":
            context = {
                "contact_email": "recruitment@autorecruiter.ai",
                "contact_phone": "+1-800-RECRUIT"
            }
        
        elif intent == "location" and job_data:
            context = {
                "work_location": job_data.get("location", "flexible"),
                "location_details": self._get_location_details(job_data.get("job_type"))
            }
        
        elif intent == "next_steps" and application_data:
            context = {
                "next_step": self._get_next_step(application_data.get("status")),
                "next_step_details": self._get_next_step_details(application_data.get("status"))
            }
        
        # Fill template with context
        response = template
        for key, value in context.items():
            placeholder = "{" + key + "}"
            response = response.replace(placeholder, str(value))
        
        # Remove any unfilled placeholders
        import re
        response = re.sub(r'\{[^}]+\}', '', response)
        
        return response.strip()
    
    def _get_status_additional_info(self, status: str) -> str:
        """Get additional info based on application status"""
        status_info = {
            "submitted": "Our team is reviewing your application.",
            "screening": "Your application is being evaluated by our AI screening system.",
            "shortlisted": "Congratulations! You've been shortlisted. We'll contact you soon for the next steps.",
            "interview_scheduled": "Your interview has been scheduled. Check your email for details.",
            "interviewed": "Thank you for interviewing with us. We're currently making our decision.",
            "selected": "Congratulations! You've been selected. Check your email for the offer details.",
            "rejected": "Unfortunately, we've decided to move forward with other candidates.",
        }
        return status_info.get(status, "We'll keep you updated on any changes.")
    
    def _calculate_expected_days(self, status: str) -> str:
        """Calculate expected days to hear back"""
        timeline = {
            "submitted": "3-5",
            "screening": "2-3",
            "shortlisted": "5-7",
            "interview_scheduled": "1-2",
            "interviewed": "7-10",
        }
        return timeline.get(status, "5-7")
    
    def _get_location_details(self, job_type: str) -> str:
        """Get location details based on job type"""
        details = {
            "remote": "This is a fully remote position. You can work from anywhere.",
            "hybrid": "This is a hybrid position with flexible work-from-home options.",
            "on-site": "This position requires working from our office location.",
        }
        return details.get(job_type, "Please check the job description for location details.")
    
    def _get_next_step(self, status: str) -> str:
        """Get next step based on current status"""
        next_steps = {
            "submitted": "Initial screening",
            "screening": "Shortlisting decision",
            "shortlisted": "Interview scheduling",
            "interview_scheduled": "Interview",
            "interviewed": "Final decision",
        }
        return next_steps.get(status, "We'll notify you of the next steps")
    
    def _get_next_step_details(self, status: str) -> str:
        """Get detailed next step information"""
        details = {
            "submitted": "Your application will be screened within 2-3 business days.",
            "screening": "We'll notify you if you're shortlisted for an interview.",
            "shortlisted": "Our team will reach out to schedule an interview with you.",
            "interview_scheduled": "Please prepare for your interview and check your email for details.",
            "interviewed": "We're reviewing all candidates and will make a decision soon.",
        }
        return details.get(status, "")
    
    def _get_fallback_response(self) -> str:
        """Get fallback response for unrecognized queries"""
        import random
        return random.choice(self.fallback_responses)
    
    def get_suggested_questions(self, candidate_data: Optional[Dict[str, Any]] = None) -> List[str]:
        """Get suggested questions for the candidate"""
        suggestions = [
            "What is the status of my application?",
            "When is my interview scheduled?",
            "What are the next steps in the process?",
            "How long does the hiring process take?",
            "Can I upload additional documents?",
            "What benefits do you offer?",
            "Is this position remote or on-site?",
            "How can I contact the recruitment team?"
        ]
        return suggestions
    
    def log_conversation(
        self,
        candidate_id: int,
        query: str,
        response: str,
        intent: Optional[str]
    ) -> Dict[str, Any]:
        """Log conversation for analytics and improvement"""
        return {
            "candidate_id": candidate_id,
            "query": query,
            "response": response,
            "intent": intent,
            "timestamp": datetime.now().isoformat(),
            "satisfaction_score": None  # Can be updated based on user feedback
        }
