from ninja import Schema, ModelSchema
from .models import Subjects, ClassSchedule
from typing import List, Optional
from datetime import time

class SubjectsSchema(ModelSchema):
    class Meta:
        model = Subjects
        fields = ["subject_id", "subject_name", ]

class SubjectTimeAndSchedule(Schema):
    day_of_week: str
    start_time: str
    end_time: str

class SubjectDetailSchema(Schema):
    subject_id: int = None
    subject_name: str
    time_and_schedule: List[SubjectTimeAndSchedule] = None

class SectionSchema(Schema):
    name: str

class AcademicPeriodSchema(Schema):
    semester: str
    academic_year: str

class SubjectCRUDSchema(Schema):
    subject_id: int = None
    subject_name: str
    schedule: List[str]
    start_time: str = "07:00"
    end_time: str = "08:00"
    section: Optional[str] = None
    semester: Optional[str] = None
    academic_year: Optional[str] = None

class SubjectListSchema(Schema):
    subject_id: int
    subject_name: str
    schedule: List[str]
    start_time: str = "07:00"
    end_time: str = "08:00"   
    section: List[SectionSchema] = None
    period: List[AcademicPeriodSchema] = None

class TimeSlot(Schema):
    start: time
    end: time
    
class AvailableTimeSlotSchema(Schema):
    day_of_week: str
    free_slots: List[TimeSlot]
    
class TokenSchema(Schema):
    token: str