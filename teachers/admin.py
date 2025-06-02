from django.contrib import admin
from .models import Teacher, ClassSchedule, Subjects, AcademicPeriod, Section
# Register your models here.

admin.site.register(Teacher)
admin.site.register(Subjects)
admin.site.register(ClassSchedule)
admin.site.register(AcademicPeriod)
admin.site.register(Section)
