from ninja import Router, PatchDict
from typing import List
from .models import Subjects
from .schemas import *
from django.shortcuts import get_object_or_404
import datetime
import django

router = Router()


@router.get("/subjects", response=List[SubjectDetailSchema])
def get_subjects(request):
    teacher = request.user
    subjects = Subjects.objects.filter(teacher=teacher)
    for subject in subjects:
        subject.time_and_schedule = ClassSchedule.objects.filter(subject_id=subject)
    return subjects

@router.post("/subjects")
def create_subject(request, payload: SubjectCRUDSchema):
    subject = Subjects.objects.create(
        subject_name=payload.subject_name,
        teacher=request.user,
    )

    for day_of_week in payload.days:
        # Convert string to datetime object
        try:
            start_time = datetime.datetime.strptime(payload.start_time, "%H:%M").time()
            end_time = datetime.datetime.strptime(payload.end_time, "%H:%M").time()
        except ValueError as e:
            return {"error": f"Invalid time format: {e}"} 
        try:
            ClassSchedule.objects.create(
                subject_id=subject,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
            )
        except django.db.IntegrityError as e:
            return {"error": f"Error creating class schedule: Already set for {day_of_week}"}
    return {"subject_id": subject.subject_id}


@router.get("/subjects/{subject_id}", response=SubjectDetailSchema)
def get_subject(request, subject_id: int):
    subject = get_object_or_404(Subjects, subject_id=subject_id, teacher=request.user)
    subject.time_and_schedule = ClassSchedule.objects.filter(subject_id=subject)
    return subject


@router.put("/subjects/{subject_id}")
def update_subject(request, subject_id: int, payload: SubjectCRUDSchema):
    subject = get_object_or_404(Subjects, subject_id=subject_id, teacher=request.user)
    subject.subject_name = payload.subject_name
    subject.save()

    class_schedule = ClassSchedule.objects.filter(subject_id=subject)
    for schedule in class_schedule:
        schedule.delete()
    for day_of_week in payload.days:
        # Convert string to datetime object
        try:
            start_time = datetime.datetime.strptime(payload.start_time, "%H:%M").time()
            end_time = datetime.datetime.strptime(payload.end_time, "%H:%M").time()
        except ValueError as e:
            return {"error": f"Invalid time format: {e}"} 
        try:
            ClassSchedule.objects.create(
                subject_id=subject,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
            )
        except django.db.IntegrityError as e:
            return {"error": f"Error creating class schedule: Already set for {day_of_week}"}

    return {"success": True}


@router.delete("/subjects/{subject_id}")
def delete_subject(request, subject_id: int):
    subject = get_object_or_404(Subjects, subject_id=subject_id, teacher=request.user)
    subject.delete()
    return {"success": True}

