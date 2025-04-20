from ninja import Schema, ModelSchema
from .models import Subjects, ClassSchedule
from typing import List, Optional


class SubjectsSchema(ModelSchema):
    class Meta:
        model = Subjects
        fields = ["subject_id", "subject_name", ]

class SubjectTimeAndSchedule(ModelSchema):
    class Meta:
        model = ClassSchedule
        fields = ["day_of_week", "start_time", "end_time"]

class SubjectDetailSchema(Schema):
    subject_id: int
    subject_name: str
    time_and_schedule: List[SubjectTimeAndSchedule] = None

class SubjectCRUDSchema(Schema):
    subject_name: str
    days: List[str] = None
    start_time: str = None
    end_time: str = None

    
