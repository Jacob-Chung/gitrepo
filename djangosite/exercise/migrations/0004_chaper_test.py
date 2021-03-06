# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2019-03-21 07:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exercise', '0003_choice_questions_fillin_questions_question_strategy'),
    ]

    operations = [
        migrations.CreateModel(
            name='chaper_test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stuId', models.CharField(max_length=255, unique=True)),
                ('chapter', models.IntegerField()),
                ('questionId', models.IntegerField()),
                ('choice_answer', models.CharField(max_length=255)),
                ('fillinId', models.IntegerField()),
                ('fillin_answer1', models.TextField()),
                ('fillin_answer2', models.TextField()),
                ('fillin_answer3', models.TextField()),
                ('c_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '\u7ae0\u8282\u7b54\u9898\u8868',
                'verbose_name_plural': '\u7ae0\u8282\u7b54\u9898\u8868',
            },
        ),
    ]
