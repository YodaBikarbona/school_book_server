from django.contrib import admin
from .models import (
    Role,
    Gender,
    User,
    SchoolClass,
    SchoolClassProfessor,
    SchoolClassStudent,
    SchoolSubject,
    ClassRoomSchoolSubject,
    Grade,
    Event,
    Absence
)

# Register your models here.

admin.register(Role)(admin.ModelAdmin)
admin.register(Gender)(admin.ModelAdmin)
admin.register(User)(admin.ModelAdmin)
admin.register(SchoolClass)(admin.ModelAdmin)
admin.register(SchoolClassProfessor)(admin.ModelAdmin)
admin.register(SchoolClassStudent)(admin.ModelAdmin)
admin.register(SchoolSubject)(admin.ModelAdmin)
admin.register(ClassRoomSchoolSubject)(admin.ModelAdmin)
admin.register(Grade)(admin.ModelAdmin)
admin.register(Event)(admin.ModelAdmin)
admin.register(Absence)(admin.ModelAdmin)
