from django.contrib import admin
from .models import Student, SubjectEnrollment, UPRFID

# Register your models here.
admin.site.register(Student)
admin.site.register(SubjectEnrollment)
admin.site.register(UPRFID)
