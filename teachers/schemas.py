from ninja import Schema, ModelSchema
from .models import Subjects

class SubjectsSchema(ModelSchema):
    class Meta:
        model = Subjects
        fields = ["subject_id", "subject_name", "section"]


class SubjectCRUDSchema(Schema):
    subject_name: str
    section: str
    
