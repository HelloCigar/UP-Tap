from django.db import models
from teachers.models import Subjects
# Create your models here.

class Student(models.Model):
    student_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=100, default='')
    middle_initial = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    email = models.EmailField(null=True)
    course = models.CharField(max_length=100, default='')
    alt_email = models.EmailField(null=True)
    gender = models.CharField(max_length=100, default='')
    face_data = models.TextField(null=True)

    def full_name(self):
        return f'{self.first_name} {self.middle_initial}. {self.last_name}'
    def last_name_first(self):
        return f'{self.last_name}, {self.first_name} {self.middle_initial}.'
    def __str__(self):
        return f'{self.student_id} - {self.last_name_first()}'
    
class UPRFID(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    rfid_num = models.BigIntegerField(unique=True)

    def __str__(self):
        return f'{self.student} - {self.rfid_num}'

    
class SubjectEnrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name='enrollments')

    def __str__(self):
        return f'{self.student_id.full_name()} - {self.subject_id.subject_name}'
