# -*- coding: utf-8 -*
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class choice_questions(models.Model):
    questionId = models.IntegerField(unique=True, null=False)
    grade = models.FloatField(default=0)
    questionContent = models.TextField()
    questionSection = models.CharField(max_length=128)
    answer1 = models.TextField()
    answer2 = models.TextField()
    answer3 = models.TextField()
    answer4 = models.TextField()
    rightAnswer = models.CharField(max_length=10)
    diff = models.IntegerField(default=1)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.questionContent

    class Meta:
        # ordering = ['c_time']
        verbose_name = '选择题'
        verbose_name_plural = '选择题'


class fillin_questions(models.Model):
    fillinId = models.IntegerField(unique=True, default=1, null=False)
    grade = models.FloatField(default=0)
    fillinContent = models.TextField()
    answer1 = models.TextField()
    answer2 = models.TextField(null=False)
    answer3 = models.TextField(null=False)
    is_order = models.IntegerField()
    fillinSection = models.CharField(max_length=128)
    diff = models.IntegerField(default=1)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '题号：'+str(self.fillinId)+' '+self.fillinContent

    class Meta:
        # ordering = ['c_time']
        verbose_name = '填空题'
        verbose_name_plural = '填空题'


# 出题策略
class question_strategy(models.Model):
    choice_number = models.IntegerField(default=5)
    fillin_number = models.IntegerField(default=5)
    essay_number = models.IntegerField(default=5)
    discuss_number = models.IntegerField(default=5)
    is_final = models.IntegerField(default=0)
    teacher = models.CharField(max_length=128)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.is_final == 0:
            message = '的章节测试'
        else:
            message = '的期末测试'
        return self.teacher + message

    class Meta:
        # ordering = ['c_time']
        verbose_name = '出题策略'
        verbose_name_plural = '出题策略'


# 选择题答案
class choice_ans(models.Model):
    stuId = models.CharField(max_length=255)
    questionId = models.IntegerField(default=1, null=False)
    answer = models.CharField(max_length=255)
    chapter = models.IntegerField(default=0)
    is_final = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '第'+str(self.chapter)+'章'

    class Meta:
        # ordering = ['c_time']
        verbose_name = '选择题答题表'
        verbose_name_plural = '选择题答题表'


# 选择题答案
class compose_choice_ans(models.Model):
    stuId = models.CharField(max_length=255)
    questionId = models.IntegerField(default=1, null=False)
    answer = models.CharField(max_length=255)
    test_name = models.CharField(max_length=255)
    correct = models.IntegerField(default=0)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.test_name

    class Meta:
        # ordering = ['c_time']
        verbose_name = '任务选择题答题表'
        verbose_name_plural = '任务选择题答题表'


# 填空题答案
class fillin_ans(models.Model):
    stuId = models.CharField(max_length=255)
    fillinId = models.IntegerField(default=1, null=False)
    ans1 = models.CharField(max_length=255)
    ans2 = models.CharField(max_length=255)
    ans3 = models.CharField(max_length=255)
    chapter = models.IntegerField(default=0)
    is_final = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '第'+str(self.chapter)+'章'

    class Meta:
        # ordering = ['c_time']
        verbose_name = '填空题答题表'
        verbose_name_plural = '填空题答题表'


# 填空题答案
class compose_fillin_ans(models.Model):
    stuId = models.CharField(max_length=255)
    fillinId = models.IntegerField(default=1, null=False)
    ans1 = models.CharField(max_length=255)
    ans2 = models.CharField(max_length=255)
    ans3 = models.CharField(max_length=255)
    test_name = models.CharField(max_length=255)
    correct = models.IntegerField(default=0)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.test_name

    class Meta:
        # ordering = ['c_time']
        verbose_name = '任务填空题答题表'
        verbose_name_plural = '任务填空题答题表'


class total_grade(models.Model):
    question_name = models.CharField(max_length=255, null=False, default='choice')
    grade = models.FloatField(default=1.0, null=False)

    def __str__(self):
        return str(self.question_name)

    class Meta:
        verbose_name = '总区分度'
        verbose_name_plural = '总区分度'


# 普通成绩表
class score(models.Model):
    stu_Id = models.CharField(max_length=255, unique=True)
    chapter1 = models.IntegerField(default=0)
    chapter2 = models.IntegerField(default=0)
    chapter3 = models.IntegerField(default=0)
    chapter4 = models.IntegerField(default=0)
    chapter5 = models.IntegerField(default=0)
    chapter6 = models.IntegerField(default=0)
    chapter7 = models.IntegerField(default=0)
    final = models.IntegerField(default=0)

    def __str__(self):
        return str(self.stu_Id)

    class Meta:
        verbose_name = '普通成绩表'
        verbose_name_plural = '普通成绩表'


# 每章节实际的选择填空题数量
class question_num(models.Model):
    chapter = models.IntegerField(default=1)
    choice = models.IntegerField(default=0)
    fillin = models.IntegerField(default=0)
    teacher = models.CharField(max_length=128)

    def __str__(self):
        if self.chapter == 0:
            return '期末考试'
        else:
            return '第'+str(self.chapter)+'章'

    class Meta:
        verbose_name = '题目数量'
        verbose_name_plural = '题目数量'


class compose_choice(models.Model):
    test_name = models.CharField(max_length=255)
    questionId = models.IntegerField(default=0)
    teacher = models.CharField(max_length=128)

    def __str__(self):
        return self.test_name+'选择题'

    class Meta:
        verbose_name = '选择题自组卷'
        verbose_name_plural = '选择题自组卷'


class compose_fillin(models.Model):
    test_name = models.CharField(max_length=255)
    fillinId = models.IntegerField(default=0)
    teacher = models.CharField(max_length=128)

    def __str__(self):
        return self.test_name+'填空题'

    class Meta:
        verbose_name = '填空题自组卷'
        verbose_name_plural = '填空题自组卷'


# 组卷成绩表
class compose_score(models.Model):
    stu_Id = models.CharField(max_length=255)
    test_name = models.CharField(max_length=255)
    choice = models.IntegerField(default=0)
    fillin = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    teacher = models.CharField(max_length=255)

    def __str__(self):
        return self.stu_Id+self.test_name

    class Meta:
        verbose_name = '组卷成绩表'
        verbose_name_plural = '组卷成绩表'


# 上传图片的模型类(测试用)
class Pictures(models.Model):
    pic = models.ImageField(upload_to='booktest/')

    def __str__(self):
        return self.pic
