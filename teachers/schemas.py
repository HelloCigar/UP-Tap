from ninja import Schema, ModelSchema
from .models import Subjects, ClassSchedule
from typing import List, Optional


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

class SubjectCRUDSchema(Schema):
    subject_id: int = None
    subject_name: str
    schedule: List[str]
    start_time: str
    end_time: str

    
