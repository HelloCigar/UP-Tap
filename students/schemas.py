from ninja import Schema, ModelSchema
from .models import Student
from typing import Optional, List

class StudentSchema(ModelSchema):
    class Meta:
        model = Student
        fields = "__all__"

class StudentListSchema(ModelSchema):
    class Meta:
        model = Student
        exclude = ["face_data"]

class StudentEditSchema(Schema):
    first_name:  str
    last_name: str
    email: str
    face_data: str
    subjects: int



class StudentIn(Schema):
    student_id: int
    first_name: Optional[str] = None
    middle_initial: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    alt_email: Optional[str] = None
    course: Optional[str] = None
    gender: Optional[str] = None
    face_data: Optional[str] = None
    subject_ids: List[int]

class StudentOut(Schema):
    student_id: int
    first_name: str
    middle_initial: str
    last_name: str
    email: Optional[str]
    alt_email: Optional[str]
    course: str
    gender: str
    face_data: Optional[str]
