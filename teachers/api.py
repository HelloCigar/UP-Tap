import logging
from ninja import Router, PatchDict
from typing import List
from .models import Subjects
from .schemas import *
from students.models import Student, SubjectEnrollment
from django.shortcuts import get_object_or_404
import datetime
import django

router = Router()


@router.get("/subjects", response=List[SubjectCRUDSchema], auth=None)
def get_subjects(request):
    result = []
    teacher = request.user

    subjects = Subjects.objects.all()

    if teacher.is_authenticated and teacher.is_superuser == False:
        subjects = Subjects.objects.filter(teacher=teacher)

    for subj in subjects:
        qs = subj.classschedule_set.all()
        days = [s.day_of_week for s in qs]
        # assume all entries share the same times
        if qs:
            st = qs[0].start_time.strftime("%H:%M")
            et = qs[0].end_time.strftime("%H:%M")
        else:
            st = et = ""
        result.append({
            "subject_id": subj.subject_id,
            "subject_name": subj.subject_name,
            "schedule": days,
            "start_time": st,
            "end_time": et,
        })
    return result

@router.post("/subjects")
def create_subject(request, payload: SubjectCRUDSchema):
    start_time = datetime.datetime.strptime(payload.start_time, "%H:%M").time()
    end_time = datetime.datetime.strptime(payload.end_time, "%H:%M").time()

    # 2) create the subject
    subj = Subjects.objects.create(
        subject_name=payload.subject_name,
        teacher=request.user,
    )

    # 3) parse times
    start = datetime.time.fromisoformat(payload.start_time)
    end   = datetime.time.fromisoformat(payload.end_time)

    # 4) create one ClassSchedule per selected day
    for day in payload.schedule:
        ClassSchedule.objects.create(
            subject_id=subj,
            day_of_week=day,
            start_time=start_time,
            end_time=end_time,
        )


    return {"subject_id": subj.subject_id}


@router.get("/subjects/{subject_id}", response=SubjectCRUDSchema)
def get_subject(request, subject_id: int):
    subj = get_object_or_404(Subjects, pk=subject_id)
    qs = subj.classschedule_set.all()
    days = [s.day_of_week for s in qs]
    st  = qs[0].start_time.isoformat() if qs else ""
    et  = qs[0].end_time.isoformat() if qs else ""
    return {
        "subject_id": subj.subject_id,
        "subject_name": subj.subject_name,
        "schedule": days,
        "start_time": st,
        "end_time": et,
    }


@router.put("/subjects/{subject_id}")
def update_subject(request, subject_id: int, payload: SubjectCRUDSchema):
    subject = get_object_or_404(Subjects, subject_id=subject_id, teacher=request.user)
    subject.subject_name = payload.subject_name
    subject.save()

    subj = get_object_or_404(Subjects, pk=subject_id)
    subj.subject_name = payload.subject_name
    subj.save()

    # clear out old schedules
    subj.classschedule_set.all().delete()

    # re-create new ones
    start_time = datetime.datetime.strptime(payload.start_time, "%H:%M").time()
    end_time = datetime.datetime.strptime(payload.end_time, "%H:%M").time()
    for day in payload.schedule:
        ClassSchedule.objects.create(
            subject_id=subj,
            day_of_week=day,
            start_time=start_time,
            end_time=end_time,
        )


    return {"success": True}


@router.delete("/subjects/{subject_id}")
def delete_subject(request, subject_id: int):
    subject = get_object_or_404(Subjects, subject_id=subject_id, teacher=request.user)
    SubjectEnrollment.objects.filter(subject_id=subject).delete()
    subject.delete()
    return {"success": True}

