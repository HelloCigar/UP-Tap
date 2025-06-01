import csv
from io import StringIO
from ninja import Router
from ninja.errors import HttpError
from typing import List
from teachers.util_funcs import get_daily_available_slots
from .models import Subjects
from .schemas import *
from students.models import Student, SubjectEnrollment
from django.shortcuts import get_object_or_404
import datetime
from ninja import File
from ninja.files import UploadedFile
from rest_framework.authtoken.models import Token
from django.db import transaction


router = Router()

@router.get("/latest_token/", response={200: TokenSchema}, auth=None)
def get_latest_token(request):
    # get the latest token by login time
    latest_token = Token.objects.all().order_by('-created').first()
    return {"token": latest_token.key}

@router.get("/subjects", response=List[SubjectCRUDSchema])
def get_subjects(request):
    result = []
    teacher = request.user

    subjects = Subjects.objects.all()

    if teacher.is_superuser == False:
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
            "section" : subj.section,
            "semester": subj.semester,
            "academic_year": subj.academic_year,
        })
    return result

@router.get("/subjects/noauth", response=List[SubjectCRUDSchema], auth=None)
def get_subjects_noauth(request):
    result =[]
    subjects = Subjects.objects.all()
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

@router.get("/subjects/availabletimeslots")
def get_available_time_slots(request):
    slots_by_day = get_daily_available_slots()  # your utility from earlier
    # Transform dict into list of schemas
    return [
        {"day_of_week": day, "free_slots": [
            {"start": s, "end": e} for s, e in slots
        ]}
        for day, slots in slots_by_day.items()
    ]


@router.post("/upload-classlist")
def upload_classlist(request, subject_id: int, file: UploadedFile = File(...)):
    # Decode and parse CSV
    try:
        raw = file.read()
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        raise HttpError(400, "Unable to decode file as UTF-8.")

    buffer = StringIO(text)
    reader = csv.DictReader(buffer)

    subject = get_object_or_404(Subjects, pk=subject_id)

    created_students = updated_students = new_enrollments = 0

    with transaction.atomic():
        for idx, row in enumerate(reader, start=2):  # start=2 to account for header row
            # Validate and normalize student_id
            raw_id = row.get('student_id', '').strip()
            if not raw_id.isdigit():
                raise HttpError(400, f"Invalid student_id '{raw_id}' at CSV line {idx}. Must be an integer.")
            sid = int(raw_id)

            # Build student data dict
            student_data = {
                'first_name':     row['first_name'].strip(),
                'middle_initial': row['middle_initial'].strip(),
                'last_name':      row['last_name'].strip(),
                'gender':         row['gender'].strip(),
                'course':         row['course'].strip(),
                'email':          row['email'].strip() or None,
                'alt_email':      row['alt_email'].strip() or None,
            }

            # Create or update Student
            student, created = Student.objects.update_or_create(
                student_id=sid,
                defaults=student_data
            )
            if created:
                created_students += 1
            else:
                updated_students += 1

            # Enroll student, avoiding duplicates
            enrollment, enrolled = SubjectEnrollment.objects.get_or_create(
                student_id=student,
                subject_id=subject
            )
            if enrolled:
                new_enrollments += 1

    return {
        "message": (
            f"Import complete. "
            f"Students created: {created_students}, updated: {updated_students}. "
            f"New enrollments: {new_enrollments}."
        )
    }


@router.post("/subjects")
def create_subject(request, payload: SubjectCRUDSchema):
    start_time = datetime.datetime.strptime("07:00" if payload.start_time == "" else payload.start_time, "%H:%M").time()
    end_time = datetime.datetime.strptime("08:00" if payload.end_time == "" else payload.end_time, "%H:%M").time()

    # 1 check if start and end time are in conflict with existing schedules
    for day in payload.schedule:
        qs = ClassSchedule.objects.all().filter(day_of_week=day)
        for sched in qs:
            if sched.start_time <= start_time < sched.end_time or sched.start_time < end_time <= sched.end_time:
                raise HttpError(400, "Time schedule conflict, please try again")

    

    # 2) create the subject
    subj = Subjects.objects.create(
        subject_name=payload.subject_name,
        teacher=request.user,
        section=payload.section,
    )

    # 3) create the schedules
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
        "section": subj.section,
        "semester": subj.semester,
        "academic_year": subj.academic_year,
        "schedule": days,
        "start_time": st,
        "end_time": et,
    }


@router.put("/subjects/{subject_id}")
def update_subject(request, subject_id: int, payload: SubjectCRUDSchema):
    start_time = datetime.datetime.strptime("07:00" if payload.start_time == "" else payload.start_time, "%H:%M").time()
    end_time = datetime.datetime.strptime("08:00" if payload.end_time == "" else payload.end_time, "%H:%M").time()
    
    for day in payload.schedule:
        #check if start and end time are in conflict with existing schedules
        # but exclude the current subject
        qs = ClassSchedule.objects.all().exclude(subject_id=subject_id).filter(day_of_week=day)
        for sched in qs:
            if sched.start_time <= start_time < sched.end_time or sched.start_time < end_time <= sched.end_time:
                raise HttpError(400, "Time schedule conflict, please try again")
            
    subject = get_object_or_404(Subjects, subject_id=subject_id, teacher=request.user)
    subject.subject_name = payload.subject_name
    subject.section = payload.section
    subject.save()

    subj = get_object_or_404(Subjects, pk=subject_id)
    subj.subject_name = payload.subject_name
    subj.section = payload.section
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


