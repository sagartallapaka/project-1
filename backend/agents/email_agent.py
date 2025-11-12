from typing import Dict, Any, Optional
from datetime import datetime
import re


class EmailAgent:
    """Agent for generating and sending automated emails"""
    
    def __init__(self):
        self.default_templates = {
            "application_received": {
                "subject": "Application Received - {job_title}",
                "body": """Dear {candidate_name},

Thank you for applying for the {job_title} position at {company_name}.

We have received your application and our team is currently reviewing it. We appreciate your interest in joining our team.

You can track your application status at: {tracking_url}

If you have any questions, please don't hesitate to reach out.

Best regards,
{company_name} Recruitment Team"""
            },
            "shortlisted": {
                "subject": "Great News! You've Been Shortlisted - {job_title}",
                "body": """Dear {candidate_name},

Congratulations! We're pleased to inform you that your application for the {job_title} position has been shortlisted.

Your profile stood out among many applicants, and we would like to proceed to the next stage of our hiring process.

{next_steps}

We look forward to learning more about you.

Best regards,
{company_name} Recruitment Team"""
            },
            "interview_invite": {
                "subject": "Interview Invitation - {job_title}",
                "body": """Dear {candidate_name},

We are excited to invite you for an interview for the {job_title} position at {company_name}.

Interview Details:
- Date: {interview_date}
- Time: {interview_time}
- Duration: {interview_duration}
- Format: {interview_format}
- Meeting Link: {meeting_link}

Please confirm your availability by replying to this email.

{interview_instructions}

We look forward to speaking with you!

Best regards,
{company_name} Recruitment Team"""
            },
            "selected": {
                "subject": "Congratulations! Job Offer - {job_title}",
                "body": """Dear {candidate_name},

Congratulations! We are delighted to offer you the position of {job_title} at {company_name}.

We were impressed by your skills, experience, and the value you can bring to our team.

{offer_details}

Please review the attached offer letter and let us know your decision by {response_deadline}.

We're excited about the possibility of you joining our team!

Best regards,
{company_name} Recruitment Team"""
            },
            "rejected": {
                "subject": "Update on Your Application - {job_title}",
                "body": """Dear {candidate_name},

Thank you for your interest in the {job_title} position at {company_name} and for taking the time to apply.

After careful consideration, we have decided to move forward with other candidates whose qualifications more closely match our current needs.

We were impressed by your background and encourage you to apply for future opportunities that align with your skills and experience.

We wish you all the best in your job search.

Best regards,
{company_name} Recruitment Team"""
            },
            "rejected_after_interview": {
                "subject": "Update on Your Application - {job_title}",
                "body": """Dear {candidate_name},

Thank you for taking the time to interview for the {job_title} position at {company_name}. We enjoyed learning more about your experience and skills.

After careful consideration, we have decided to move forward with another candidate for this position.

This was a difficult decision as we had many qualified candidates. We were impressed by your {positive_feedback} and encourage you to apply for future opportunities.

We wish you continued success in your career.

Best regards,
{company_name} Recruitment Team"""
            },
            "on_hold": {
                "subject": "Application Status Update - {job_title}",
                "body": """Dear {candidate_name},

Thank you for your patience during our hiring process for the {job_title} position.

We wanted to update you that your application is currently on hold as we are still reviewing all candidates. We expect to make a decision by {expected_decision_date}.

We appreciate your continued interest and will keep you informed of any updates.

Best regards,
{company_name} Recruitment Team"""
            }
        }
    
    def generate_email(
        self,
        template_type: str,
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Generate personalized email from template"""
        
        template = self.default_templates.get(template_type)
        if not template:
            raise ValueError(f"Unknown template type: {template_type}")
        
        # Prepare variables for template
        variables = {
            "candidate_name": candidate_data.get("full_name", "Candidate"),
            "job_title": job_data.get("title", "Position"),
            "company_name": job_data.get("company_name", "Our Company"),
            "tracking_url": f"https://autorecruiter.ai/track/{candidate_data.get('id', '')}",
        }
        
        # Add additional data if provided
        if additional_data:
            variables.update(additional_data)
        
        # Fill in template
        subject = self._fill_template(template["subject"], variables)
        body = self._fill_template(template["body"], variables)
        
        return {
            "subject": subject,
            "body": body,
            "to_email": candidate_data.get("email"),
            "to_name": candidate_data.get("full_name")
        }
    
    def _fill_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Fill template with variables"""
        result = template
        
        for key, value in variables.items():
            placeholder = "{" + key + "}"
            result = result.replace(placeholder, str(value) if value else "")
        
        # Remove any unfilled placeholders
        result = re.sub(r'\{[^}]+\}', '', result)
        
        return result
    
    def send_application_received_email(
        self,
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Send application received confirmation"""
        return self.generate_email("application_received", candidate_data, job_data)
    
    def send_shortlist_email(
        self,
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        next_steps: str = "Our team will contact you soon to schedule an interview."
    ) -> Dict[str, str]:
        """Send shortlist notification"""
        return self.generate_email(
            "shortlisted",
            candidate_data,
            job_data,
            {"next_steps": next_steps}
        )
    
    def send_interview_invite(
        self,
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        interview_details: Dict[str, Any]
    ) -> Dict[str, str]:
        """Send interview invitation"""
        return self.generate_email(
            "interview_invite",
            candidate_data,
            job_data,
            interview_details
        )
    
    def send_selection_email(
        self,
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        offer_details: str = "Please find the detailed offer letter attached.",
        response_deadline: str = "7 days"
    ) -> Dict[str, str]:
        """Send job offer email"""
        return self.generate_email(
            "selected",
            candidate_data,
            job_data,
            {
                "offer_details": offer_details,
                "response_deadline": response_deadline
            }
        )
    
    def send_rejection_email(
        self,
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        after_interview: bool = False,
        positive_feedback: str = ""
    ) -> Dict[str, str]:
        """Send rejection email"""
        template_type = "rejected_after_interview" if after_interview else "rejected"
        additional_data = {"positive_feedback": positive_feedback} if after_interview else None
        
        return self.generate_email(
            template_type,
            candidate_data,
            job_data,
            additional_data
        )
    
    def create_bulk_emails(
        self,
        template_type: str,
        candidates: list[Dict[str, Any]],
        job_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> list[Dict[str, str]]:
        """Generate bulk emails for multiple candidates"""
        emails = []
        
        for candidate in candidates:
            try:
                email = self.generate_email(
                    template_type,
                    candidate,
                    job_data,
                    additional_data
                )
                emails.append(email)
            except Exception as e:
                print(f"Error generating email for candidate {candidate.get('id')}: {str(e)}")
                continue
        
        return emails
    
    def log_email_sent(
        self,
        application_id: int,
        email_type: str,
        email_data: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create log entry for sent email"""
        return {
            "application_id": application_id,
            "email_type": email_type,
            "subject": email_data.get("subject"),
            "sent_to": email_data.get("to_email"),
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }
