from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pytz


class SchedulerAgent:
    """Agent for scheduling interviews and managing calendar"""
    
    def __init__(self):
        self.default_interview_duration = 60  # minutes
        self.default_timezone = "UTC"
        self.buffer_time = 15  # minutes between interviews
    
    def find_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 60,
        timezone: str = "UTC",
        working_hours: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Find available interview slots"""
        
        if working_hours is None:
            working_hours = {
                "start_hour": 9,  # 9 AM
                "end_hour": 17,   # 5 PM
                "working_days": [0, 1, 2, 3, 4]  # Monday to Friday
            }
        
        tz = pytz.timezone(timezone)
        available_slots = []
        
        current_date = start_date
        while current_date <= end_date:
            # Check if it's a working day
            if current_date.weekday() in working_hours["working_days"]:
                # Generate slots for this day
                day_slots = self._generate_day_slots(
                    current_date,
                    working_hours["start_hour"],
                    working_hours["end_hour"],
                    duration_minutes,
                    tz
                )
                available_slots.extend(day_slots)
            
            current_date += timedelta(days=1)
        
        return available_slots
    
    def _generate_day_slots(
        self,
        date: datetime,
        start_hour: int,
        end_hour: int,
        duration_minutes: int,
        timezone: pytz.timezone
    ) -> List[Dict[str, Any]]:
        """Generate interview slots for a single day"""
        slots = []
        
        # Start from the beginning of working hours
        current_time = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end_time = date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        
        while current_time + timedelta(minutes=duration_minutes) <= end_time:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            
            slots.append({
                "start_time": current_time.isoformat(),
                "end_time": slot_end.isoformat(),
                "duration_minutes": duration_minutes,
                "timezone": str(timezone),
                "is_available": True
            })
            
            # Move to next slot (with buffer time)
            current_time = slot_end + timedelta(minutes=self.buffer_time)
        
        return slots
    
    def schedule_interview(
        self,
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        slot: Dict[str, Any],
        interviewers: List[Dict[str, Any]] = None,
        interview_type: str = "video",
        additional_notes: str = ""
    ) -> Dict[str, Any]:
        """Schedule an interview"""
        
        interview_details = {
            "candidate_id": candidate_data.get("id"),
            "candidate_name": candidate_data.get("full_name"),
            "candidate_email": candidate_data.get("email"),
            "job_id": job_data.get("id"),
            "job_title": job_data.get("title"),
            "start_time": slot["start_time"],
            "end_time": slot["end_time"],
            "duration_minutes": slot["duration_minutes"],
            "timezone": slot["timezone"],
            "interview_type": interview_type,  # video, phone, in-person
            "status": "scheduled",
            "interviewers": interviewers or [],
            "meeting_link": self._generate_meeting_link(interview_type),
            "notes": additional_notes,
            "created_at": datetime.now().isoformat()
        }
        
        return interview_details
    
    def _generate_meeting_link(self, interview_type: str) -> Optional[str]:
        """Generate meeting link based on interview type"""
        if interview_type == "video":
            # In production, integrate with Zoom/Google Meet/Teams API
            return f"https://meet.autorecruiter.ai/interview/{datetime.now().timestamp()}"
        elif interview_type == "phone":
            return None
        elif interview_type == "in-person":
            return "Office Address: [To be provided]"
        return None
    
    def reschedule_interview(
        self,
        interview_id: int,
        new_slot: Dict[str, Any],
        reason: str = ""
    ) -> Dict[str, Any]:
        """Reschedule an existing interview"""
        
        return {
            "interview_id": interview_id,
            "new_start_time": new_slot["start_time"],
            "new_end_time": new_slot["end_time"],
            "reschedule_reason": reason,
            "rescheduled_at": datetime.now().isoformat(),
            "status": "rescheduled"
        }
    
    def cancel_interview(
        self,
        interview_id: int,
        reason: str = "",
        cancelled_by: str = "system"
    ) -> Dict[str, Any]:
        """Cancel an interview"""
        
        return {
            "interview_id": interview_id,
            "status": "cancelled",
            "cancellation_reason": reason,
            "cancelled_by": cancelled_by,
            "cancelled_at": datetime.now().isoformat()
        }
    
    def get_interview_reminders(
        self,
        interview_details: Dict[str, Any],
        reminder_times: List[int] = None
    ) -> List[Dict[str, Any]]:
        """Generate interview reminders"""
        
        if reminder_times is None:
            reminder_times = [24 * 60, 60, 15]  # 24 hours, 1 hour, 15 minutes before
        
        interview_time = datetime.fromisoformat(interview_details["start_time"])
        reminders = []
        
        for minutes_before in reminder_times:
            reminder_time = interview_time - timedelta(minutes=minutes_before)
            
            reminders.append({
                "interview_id": interview_details.get("id"),
                "reminder_time": reminder_time.isoformat(),
                "minutes_before": minutes_before,
                "recipient_email": interview_details["candidate_email"],
                "message": self._generate_reminder_message(interview_details, minutes_before)
            })
        
        return reminders
    
    def _generate_reminder_message(
        self,
        interview_details: Dict[str, Any],
        minutes_before: int
    ) -> str:
        """Generate reminder message"""
        
        if minutes_before >= 24 * 60:
            time_desc = f"{minutes_before // (24 * 60)} day(s)"
        elif minutes_before >= 60:
            time_desc = f"{minutes_before // 60} hour(s)"
        else:
            time_desc = f"{minutes_before} minute(s)"
        
        message = f"""
