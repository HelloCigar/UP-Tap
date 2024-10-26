from ninja import Schema, ModelSchema
from .models import Student
class StudentSchema(ModelSchema):
    class Meta:
        model = Student
        fields = "__all__"

class StudentListSchema(ModelSchema):
    class Meta:
        model = Student
        exclude = ["face_data"]