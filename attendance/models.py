from django.db import models
from teachers.models import Subjects
from students.models import Student

# Create your models here.
class AttendanceSheet(models.Model):
    sheet_id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    session_date = models.DateField()
    is_active = models.BooleanField(default=False)
    override_start_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.subject_id.subject_name} - {self.session_date}"


class StudentAttendaceInfo(models.Model):
    attendance_info_id = models.AutoField(primary_key=True)
    is_present = models.BooleanField(default=False)
    time_in = models.TimeField(null=True)
    time_out = models.TimeField(null=True)
    sheet_id = models.ForeignKey(AttendanceSheet, on_delete=models.CASCADE)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
        
    def __str__(self):
        return f'{self.student_id.last_name} - {self.sheet_id.subject_id.subject_name} - Time in @ {self.time_in}'
    
