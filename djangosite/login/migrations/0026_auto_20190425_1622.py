# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-04-25 08:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0025_auto_20190416_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$24000$Oyl4goEic88J$dr5aBO4k06g8IOH5Z0yXW+R6Dn+nF3RmaRPphedaOoQ=', max_length=256),
        ),
    ]