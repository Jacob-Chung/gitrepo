# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-04-16 02:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0019_auto_20190416_1020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$24000$OcN1sCvpsENS$JxnY0GbzGeT+ubGF56quE0XY8Y0csPteohTs76PUwNs=', max_length=256),
        ),
    ]
