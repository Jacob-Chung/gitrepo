# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-04-25 08:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exercise', '0027_auto_20190425_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='compose_score',
            name='teacher',
            field=models.CharField(default='wang', max_length=255),
            preserve_default=False,
        ),
    ]