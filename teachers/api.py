from ninja import Router
from typing import List
from .models import Subjects
from .schemas import *

router = Router()


@router.get("/subjects", response=List[SubjectsSchema])
def get_subjects(request):
    teacher = request.user
    return Subjects.objects.filter(teacher=teacher)

