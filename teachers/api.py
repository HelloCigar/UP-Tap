from ninja import Router, PatchDict
from typing import List
from .models import Subjects
from .schemas import *
from django.shortcuts import get_object_or_404

router = Router()


@router.get("/subjects", response=List[SubjectsSchema])
def get_subjects(request):
    teacher = request.user
    return Subjects.objects.filter(teacher=teacher)

@router.post("/subjects")
def create_subject(request, payload: SubjectCRUDSchema):
    subject = Subjects.objects.create(
        subject_name=payload.subject_name,
        section=payload.section,
        teacher=request.user,
    )
    return {"subject_id": subject.subject_id}


@router.get("/subjects/{subject_id}", response=SubjectCRUDSchema)
def get_subject(request, subject_id: int):
    subject = get_object_or_404(Subjects, subject_id=subject_id, teacher=request.user)
    return subject


@router.put("/subjects/{subject_id}")
def update_subject(request, subject_id: int, payload: PatchDict[SubjectCRUDSchema]):
    subject = get_object_or_404(Subjects, subject_id=subject_id, teacher=request.user)
    for attr, value in payload.items():
        setattr(subject, attr, value)
    subject.save()
    return {"success": True}


@router.delete("/subjects/{subject_id}")
def delete_subject(request, subject_id: int):
    subject = get_object_or_404(Subjects, subject_id=subject_id, teacher=request.user)
    subject.delete()
    return {"success": True}

