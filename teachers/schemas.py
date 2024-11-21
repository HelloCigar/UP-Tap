from ninja import Schema, ModelSchema
from .models import Subjects

class SubjectsSchema(ModelSchema):
    class Meta:
        model = Subjects
        exclude = ["teacher"]

