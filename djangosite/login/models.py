# -*- coding: utf-8 -*
from __future__ import unicode_literals

from django.contrib.auth.hashers import make_password
from django.db import models
# Create your models here.


class teacher(models.Model):
    gender = (
        ('male', '男'),
        ('female', '女'),
    )

    teacher_id = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32, choices=gender, default='男')
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['c_time']
        verbose_name = '老师'
        verbose_name_plural = '老师'


class student(models.Model):
    gender = (
        ('male', '男'),
        ('female', '女'),
    )
    stu_Id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=128)
    password = models.CharField(max_length=256, default=make_password('123456', None, 'pbkdf2_sha256'))
    stu_major = models.CharField(max_length=256)
    stu_class = models.CharField(max_length=256)
    teacher = models.CharField(max_length=128, default='wang')
    email = models.EmailField()
    sex = models.CharField(max_length=32, choices=gender, default='男')
    pic = models.ImageField(upload_to='student_Pic/')
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['c_time']
        verbose_name = '学生'
        verbose_name_plural = '学生'


class major(models.Model):
    major = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.major

    class Meta:
        verbose_name = '专业'
        verbose_name_plural = '专业'


class stu_class(models.Model):
    major = models.CharField(max_length=256)
    class_name = models.CharField(max_length=256)

    def __str__(self):
        return self.major+self.class_name

    class Meta:
        verbose_name = '班级'
        verbose_name_plural = '班级'


class post(models.Model):
    user_name = models.CharField(max_length=128)
    title = models.CharField(max_length=128)
    content = models.TextField()
    tag = models.CharField(max_length=256)
    support = models.IntegerField(default=0)
    against = models.IntegerField(default=0)
    c_time = models.DateTimeField(auto_now_add=True)
    # student = models.OneToOneField(student)
    is_teacher = models.IntegerField(default=0)
    pic = models.CharField(max_length=256)

    def __str__(self):
        return self.user_name + '-' + self.title

    class Meta:
        ordering = ['c_time']
        verbose_name = '帖子'
        verbose_name_plural = '帖子'


class comment(models.Model):
    user_name = models.CharField(max_length=128)
    post_id = models.IntegerField(default=1)
    content = models.TextField()
    support = models.IntegerField(default=0)
    against = models.IntegerField(default=0)
    c_time = models.DateTimeField(auto_now_add=True)
    # student = models.OneToOneField(student)
    is_teacher = models.IntegerField(default=0)
    pic = models.CharField(max_length=256)

    def __str__(self):
        return self.user_name + '-' + str(self.post_id)

    class Meta:
        ordering = ['c_time']
        verbose_name = '回复'
        verbose_name_plural = '回复'