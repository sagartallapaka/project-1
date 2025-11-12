"""
Audit logging model for compliance and tracking
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from . import Base


class AuditLog(Base):
    """Audit log for tracking all important actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Who
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)

    # What
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)  # candidate, job, resume, etc.
    resource_id = Column(Integer, nullable=True)

    # Details
    description = Column(Text, nullable=True)
    changes = Column(JSON, nullable=True)  # Before/after for updates
    metadata = Column(JSON, nullable=True)

    # When
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Context
    request_id = Column(String(100), nullable=True)
    session_id = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.resource_type} by User {self.user_id}>"
