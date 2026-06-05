from dataclasses import asdict, dataclass
from datetime import datetime

import settings


@dataclass
class ExamProfile:
    """Basic session metadata for a university-style monitoring report."""

    student_name: str = "Demo Student"
    student_id: str = "000000"
    course_name: str = "AI / Computer Vision"
    exam_name: str = "Local Monitoring Prototype"
    instructor_name: str = "Course Instructor"
    room_name: str = "Local Webcam"
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat(timespec="seconds")

    def to_dict(self):
        return asdict(self)


def collect_exam_profile():
    """Collect optional metadata without making the app hard to run."""
    if not settings.PROMPT_EXAM_PROFILE:
        print("Using default demo exam profile. Set PROMPT_EXAM_PROFILE=True in settings.py to enter details.")
        return ExamProfile()

    print("\nExam Profile")
    print("Leave any field empty to use the default demo value.")

    profile = ExamProfile()
    try:
        values = {
            "student_name": input(f"Student name [{profile.student_name}]: ").strip(),
            "student_id": input(f"Student ID [{profile.student_id}]: ").strip(),
            "course_name": input(f"Course name [{profile.course_name}]: ").strip(),
            "exam_name": input(f"Exam name [{profile.exam_name}]: ").strip(),
            "instructor_name": input(f"Instructor name [{profile.instructor_name}]: ").strip(),
            "room_name": input(f"Room / camera [{profile.room_name}]: ").strip(),
        }
    except EOFError:
        print("No interactive input detected. Using default demo exam profile.")
        return profile

    for key, value in values.items():
        if value:
            setattr(profile, key, value)
    return profile
