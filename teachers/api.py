from ninja import Router
from ninja import Schema, ModelSchema
from typing import List
from .models import Subjects


router = Router()

class SubjectsSchema(ModelSchema):
    class Meta:
        model = Subjects
        exclude = ["teacher"]


@router.get("/subjects", response=List[SubjectsSchema])
def get_subjects(request):
    teacher = request.user
    return Subjects.objects.filter(teacher=teacher)

