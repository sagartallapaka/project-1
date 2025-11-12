"""
Interview and Feedback models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from . import Base


class InterviewStatus(str, enum.Enum):
    """Interview status enum"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    RESCHEDULED = "rescheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class InterviewType(str, enum.Enum):
    """Interview type enum"""
    PHONE_SCREEN = "phone_screen"
    VIDEO_CALL = "video_call"
    IN_PERSON = "in_person"
    TECHNICAL = "technical"
    HR_ROUND = "hr_round"
    MANAGER_ROUND = "manager_round"
    FINAL_ROUND = "final_round"


class Interview(Base):
    """Interview scheduling model"""
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)

    # Interview Details
    interview_type = Column(SQLEnum(InterviewType), nullable=False)
    interview_round = Column(Integer, default=1)
    status = Column(SQLEnum(InterviewStatus), default=InterviewStatus.SCHEDULED, index=True)

    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(50), default="Asia/Kolkata")

    # Location/Link
    location = Column(String(500), nullable=True)  # Physical address or video link
    meeting_link = Column(String(500), nullable=True)
    meeting_id = Column(String(100), nullable=True)
    meeting_password = Column(String(100), nullable=True)

    # Participants
    interviewer_ids = Column(JSON, nullable=True)  # List of user IDs
    interviewer_names = Column(JSON, nullable=True)  # List of names
    interviewer_emails = Column(JSON, nullable=True)  # List of emails

    # Calendar Integration
    google_calendar_event_id = Column(String(255), nullable=True)
    outlook_calendar_event_id = Column(String(255), nullable=True)

    # Reminders
    reminder_sent_candidate = Column(Boolean, default=False)
    reminder_sent_interviewer = Column(Boolean, default=False)
    reminder_sent_at = Column(DateTime(timezone=True), nullable=True)

    # Instructions
    instructions_for_candidate = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)

    # Rescheduling
    reschedule_count = Column(Integer, default=0)
    reschedule_reason = Column(Text, nullable=True)
    original_scheduled_at = Column(DateTime(timezone=True), nullable=True)

    # Cancellation
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Completion
    completed_at = Column(DateTime(timezone=True), nullable=True)
    actual_duration_minutes = Column(Integer, nullable=True)

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    job = relationship("Job", back_populates="interviews")
    candidate = relationship("Candidate", back_populates="interviews")
    application = relationship("JobApplication", back_populates="interviews")
    feedback = relationship("InterviewFeedback", back_populates="interview", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Interview {self.interview_type.value} - Candidate {self.candidate_id} for Job {self.job_id}>"


class InterviewFeedback(Base):
    """Interview feedback and evaluation"""
    __tablename__ = "interview_feedback"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False, unique=True)

    # Evaluator
    evaluator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    evaluator_name = Column(String(255), nullable=True)

    # Overall Assessment
    overall_rating = Column(Float, nullable=True)  # 1-5 or 1-10
    recommendation = Column(String(50), nullable=True)  # strong_hire, hire, maybe, no_hire, strong_no_hire
    decision = Column(String(50), nullable=True)  # proceed, reject, hold

    # Detailed Ratings
    technical_skills_rating = Column(Float, nullable=True)
    communication_skills_rating = Column(Float, nullable=True)
    problem_solving_rating = Column(Float, nullable=True)
    cultural_fit_rating = Column(Float, nullable=True)
    experience_rating = Column(Float, nullable=True)

    # Structured Feedback
    strengths = Column(JSON, nullable=True)  # List of strengths
    weaknesses = Column(JSON, nullable=True)  # List of weaknesses
    skills_assessed = Column(JSON, nullable=True)  # {skill: rating}

    # Detailed Comments
    detailed_feedback = Column(Text, nullable=True)
    technical_assessment = Column(Text, nullable=True)
    behavioral_assessment = Column(Text, nullable=True)
    additional_notes = Column(Text, nullable=True)

    # Questions Asked
    questions_asked = Column(JSON, nullable=True)  # List of questions
    answers_quality = Column(JSON, nullable=True)  # {question: rating}

    # Concerns & Red Flags
    concerns = Column(JSON, nullable=True)
    red_flags = Column(JSON, nullable=True)

    # Next Steps
    next_steps = Column(Text, nullable=True)
    follow_up_required = Column(Boolean, default=False)

    # Metadata
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    interview = relationship("Interview", back_populates="feedback")

    def __repr__(self):
        return f"<InterviewFeedback for Interview {self.interview_id} - Rating: {self.overall_rating}>"
