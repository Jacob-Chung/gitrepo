# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2019-03-20 02:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0004_delete_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teacher_id', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=128)),
                ('password', models.CharField(max_length=256)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('sex', models.CharField(choices=[('male', '\u7537'), ('female', '\u5973')], default='\u7537', max_length=32)),
                ('c_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['c_time'],
                'verbose_name': '\u8001\u5e08',
                'verbose_name_plural': '\u8001\u5e08',
            },
        ),
    ]
