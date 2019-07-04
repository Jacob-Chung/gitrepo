# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-03-28 13:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exercise', '0015_auto_20190325_0025'),
    ]

    operations = [
        migrations.CreateModel(
            name='score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stu_Id', models.CharField(max_length=255, unique=True)),
                ('chapter1', models.IntegerField(default=0)),
                ('chapter2', models.IntegerField(default=0)),
                ('chapter3', models.IntegerField(default=0)),
                ('chapter4', models.IntegerField(default=0)),
                ('chapter5', models.IntegerField(default=0)),
                ('chapter6', models.IntegerField(default=0)),
                ('chapter7', models.IntegerField(default=0)),
                ('final', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': '\u6210\u7ee9\u8868',
                'verbose_name_plural': '\u6210\u7ee9\u8868',
            },
        ),
    ]
