from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.teacher)
admin.site.register(models.student)
admin.site.register(models.stu_class)
admin.site.register(models.major)
admin.site.register(models.post)
admin.site.register(models.comment)

