from django.contrib import admin

# Register your models here.
from exercise import models

admin.site.register(models.choice_questions)
admin.site.register(models.fillin_questions)
admin.site.register(models.question_strategy)
admin.site.register(models.choice_ans)
admin.site.register(models.fillin_ans)
admin.site.register(models.total_grade)
admin.site.register(models.Pictures)
admin.site.register(models.score)
admin.site.register(models.question_num)
admin.site.register(models.compose_choice)
admin.site.register(models.compose_fillin)
admin.site.register(models.compose_choice_ans)
admin.site.register(models.compose_fillin_ans)
admin.site.register(models.compose_score)
