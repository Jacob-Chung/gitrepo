# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-04-16 07:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0021_auto_20190416_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$24000$um5fxdN5rVPM$msJ2XEifmlXZNvHzav2Dg14DTTXMMfQAUz8DBKaEw74=', max_length=256),
        ),
    ]
