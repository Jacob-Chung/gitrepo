# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-03-27 07:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0015_major'),
    ]

    operations = [
        migrations.AlterField(
            model_name='major',
            name='major',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]