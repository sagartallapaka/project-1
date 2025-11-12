"""
Email Automation Agent - Sends personalized emails
"""
import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from jinja2 import Template


class EmailAgent:
    """Automated email sending for candidates"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("EMAIL_FROM", self.smtp_user)

    async def send_acceptance_email(
        self,
        candidate: Dict[str, Any],
        job: Dict[str, Any]
    ) -> bool:
        """Send acceptance/selection email"""
        template = """
        Dear {{ candidate_name }},

        Congratulations! We are pleased to inform you that you have been selected 
        for the {{ job_title }} position at {{ company_name }}.

        Our HR team will reach out to you shortly with the next steps.

        Best regards,
        {{ company_name }} Recruitment Team
        """
        
        context = {
            "candidate_name": candidate.get("first_name", "Candidate"),
            "job_title": job.get("title"),
            "company_name": job.get("company_name")
        }
        
        return await self._send_email(
            to_email=candidate.get("email"),
            subject=f"Congratulations - Selected for {job.get('title')}",
            body=Template(template).render(**context)
        )

    async def send_rejection_email(
        self,
        candidate: Dict[str, Any],
        job: Dict[str, Any],
        feedback: Optional[str] = None
    ) -> bool:
        """Send rejection email"""
        template = """
        Dear {{ candidate_name }},

        Thank you for your interest in the {{ job_title }} position at {{ company_name }}.

        After careful consideration, we have decided to move forward with other candidates
        whose qualifications more closely match our current needs.

        We appreciate the time you invested in the application process and wish you 
        success in your job search.

        Best regards,
        {{ company_name }} Recruitment Team
        """
        
        context = {
            "candidate_name": candidate.get("first_name", "Candidate"),
            "job_title": job.get("title"),
            "company_name": job.get("company_name")
        }
        
        return await self._send_email(
            to_email=candidate.get("email"),
            subject=f"Application Update - {job.get('title')}",
            body=Template(template).render(**context)
        )

    async def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> bool:
        """Internal method to send email"""
        try:
            message = MIMEMultipart()
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject
            
            message.attach(MIMEText(body, "plain"))
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )
            
            return True
        except Exception as e:
            print(f"Email send error: {e}")
            return False
