from django.contrib import admin
from .models import Teacher, ClassSchedule, Subjects
# Register your models here.

admin.site.register(Teacher)
admin.site.register(Subjects)
admin.site.register(ClassSchedule)
