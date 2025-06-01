from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.

class TeacherManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Create and return a regular user (teacher) with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, first_name, last_name, password, **extra_fields)

class Teacher(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = TeacherManager()
    def __str__(self):
        # use full name
        return f'{self.first_name} {self.last_name} - {self.email}'
    

class Semesters(models.TextChoices):
    FIRST = '1', 'First Semester'
    SECOND = '2', 'Second Semester'
    MIDYEAR = '3', 'Mid Year Semester'

class Subjects(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=100)
    section = models.CharField(max_length=50, blank=True, null=True)  # e.g., 'A', 'B', etc.
    semester = models.CharField(max_length=20, choices=Semesters.choices, default=Semesters.FIRST)
    academic_year = models.CharField(max_length=20, default=f"{datetime.now().year}-{datetime.now().year + 1}")  # e.g., '2023-2024'
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='subjects')

    class Meta:
        unique_together = ('subject_name', 'semester', 'academic_year')

    def __str__(self):
        return f'{self.subject_id} - {self.subject_name}'


class ClassSchedule(models.Model):
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=255)  # e.g., 'Monday', 'Tuesday'
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.subject_id.subject_name} on {self.day_of_week} ({self.start_time} - {self.end_time})"
