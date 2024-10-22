from django.db import models
from teachers.models import Subjects
from students.models import Student

# Create your models here.

class AttendanceSheet(models.Model):
    sheet_id = models.AutoField(primary_key=True)
    session_date = models.DateField(null=True)
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.session_date)

class StudentAttendaceInfo(models.Model):
    attendance_info_id = models.AutoField(primary_key=True)
    is_present = models.BooleanField()
    time_in = models.TimeField(null=True)
    time_out = models.TimeField(null=True)
    sheet_id = models.ForeignKey(AttendanceSheet, on_delete=models.CASCADE)
    student_id = models.OneToOneField(Student, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.student_id.student_name} - {self.is_present}'
    