Reminder: Your interview for {interview_details['job_title']} is in {time_desc}.

Interview Details:
- Time: {interview_details['start_time']}
- Duration: {interview_details['duration_minutes']} minutes
- Type: {interview_details['interview_type']}
"""
        
        if interview_details.get('meeting_link'):
            message += f"- Meeting Link: {interview_details['meeting_link']}\n"
        
        return message.strip()
    
    def check_scheduling_conflicts(
        self,
        proposed_slot: Dict[str, Any],
        existing_interviews: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check for scheduling conflicts"""
        
        proposed_start = datetime.fromisoformat(proposed_slot["start_time"])
        proposed_end = datetime.fromisoformat(proposed_slot["end_time"])
        
        conflicts = []
        
        for interview in existing_interviews:
            existing_start = datetime.fromisoformat(interview["start_time"])
            existing_end = datetime.fromisoformat(interview["end_time"])
            
            # Check for overlap
            if (proposed_start < existing_end and proposed_end > existing_start):
                conflicts.append({
                    "interview_id": interview.get("id"),
                    "conflicting_time": f"{interview['start_time']} - {interview['end_time']}",
                    "candidate": interview.get("candidate_name")
                })
        
        return {
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts
        }
    
    def generate_interview_calendar_event(
        self,
        interview_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate calendar event data (for Google Calendar, Outlook, etc.)"""
        
        return {
            "summary": f"Interview: {interview_details['candidate_name']} - {interview_details['job_title']}",
            "description": f"""
Interview with {interview_details['candidate_name']} for {interview_details['job_title']} position.

Type: {interview_details['interview_type']}
Duration: {interview_details['duration_minutes']} minutes

{interview_details.get('notes', '')}
""".strip(),
            "start": {
                "dateTime": interview_details['start_time'],
                "timeZone": interview_details['timezone']
            },
            "end": {
                "dateTime": interview_details['end_time'],
                "timeZone": interview_details['timezone']
            },
            "attendees": [
                {"email": interview_details['candidate_email']}
            ] + [
                {"email": interviewer.get('email')}
                for interviewer in interview_details.get('interviewers', [])
            ],
            "conferenceData": {
                "createRequest": {
                    "requestId": f"interview-{interview_details.get('id', datetime.now().timestamp())}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            } if interview_details['interview_type'] == 'video' else None
        }
    
    def get_interviewer_availability(
        self,
        interviewer_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get interviewer's availability (placeholder for calendar integration)"""
        
        # In production, this would integrate with Google Calendar API or similar
        # For now, return default working hours
        return self.find_available_slots(start_date, end_date)
    
    def optimize_interview_schedule(
        self,
        candidates: List[Dict[str, Any]],
        available_slots: List[Dict[str, Any]],
        priority_scores: Dict[int, float] = None
    ) -> List[Dict[str, Any]]:
        """Optimize interview scheduling based on candidate priority"""
        
        if priority_scores is None:
            priority_scores = {c['id']: 50.0 for c in candidates}
        
        # Sort candidates by priority (highest first)
        sorted_candidates = sorted(
            candidates,
            key=lambda c: priority_scores.get(c['id'], 0),
            reverse=True
        )
        
        scheduled_interviews = []
        used_slots = set()
        
        for candidate in sorted_candidates:
            # Find first available slot
            for i, slot in enumerate(available_slots):
                if i not in used_slots:
                    scheduled_interviews.append({
                        "candidate_id": candidate['id'],
                        "candidate_name": candidate['full_name'],
                        "slot": slot,
                        "priority_score": priority_scores.get(candidate['id'], 0)
                    })
                    used_slots.add(i)
                    break
        
        return scheduled_interviews
