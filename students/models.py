from django.db import models
from teachers.models import Subjects
# Create your models here.

class Student(models.Model):
    student_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    email = models.EmailField(null=True)
    face_data = models.TextField(null=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    def __str__(self):
        return self.full_name()
    
class SubjectEnrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name='enrollments')

    def __str__(self):
        return f'{self.student_id.full_name()} - {self.subject_id.subject_name}'
