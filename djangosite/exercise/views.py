# coding=UTF-8
from __future__ import print_function

import json
import random

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Max

import xlrd
from django.conf import settings

from django.db import transaction
from django.http import response, HttpResponse
# from django.middleware.common import logger
from django.shortcuts import render, redirect

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from logger import logger

import exercise
import login
from exercise import models

# from login.models import IMG
from exercise.models import Pictures
from login.models import student


# test
def tetest(request):
    pass
    return render(request, 'student/tetest.html')


# for test
def select_chapter(request):
    # max_score = models.score.objects.all().aggregate(Max('chapter1'))
    # print(max_score)
    # score = max_score['chapter1__max']
    # print(score)
    list = []
    li = ['jacob', 1, 'male']
    li2 = ['gawain', 2, 'male']
    list.append(li)
    list.append(li2)
    # print(list)
    # for i in list:
    #     print(i[0])
    print(list[0][0])
    return render(request, 'student/select_chapter.html')


# 返回上传图片的页面 for test
def getUpload(request):
    return render(request, 'img_tem/uploading.html')


# for test
def uploadImg(request):
    # 从请求当中　获取文件对象
    f1 = request.FILES.get('picture')
    # 　利用模型类　将图片要存放的路径存到数据库中
    p = Pictures()
    # print(f1)
    p.pic = 'booktest/' + f1.name
    p.save()
    # 在之前配好的静态文件目录static/media/booktest 下 新建一个空文件
    # 然后我们循环把上传的图片写入到新建文件当中
    fname = settings.MEDIA_ROOT + "/booktest/" + f1.name
    with open(fname, 'wb') as pic:
        for c in f1.chunks():
            pic.write(c)
    return HttpResponse("上传成功")


# 显示图片
def show_pic(request):
    pic_obj = Pictures.objects.get(id=1)
    return render(request, 'img_tem/showing.html', {'pic_obj': pic_obj})


# 学生
def my_mission(request):
    this_student = request.session.get('user_id')
    teacher = student.objects.get(stu_Id=this_student).teacher
    test_list1 = models.compose_choice.objects.values('test_name').filter(teacher=teacher).distinct()
    test_list = []
    state_list = []
    for li in test_list1:
        test_list.append(li['test_name'])

    for li in test_list:
        flag1 = models.compose_choice_ans.objects.filter(stuId=this_student, test_name=li)
        flag2 = models.compose_fillin_ans.objects.filter(stuId=this_student, test_name=li)
        if len(flag1) == 0 and len(flag2) == 0:
            state_list.append([li, '否', 0])
        else:
            marks = 0
            for lis in flag1:
                if lis.correct != 0:
                    marks += lis.correct

            for lis1 in flag2:
                if lis1.correct != 0:
                    marks += lis1.correct

            state_list.append([li, '是', marks])

    print(state_list)
    return render(request, 'student/my_mission.html', {'test_list': test_list, 'state_list': state_list})


def do_compose(request):
    from login import models

    # choice_list = exercise.models.choice_questions.objects.all()
    # fillin_list = exercise.models.fillin_questions.objects.all()
    student_id = request.session.get('user_id')

    teacher = login.models.student.objects.get(stu_Id=student_id).teacher

    test_name = request.GET.get('test_name')
    # 选择题
    choice_list = exercise.models.compose_choice.objects.filter(teacher=teacher, test_name=test_name)
    choice_paper = []
    for li in choice_list:
        choice_paper.append(exercise.models.choice_questions.objects.get(questionId=li.questionId))
    # 填空题
    fillin_list = exercise.models.compose_fillin.objects.filter(teacher=teacher, test_name=test_name)
    fillin_paper = []
    for li in fillin_list:
        fillin_paper.append(exercise.models.fillin_questions.objects.get(fillinId=li.fillinId))

    choice_num = len(choice_paper)
    fillin_num = len(fillin_paper)
    return render(request, 'student/do_compose.html',
                  {'choice_paper': choice_paper, 'fillin_paper': fillin_paper, 'test_name': test_name,
                   'choice_num': choice_num, 'fillin_num': fillin_num})


def submit_compose(request):
    test_name = request.POST['test_name']
    stuId = request.session.get('user_id')
    C_list = models.compose_choice_ans.objects.filter(stuId=stuId, test_name=test_name)
    C1_list = models.compose_fillin_ans.objects.filter(stuId=stuId, test_name=test_name)
    choice_number = request.POST['choice_num']
    fillin_number = request.POST['fillin_num']
    # print(C_list)
    if len(C_list) > 0 or len(C1_list):
        message = '您已做过该测试！'
    else:
        # 取出选择题
        choice_total_score = 0
        for i in range(1, int(choice_number) + 1):
            questionId = request.POST['choice_' + str(i) + '_id']
            choice_answer = request.POST['choice_' + str(i)]

            new_choice = models.compose_choice_ans.objects.create()
            new_choice.stuId = stuId
            new_choice.questionId = questionId
            new_choice.answer = choice_answer
            new_choice.test_name = test_name

            if choice_answer == models.choice_questions.objects.get(questionId=questionId).rightAnswer:
                new_choice.correct = 1
                choice_total_score += models.choice_questions.objects.get(questionId=questionId).diff
            else:
                new_choice.correct = 0
            new_choice.save()

            # 对题目、总区分度修改
            count_choice_grade(questionId)

        # 取出填空题
        fillin_total_score = 0
        for i in range(1, int(fillin_number) + 1):
            fillinId = request.POST['fillin_' + str(i) + '_id']
            question = models.fillin_questions.objects.get(fillinId=fillinId)
            diff = question.diff
            if diff == 1:
                fillin_answer1 = request.POST['fillin_' + str(i) + '_answer1']
            elif diff == 2:
                fillin_answer1 = request.POST['fillin_' + str(i) + '_answer1']
                fillin_answer2 = request.POST['fillin_' + str(i) + '_answer2']
            else:
                fillin_answer1 = request.POST['fillin_' + str(i) + '_answer1']
                fillin_answer2 = request.POST['fillin_' + str(i) + '_answer2']
                fillin_answer3 = request.POST['fillin_' + str(i) + '_answer3']

            new_fillin = models.compose_fillin_ans.objects.create()
            new_fillin.stuId = stuId
            new_fillin.fillinId = fillinId
            new_fillin.test_name = test_name
            if diff == 1:
                new_fillin.ans1 = fillin_answer1
                if fillin_answer1 != '' and fillin_answer1 in question.answer1:
                    new_fillin.correct = 1
                    fillin_total_score += 1
                else:
                    new_fillin.correct = 0

            elif diff == 2:
                new_fillin.ans1 = fillin_answer1
                new_fillin.ans2 = fillin_answer2
                order = question.is_order
                fillin_ans = [fillin_answer1, fillin_answer2]
                right_ans = [question.answer1, question.answer2]
                new_fillin.correct = 0
                if order == 1:

                    for num in range(0, 2):
                        if fillin_ans[num] != '' and fillin_ans[num] == right_ans[num]:
                            new_fillin.correct += 1
                            fillin_total_score += 1

                elif order == 0:
                    for num in range(0, 2):
                        for li in right_ans:
                            if fillin_ans[num] != '' and fillin_ans[num] == li:
                                new_fillin.correct += 1
                                fillin_total_score += 1

            elif diff == 3:
                new_fillin.ans1 = fillin_answer1
                new_fillin.ans2 = fillin_answer2
                new_fillin.ans3 = fillin_answer3
                fillin_ans = [fillin_answer1, fillin_answer2, fillin_answer3]
                right_ans = [question.answer1, question.answer2, question.answer3]
                new_fillin.correct = 0

                order = question.is_order
                if order == 1:
                    for num in range(0, 3):
                        if fillin_ans[num] != '' and fillin_ans[num] in right_ans[num]:
                            new_fillin.correct += 1
                            fillin_total_score += 1

                elif order == 0:
                    for num in range(0, 3):
                        for li in right_ans:
                            if fillin_ans[num] != '' and fillin_ans[num] in li:
                                new_fillin.correct += 1
                                fillin_total_score += 1

            new_fillin.save()
            count_fillin_grade(fillinId)

        # 将成绩存入成绩表
        # chapter_list = ['chapter1', 'chapter2', 'chapter3', 'chapter4', 'chapter5', 'chapter6', 'chapter7']
        teacher = student.objects.get(stu_Id=stuId).teacher
        new_score = models.compose_score.objects.create(stu_Id=stuId, test_name=test_name,
                                                        choice=choice_total_score, fillin=fillin_total_score,
                                                        total_score=choice_total_score + fillin_total_score,
                                                        teacher=teacher)
        new_score.save()
        message = '交卷成功'

    return render(request, 'student/do_compose.html', {'message': message, 'test_name': test_name})


def chapter_test(request):
    from login import models
    # chapter = request.GET.get('chapter')

    chapter = 1
    choice_list = exercise.models.choice_questions.objects.filter(questionSection__startswith='01')
    fillin_list = exercise.models.fillin_questions.objects.filter(fillinSection__startswith='01')
    student_id = request.session.get('user_id')

    teacher = login.models.student.objects.get(stu_Id=student_id).teacher
    # print(teacher)

    question_strategy = exercise.models.question_strategy.objects.get(teacher=teacher, is_final=0)
    choice_number = question_strategy.choice_number
    fillin_score = question_strategy.fillin_number

    if choice_number > len(choice_list):
        choice_number = len(choice_list)

    fillin_total_score = 0
    for li in fillin_list:
        fillin_total_score += li.diff

    if fillin_score > fillin_total_score:
        fillin_score = fillin_total_score

    # 选择题取样的间隔，可避免知识点重复
    choice_interval = len(choice_list) / choice_number
    choice_flag = random.randint(1, choice_interval)
    choice_paper = []
    for i in range(1, choice_number + 1):
        choice_paper.append(choice_list[choice_flag - 1])
        choice_flag += choice_interval

    # fillin_number = 0
    while 1:
        fillin_num = random.randint(1, len(fillin_list))
        fillin_paper = random.sample(fillin_list, fillin_num)
        total = 0
        for li in fillin_paper:
            total += li.diff
        # print('我是总分' + str(total))
        if total == fillin_score:
            break

    fillin_num = len(fillin_paper)

    return render(request, 'student/chapter_test.html',
                  {'choice_paper': choice_paper, 'choice_number': choice_number, 'fillin_paper': fillin_paper,
                   'fillin_number': fillin_num, 'chapter': '01', 'fillin_score': fillin_score})


# 改变考试的章节
def change_chapter(request):
    from login import models
    chapter = request.GET.get('chapter')

    choice_list = exercise.models.choice_questions.objects.filter(questionSection__startswith=chapter)
    fillin_list = exercise.models.fillin_questions.objects.filter(fillinSection__startswith=chapter)
    student_id = request.session.get('user_id')

    teacher = login.models.student.objects.get(stu_Id=student_id).teacher
    # print(teacher)

    question_strategy = exercise.models.question_strategy.objects.get(teacher=teacher, is_final=0)
    choice_number = question_strategy.choice_number
    fillin_score = question_strategy.fillin_number

    if choice_number > len(choice_list):
        choice_number = len(choice_list)

    fillin_total_score = 0
    for li in fillin_list:
        fillin_total_score += li.diff

    if fillin_score > fillin_total_score:
        fillin_score = fillin_total_score

    # 选择题取样的间隔，可避免知识点重复
    choice_interval = len(choice_list) / choice_number
    choice_flag = random.randint(1, choice_interval)
    choice_paper = []
    for i in range(1, choice_number + 1):
        choice_paper.append(choice_list[choice_flag - 1])
        choice_flag += choice_interval

    if len(fillin_list) > 0:
        while 1:
            fillin_num = random.randint(1, len(fillin_list))
            fillin_paper = random.sample(fillin_list, fillin_num)
            total = 0
            for li in fillin_paper:
                total += li.diff
            # print('我是总分' + str(total))
            if total == fillin_score:
                break
    else:
        fillin_num = 0
        fillin_paper = []

    fillin_num = len(fillin_paper)
    return render(request, 'student/chapter_test.html',
                  {'choice_paper': choice_paper, 'choice_number': choice_number, 'fillin_paper': fillin_paper,
                   'fillin_number': fillin_num, 'chapter': chapter, 'fillin_score': fillin_score})


def count_choice_grade(questionId):
    question_list = models.choice_ans.objects.filter(questionId=questionId)
    total_finish_num = len(question_list)
    correct_num = 0
    for li in question_list:
        if li.correct == 1:
            correct_num += 1

    if total_finish_num != 0:
        new_grade = float(correct_num) / float(total_finish_num)
    else:
        new_grade = 0

    sigle_grade = models.choice_questions.objects.get(questionId=questionId)
    sigle_grade.grade = new_grade
    sigle_grade.save()
    # 对总的区分度进行修改
    ans_list = models.choice_ans.objects.all()
    total_grade_ans_num = len(ans_list)
    correct_ans = 0
    for li in ans_list:
        if li.correct == 1:
            correct_ans += 1
    total_grade = models.total_grade.objects.get(question_name='choice')
    if total_grade_ans_num != 0:
        total_grade.grade = float(correct_ans) / float(total_grade_ans_num)
    else:
        total_grade.grade = 0
    total_grade.save()


def count_fillin_grade(fillinId):
    fillin_list = models.fillin_ans.objects.filter(fillinId=fillinId)
    total_fillin_num = len(fillin_list)
    correct_num = 0
    for li in fillin_list:
        if li.correct == 1:
            correct_num += 1
        elif li.correct == 2:
            correct_num += 2
        elif li.correct == 3:
            correct_num += 3
    if total_fillin_num != 0:
        new_grade = float(correct_num) / float(total_fillin_num)
    else:
        new_grade = 0

    sigle_grade = models.fillin_questions.objects.get(fillinId=fillinId)
    sigle_grade.grade = new_grade
    sigle_grade.save()

    ans_list = models.fillin_ans.objects.all()
    ans_list_num = len(ans_list)
    correct_ans = 0
    for li in ans_list:
        if li.correct == 1:
            correct_ans += 1
        elif li.correct == 2:
            correct_ans += 2
        elif li.correct == 3:
            correct_ans += 3
    if ans_list_num != 0:
        new_ans_grade = float(correct_ans) / float(ans_list_num)
    else:
        new_ans_grade = 0
    total_grade = models.total_grade.objects.get(question_name='fillin')
    total_grade.grade = new_ans_grade
    total_grade.save()


# 交章节测试的卷
def submit_paper(request):
    choice_nunmber = request.POST['choice_number']
    fillin_number = request.POST['fillin_number']
    stuId = request.session.get('user_id')
    chapter = request.POST['chapter']
    fillin_score = request.POST['fillin_score']
    this_student = request.session.get('user_id')
    teacher = student.objects.get(stu_Id=this_student).teacher

    chapter = int(chapter)
    # print(chapter)

    C_list = models.choice_ans.objects.filter(chapter=chapter, stuId=this_student)
    # print(C_list)
    if len(C_list) > 0:
        message = '您已做过本章题目！'

        # fillin_number = 0
    else:
        # 取出选择题
        total_score = 0
        for i in range(1, int(choice_nunmber) + 1):
            questionId = request.POST['choice_' + str(i) + '_id']
            choice_answer = request.POST['choice_' + str(i)]

            new_choice = models.choice_ans.objects.create()
            new_choice.stuId = stuId
            new_choice.questionId = questionId
            new_choice.answer = choice_answer
            new_choice.chapter = chapter
            new_choice.is_final = 0
            if choice_answer == models.choice_questions.objects.get(questionId=questionId).rightAnswer:
                new_choice.correct = 1
                total_score += models.choice_questions.objects.get(questionId=questionId).diff
            else:
                new_choice.correct = 0
            new_choice.save()

            count_choice_grade(questionId)

        # 取出填空题
        # print(fillin_number)
        for i in range(1, int(fillin_number) + 1):
            fillinId = request.POST['fillin_' + str(i) + '_id']
            question = models.fillin_questions.objects.get(fillinId=fillinId)
            diff = question.diff
            if diff == 1:
                fillin_answer1 = request.POST['fillin_' + str(i) + '_answer1']
            elif diff == 2:
                fillin_answer1 = request.POST['fillin_' + str(i) + '_answer1']
                fillin_answer2 = request.POST['fillin_' + str(i) + '_answer2']
            else:
                fillin_answer1 = request.POST['fillin_' + str(i) + '_answer1']
                fillin_answer2 = request.POST['fillin_' + str(i) + '_answer2']
                fillin_answer3 = request.POST['fillin_' + str(i) + '_answer3']

            new_fillin = models.fillin_ans.objects.create()
            new_fillin.stuId = stuId
            new_fillin.fillinId = fillinId
            if diff == 1:
                new_fillin.ans1 = fillin_answer1
                if (fillin_answer1 != '') and (fillin_answer1 in question.answer1):
                    new_fillin.correct = 1
                    total_score += 1
                else:
                    new_fillin.correct = 0

            elif diff == 2:
                new_fillin.ans1 = fillin_answer1
                new_fillin.ans2 = fillin_answer2
                order = question.is_order
                fillin_ans = [fillin_answer1, fillin_answer2]
                right_ans = [question.answer1, question.answer2]
                new_fillin.correct = 0
                if order == 1:
                    for num in range(0, 2):
                        if fillin_ans[num] != "":
                            if fillin_ans[num] in right_ans[num]:
                                new_fillin.correct += 1
                                total_score += 1
                                print(fillin_ans[num])
                                print(type(fillin_ans[num]))

                elif order == 0:
                    for num in range(0, 2):
                        for li in right_ans:
                            if fillin_ans[num] != '':
                                if fillin_ans[num] in li:
                                    new_fillin.correct += 1
                                    total_score += 1
                                    print(fillin_ans[num])

            elif diff == 3:
                new_fillin.ans1 = fillin_answer1
                new_fillin.ans2 = fillin_answer2
                new_fillin.ans3 = fillin_answer3
                fillin_ans = [fillin_answer1, fillin_answer2, fillin_answer3]
                right_ans = [question.answer1, question.answer2, question.answer3]
                new_fillin.correct = 0

                order = question.is_order
                if order == 1:
                    for num in range(0, 3):
                        if fillin_ans[num] != '' and fillin_ans[num] in right_ans[num]:
                            new_fillin.correct += 1
                            total_score += 1

                elif order == 0:
                    for num in range(0, 3):
                        for li in right_ans:
                            if fillin_ans[num] != '' and fillin_ans[num] in li:
                                new_fillin.correct += 1
                                total_score += 1

            new_fillin.chapter = chapter
            new_fillin.is_final = 0
            new_fillin.save()
            count_fillin_grade(fillinId)

        # 将成绩存入成绩表
        # chapter_list = ['chapter1', 'chapter2', 'chapter3', 'chapter4', 'chapter5', 'chapter6', 'chapter7']
        new_score = models.score.objects.get(stu_Id=stuId)

        if chapter == 1:
            new_score.chapter1 = total_score
        elif chapter == 2:
            new_score.chapter2 = total_score
        elif chapter == 3:
            new_score.chapter3 = total_score
        elif chapter == 4:
            new_score.chapter4 = total_score
        elif chapter == 5:
            new_score.chapter5 = total_score
        elif chapter == 6:
            new_score.chapter6 = total_score
        elif chapter == 7:
            new_score.chapter7 = total_score

        new_score.final = 0
        new_score.save()
        message = '交卷成功'

        # 将章节总分存入成绩表
        new_question_num = models.question_num.objects.get(chapter=chapter, teacher=teacher)
        new_question_num.choice = choice_nunmber
        new_question_num.fillin = fillin_score
        new_question_num.save()

    return render(request, 'student/chapter_test.html', {'message': message, 'fillin_number': 0, 'chapter': chapter})


def final_test(request):
    from login import models

    choice_list = exercise.models.choice_questions.objects.all().order_by('questionSection')
    fillin_list = exercise.models.fillin_questions.objects.all().order_by('fillinSection')
    student_id = request.session.get('user_id')

    teacher = login.models.student.objects.get(stu_Id=student_id).teacher

    question_strategy = exercise.models.question_strategy.objects.get(teacher=teacher, is_final=1)
    choice_number = question_strategy.choice_number
    fillin_score = question_strategy.fillin_number

    if choice_number > len(choice_list):
        choice_number = len(choice_list)

    total_fillin_diff = 0
    for li in fillin_list:
        total_fillin_diff += li.diff

    if fillin_score > total_fillin_diff:
        fillin_score = total_fillin_diff

    # 选择题取样的间隔，可避免知识点重复
    choice_interval = len(choice_list) / choice_number
    choice_flag = random.randint(1, choice_interval)
    choice_paper = []
    for i in range(1, choice_number + 1):
        choice_paper.append(choice_list[choice_flag - 1])
        choice_flag += choice_interval

    # 填空题

    while 1:
        fillin_number = random.randint(1, len(fillin_list))
        fillin_paper = random.sample(fillin_list, fillin_number)
        total = 0
        for li in fillin_paper:
            total += li.diff
        if total == fillin_score:
            break

    return render(request, 'student/final_test.html',
                  {'choice_paper': choice_paper, 'choice_number': choice_number, 'fillin_paper': fillin_paper,
                   'fillin_number': fillin_number, 'fillin_score': fillin_score})


# 交期末测试的卷
def submit_final(request):
    choice_nunmber = request.POST['choice_number']
    fillin_number = request.POST['fillin_number']
    stuId = request.session.get('user_id')
    fillin_score = request.POST['fillin_score']
    this_student = request.session.get('user_id')
    teacher = student.objects.get(stu_Id=this_student).teacher

    C_list = models.choice_ans.objects.filter(is_final=1, stuId=stuId)
    # print(C_list)
    if len(C_list) > 0:
        message = '您已做过期末测试！'
        # fillin_number = 0
    else:
        # 取出选择题
        total_score = 0
        for i in range(1, int(choice_nunmber) + 1):
            questionId = request.POST['choice_' + str(i) + '_id']
            choice_answer = request.POST['choice_' + str(i)]

            new_choice = models.choice_ans.objects.create()
            new_choice.stuId = stuId
            new_choice.questionId = questionId
            new_choice.answer = choice_answer
            # new_choice.chapter = chapter
            new_choice.is_final = 1
            if choice_answer == models.choice_questions.objects.get(questionId=questionId).rightAnswer:
                new_choice.correct = 1
                total_score += models.choice_questions.objects.get(questionId=questionId).diff
            else:
                new_choice.correct = 0
            new_choice.save()

            count_choice_grade(questionId)

        # 取出填空题
        # print(fillin_number)
        for i in range(1, int(fillin_number) + 1):
            fillinId = request.POST['fillin_' + str(i) + '_id']
            question = models.fillin_questions.objects.get(fillinId=fillinId)
            diff = question.diff
            if diff == 1:
                fillin_answer1 = request.POST['fillin_' + str(i) + '_answer1']
            elif diff == 2:
                fillin_answer1 = request.POST['fillin_' + str(i) + '_answer1']
                fillin_answer2 = request.POST['fillin_' + str(i) + '_answer2']
            else:
                fillin_answer1 = request.POST['fillin_' + str(i) + '_answer1']
                fillin_answer2 = request.POST['fillin_' + str(i) + '_answer2']
                fillin_answer3 = request.POST['fillin_' + str(i) + '_answer3']

            new_fillin = models.fillin_ans.objects.create()
            new_fillin.stuId = stuId
            new_fillin.fillinId = fillinId
            if diff == 1:
                new_fillin.ans1 = fillin_answer1
                if fillin_answer1 != '' and fillin_answer1 in question.answer1:
                    new_fillin.correct = 1
                    total_score += 1
                else:
                    new_fillin.correct = 0

            elif diff == 2:
                new_fillin.ans1 = fillin_answer1
                new_fillin.ans2 = fillin_answer2
                order = question.is_order
                fillin_ans = [fillin_answer1, fillin_answer2]
                right_ans = [question.answer1, question.answer2]
                new_fillin.correct = 0
                if order == 1:

                    for num in range(0, 2):
                        if fillin_ans[num] != '' and fillin_ans[num] == right_ans[num]:
                            new_fillin.correct += 1
                            total_score += 1

                elif order == 0:
                    for num in range(0, 2):
                        for li in right_ans:
                            if fillin_ans[num] != '' and fillin_ans[num] == li:
                                new_fillin.correct += 1
                                total_score += 1

            elif diff == 3:
                new_fillin.ans1 = fillin_answer1
                new_fillin.ans2 = fillin_answer2
                new_fillin.ans3 = fillin_answer3
                fillin_ans = [fillin_answer1, fillin_answer2, fillin_answer3]
                right_ans = [question.answer1, question.answer2, question.answer3]
                new_fillin.correct = 0

                order = question.is_order
                if order == 1:
                    for num in range(0, 3):
                        if fillin_ans[num] != '' and fillin_ans[num] in right_ans[num]:
                            new_fillin.correct += 1
                            total_score += 1

                elif order == 0:
                    for num in range(0, 3):
                        for li in right_ans:
                            if fillin_ans[num] != '' and fillin_ans[num] in li:
                                new_fillin.correct += 1
                                total_score += 1

            # new_fillin.chapter = chapter
            new_fillin.is_final = 1
            new_fillin.save()
            count_fillin_grade(fillinId)

        # 将成绩存入成绩表
        # chapter_list = ['chapter1', 'chapter2', 'chapter3', 'chapter4', 'chapter5', 'chapter6', 'chapter7']
        new_score = models.score.objects.get(stu_Id=stuId)

        new_score.final = total_score

        new_score.final = 1
        new_score.save()
        message = '交卷成功'

        # 将期末分存入成绩表
        new_question_num = models.question_num.objects.get(chapter=0, teacher=teacher)
        new_question_num.choice = choice_nunmber
        new_question_num.fillin = fillin_score
        new_question_num.save()

    return render(request, 'student/final_test.html', {'message': message, 'fillin_number': 0})


# 我的测试
def mytest(request):
    stuId = request.session.get('user_id')
    chapter = 1
    choice_list = models.choice_questions.objects.all()
    my_choice = models.choice_ans.objects.filter(chapter=chapter, stuId=stuId)
    choice_score = 0
    for list in my_choice:
        if list.correct == 1:
            choice_score += 1

    fillin_list = models.fillin_questions.objects.all()
    my_fillin = models.fillin_ans.objects.filter(chapter=chapter, stuId=stuId)
    fillin_score = 0
    for list in my_fillin:
        if list.correct == 1:
            fillin_score += 1
        elif list.correct == 2:
            fillin_score += 2
        elif list.correct == 3:
            fillin_score += 3

    return render(request, 'student/mytest.html',
                  {'choice_list': choice_list, 'my_choice': my_choice, 'fillin_list': fillin_list,
                   'my_fillin': my_fillin, 'choice_score': choice_score, 'fillin_score': fillin_score,
                   'total_score': choice_score + fillin_score})


# 我的组卷测试
def my_compose_test(request):
    stuId = request.session.get('user_id')
    test_name = request.GET.get('test_name')
    choice_list = models.choice_questions.objects.all()
    my_choice = models.compose_choice_ans.objects.filter(test_name=test_name, stuId=stuId)

    # 计算我的选择题分数
    choice_score = 0
    for list in my_choice:
        if list.correct == 1:
            choice_score += 1

    fillin_list = models.fillin_questions.objects.all()
    my_fillin = models.compose_fillin_ans.objects.filter(test_name=test_name, stuId=stuId)

    # 计算我的填空题分数
    fillin_score = 0
    for list in my_fillin:
        if list.correct == 1:
            fillin_score += 1
        elif list.correct == 2:
            fillin_score += 2
        elif list.correct == 3:
            fillin_score += 3

    return render(request, 'student/my_compose_test.html', locals())


# 改变查看成绩的章节
def change_chapter_mytest(request):
    chapter = request.GET.get('chapter')
    final = request.GET.get('final')
    print(final)
    if final is None:
        stuId = request.session.get('user_id')

        choice_list = models.choice_questions.objects.all()
        my_choice = models.choice_ans.objects.filter(chapter=chapter, stuId=stuId)
        choice_score = 0
        for list in my_choice:
            if list.correct == 1:
                choice_score += 1

        fillin_list = models.fillin_questions.objects.all()
        my_fillin = models.fillin_ans.objects.filter(chapter=chapter, stuId=stuId)
        fillin_score = 0
        for list in my_fillin:
            if list.correct == 1:
                fillin_score += 1
            elif list.correct == 2:
                fillin_score += 2
            elif list.correct == 3:
                fillin_score += 3

    else:
        stuId = request.session.get('user_id')

        choice_list = models.choice_questions.objects.all()
        my_choice = models.choice_ans.objects.filter(is_final=final, stuId=stuId)
        choice_score = 0
        for list in my_choice:
            if list.correct == 1:
                choice_score += 1

        fillin_list = models.fillin_questions.objects.all()
        my_fillin = models.fillin_ans.objects.filter(is_final=final, stuId=stuId)
        fillin_score = 0
        for list in my_fillin:
            if list.correct == 1:
                fillin_score += 1
            elif list.correct == 2:
                fillin_score += 2
            elif list.correct == 3:
                fillin_score += 3

    return render(request, 'student/mytest.html',
                  {'choice_list': choice_list, 'my_choice': my_choice, 'fillin_list': fillin_list,
                   'my_fillin': my_fillin, 'choice_score': choice_score, 'fillin_score': fillin_score,
                   'total_score': choice_score + fillin_score})


# 老师
def compose_test(request):
    teacher = request.session.get('user_id')
    test_name_list = models.compose_choice.objects.values('test_name').filter(teacher=teacher).distinct()
    # print(test_name_list[0]['test_name'])
    my_test = []
    for li in test_name_list:
        my_test.append(li['test_name'])
    return render(request, 'teacher/compose_test.html', {'my_test': my_test})


def my_compose(request):
    teacher = request.session.get('user_id')
    test_name = request.GET.get('test_name')
    return render(request, 'teacher/my_compose.html', locals())


def compose_choice(request):
    teacher = request.session.get('user_id')
    test_name = request.GET.get('test_name')
    # 判断是否已经有该试卷名
    flag = models.compose_choice.objects.filter(test_name=test_name, teacher=teacher)
    if len(flag) == 0:
        choice_list = models.choice_questions.objects.all()

        # # 选择题分页
        # paginator = Paginator(choice_list, 8)
        # page = request.GET.get('page')
        # try:
        #     choice_list = paginator.page(page)
        # except PageNotAnInteger:
        #     choice_list = paginator.page(1)
        # except EmptyPage:
        #     choice_list = paginator.page(paginator.num_pages)

        return render(request, 'teacher/compose_choice.html', locals())
    else:
        message = '试卷名不得重复！'

        test_name_list = models.compose_choice.objects.values('test_name').filter(teacher=teacher).distinct()
        # print(test_name_list[0]['test_name'])
        my_test = []
        for li in test_name_list:
            my_test.append(li['test_name'])
        return render(request, 'teacher/compose_test.html', {'my_test': my_test, 'message': message})


def compose_situation(request):
    test_name = request.GET.get('test_name')
    teacher = request.session.get('user_id')
    score_list = models.compose_score.objects.filter(test_name=test_name, teacher=teacher)
    situation_list = []
    chart_list = []

    # 计算满分
    full_choice_score = len(models.compose_choice.objects.filter(test_name=test_name, teacher=teacher))
    full_fillin_score = 0
    fillin_list = models.compose_fillin.objects.filter(test_name=test_name, teacher=teacher)
    for li in fillin_list:
        full_fillin_score += models.fillin_questions.objects.get(fillinId=li.fillinId).diff
    full_score = full_fillin_score + full_choice_score

    # 画图用
    for i in range(0, full_score + 1):
        chart_list.append(0)

    for li in score_list:
        this_student = student.objects.get(stu_Id=li.stu_Id)
        situation_list.append([li.stu_Id, this_student.name, this_student.stu_major, this_student.stu_class, test_name,
                               li.choice, li.fillin, li.total_score, full_score])

        chart_list[li.total_score] += 1

    return render(request, 'teacher/compose_situation.html',
                  {'situation_list': situation_list, 'chart_list': chart_list, 'test_name': test_name})


def submit_choice(request):
    test_name = request.GET.get('test_name')
    teacher = request.session.get('user_id')
    questionId = json.loads(request.GET.get('list'))
    questionId = questionId[0].encode('utf-8')

    new_choice = models.compose_choice.objects.create(test_name=test_name, teacher=teacher, questionId=questionId)
    new_choice.save()

    return render(request, 'teacher/compose_fillin.html', {'test_name': test_name})


def compose_fillin(request):
    test_name = request.GET.get('test_name')
    fillin_list = models.fillin_questions.objects.all()
    return render(request, 'teacher/compose_fillin.html', locals())


def submit_fillin(request):
    test_name = request.GET.get('test_name')
    teacher = request.session.get('user_id')
    fillinId = json.loads(request.GET.get('list'))
    fillinId = fillinId[0].encode('utf-8')

    new_fillin = models.compose_fillin.objects.create(test_name=test_name, teacher=teacher, fillinId=fillinId)
    new_fillin.save()

    return render(request, 'teacher/compose_fillin.html', {'test_name': test_name})


def test_situation(request):
    # 总的区分度
    choice_grade = models.total_grade.objects.get(question_name='choice')
    fillin_grade = models.total_grade.objects.get(question_name='fillin')
    teacher = request.session.get('user_id')
    total_score = models.question_num.objects.filter(teacher=teacher)
    whole_student = student.objects.filter(teacher=teacher)
    # choice_ans = models.choice_ans.objects.all()

    # 参加了章节考试以及期末考的总人数
    chapter_num = [0, 0, 0, 0, 0, 0, 0]
    final_num = 0
    # 每章考试的总得分
    chapter_score = [0, 0, 0, 0, 0, 0, 0]
    # 期末考的总得分
    final_score = 0
    # 章节考试的平均分
    avg_chapter = [0, 0, 0, 0, 0, 0, 0]
    # 期末考的平均分
    avg_final = 0
    # 得分率
    score_rate = [0, 0, 0, 0, 0, 0, 0, 0]

    # print(chapter_num[0][1])
    for li in whole_student:
        for i in range(1, 8):
            flag = models.choice_ans.objects.filter(stuId=li.stu_Id, chapter=i)
            # 这学生考了这个章节的试
            if len(flag) != 0:
                chapter_num[i - 1] += 1
                # 算该章节的总分
                if i == 1:
                    chapter_score[i - 1] += models.score.objects.get(stu_Id=li.stu_Id).chapter1
                elif i == 2:
                    chapter_score[i - 1] += models.score.objects.get(stu_Id=li.stu_Id).chapter2
                elif i == 3:
                    chapter_score[i - 1] += models.score.objects.get(stu_Id=li.stu_Id).chapter3
                elif i == 4:
                    chapter_score[i - 1] += models.score.objects.get(stu_Id=li.stu_Id).chapter4
                elif i == 5:
                    chapter_score[i - 1] += models.score.objects.get(stu_Id=li.stu_Id).chapter5
                elif i == 6:
                    chapter_score[i - 1] += models.score.objects.get(stu_Id=li.stu_Id).chapter6
                elif i == 7:
                    chapter_score[i - 1] += models.score.objects.get(stu_Id=li.stu_Id).chapter7

        flag1 = models.choice_ans.objects.filter(stuId=li.stu_Id, is_final=1)
        if len(flag1) != 0:
            final_num += 1
            final_score += models.score.objects.get(stu_Id=li.stu_Id).final

    # 计算平均分
    for i in range(0, 7):
        if chapter_num[i] != 0:
            avg_chapter[i] = chapter_score[i] / chapter_num[i]

    if final_num != 0:
        avg_final = final_score / final_num

    # 计算得分率
    # print(total_score[7].choice)
    for i in range(0, 7):
        if total_score[i].choice + total_score[i].fillin != 0:
            score_rate[i] = float(avg_chapter[i]) / float(total_score[i].choice + total_score[i].fillin)
    #         print(score_rate[i])
    #
    if total_score[7].choice + total_score[7].fillin != 0:
        score_rate[7] = float(avg_final) / float(total_score[7].choice + total_score[7].fillin)
    #     pass

    # 组卷考试的情况
    compose_list = []
    whole_test = []
    whole_test1 = models.compose_choice.objects.values('test_name').filter(teacher=teacher).distinct()
    for i in whole_test1:
        whole_test.append(str(i['test_name']))
    # 遍历一下成绩表
    for li in whole_test:
        # print(type(li))
        index = models.compose_score.objects.filter(test_name=li)
        total_num = len(index)
        total_score1 = 0
        avg_score = 0
        for lis in index:
            total_score1 += lis.choice
            total_score1 += lis.fillin
        if total_num != 0:
            avg_score = float(total_score1) / float(total_num)
        # 计算满分
        choice_full_score = len(models.compose_choice.objects.filter(test_name=li))
        fillin_full_score = 0
        this_fillin = models.compose_fillin.objects.filter(test_name=li)
        for lis1 in this_fillin:
            choice_full_score += models.fillin_questions.objects.get(fillinId=lis1.fillinId).diff

        # 计算最高分
        max_score = models.compose_score.objects.filter(test_name=li).aggregate(Max('total_score'))['total_score__max']

        compose_list.append([li, total_num, avg_score, choice_full_score + fillin_full_score, max_score])
    return render(request, 'teacher/test_situation.html', locals())


# 测试情况详细
def chapter_situation(request):
    chapter = int(request.GET.get('chapter'))
    teacher = request.session.get('user_id')
    list = []
    stu_list = []
    chart_list = []
    # 章节测试信息
    if chapter != 0:

        student_list = models.choice_ans.objects.values('stuId').distinct().filter(chapter=chapter)
        full_choice_score = models.question_num.objects.get(chapter=chapter,
                                                            teacher=teacher).choice
        full_fillin_score = models.question_num.objects.get(chapter=chapter,
                                                            teacher=teacher).fillin
        full_score = full_fillin_score + full_choice_score

        for i in range(0, full_score + 1):
            chart_list.append(0)

        for li in student_list:
            stu_Id = li['stuId']
            # 判断是否当前老师用户的学生
            if len(student.objects.filter(stu_Id=stu_Id, teacher=teacher)) != 0:
                # 取出student信息
                this_student = student.objects.get(stu_Id=stu_Id)
                name = this_student.name
                stu_major = this_student.stu_major
                stuClass = this_student.stu_class
                # 取出该学生本章答过的选择题和填空题来计算填空题选择题得分
                choice_ans_list = models.choice_ans.objects.filter(stuId=stu_Id, chapter=chapter)
                fillin_ans_list = models.fillin_ans.objects.filter(stuId=stu_Id, chapter=chapter)
                choice_score = 0
                fillin_score = 0
                # 最高分
                max_score = 0

                # 最高分
                if chapter == 1:
                    max_score = models.score.objects.all().aggregate(Max('chapter1'))['chapter1__max']
                elif chapter == 2:
                    max_score = models.score.objects.all().aggregate(Max('chapter2'))['chapter2__max']
                elif chapter == 3:
                    max_score = models.score.objects.all().aggregate(Max('chapter3'))['chapter3__max']
                elif chapter == 4:
                    max_score = models.score.objects.all().aggregate(Max('chapter4'))['chapter4__max']
                elif chapter == 5:
                    max_score = models.score.objects.all().aggregate(Max('chapter5'))['chapter5__max']
                elif chapter == 6:
                    max_score = models.score.objects.all().aggregate(Max('chapter6'))['chapter6__max']
                elif chapter == 7:
                    max_score = models.score.objects.all().aggregate(Max('chapter7'))['chapter7__max']

                for lis in choice_ans_list:
                    if lis.correct == 1:
                        choice_score += 1

                for lis in fillin_ans_list:
                    if lis.correct == 1:
                        fillin_score += 1
                    elif lis.correct == 2:
                        fillin_score += 2
                    elif fillin_score == 3:
                        fillin_score += 3
                # 做图表的时候用
                chart_list[fillin_score + choice_score] += 1

                stu_list.append(stu_Id)
                list.append([stu_Id, name, stu_major, stuClass, choice_score, fillin_score, choice_score + fillin_score,
                             full_score, max_score])

    # 期末测试信息
    else:
        full_choice_score = models.question_num.objects.get(chapter=chapter, teacher=teacher).choice
        full_fillin_score = models.question_num.objects.get(chapter=chapter, teacher=teacher).fillin
        full_score = full_choice_score + full_fillin_score
        for i in range(1, full_score + 1):
            chart_list.append(0)

        student_list = models.choice_ans.objects.values('stuId').distinct().filter(chapter=chapter)
        # print(student_list)
        for li in student_list:
            stu_Id = li['stuId']
            # 判断是否当前老师用户的学生
            if len(student.objects.filter(stu_Id=stu_Id, teacher=teacher)) != 0:
                # 取出student信息
                this_student = student.objects.get(stu_Id=stu_Id)
                name = this_student.name
                stu_major = this_student.stu_major
                stuClass = this_student.stu_class
                # 取出该学生本章答过的选择题和填空题来计算填空题选择题得分
                choice_ans_list = models.choice_ans.objects.filter(is_final=1)
                fillin_ans_list = models.fillin_ans.objects.filter(is_final=1)
                choice_score = 0
                fillin_score = 0
                # 最高分
                max_score = 0

                # 最高分
                max_score = models.score.objects.all().aggregate(Max('final'))['final__max']

                for lis in choice_ans_list:
                    if lis.correct == 1:
                        choice_score += 1

                for lis in fillin_ans_list:
                    if lis.correct == 1:
                        fillin_score += 1
                    elif lis.correct == 2:
                        fillin_score += 2
                    elif fillin_score == 3:
                        fillin_score += 3

                # 做图表的时候用
                flag = fillin_score + choice_score - 1
                chart_list[flag] += 1

                stu_list.append(stu_Id)
                list.append([stu_Id, name, stu_major, stuClass, choice_score, fillin_score, choice_score + fillin_score,
                             full_score, max_score])

    return render(request, 'teacher/chapter_situation.html',
                  {'list': list, 'chapter': chapter, 'stu_list': stu_list, 'chart_list': chart_list})


# @csrf_exempt
def del_student(request):
    list1 = json.loads(request.GET.get('list'))

    list1 = list1[0].encode('utf-8')

    student.objects.get(stu_Id=list1).delete()
    # 删除成绩表
    models.score.objects.get(stu_Id=list1).delete()

    return redirect('/exercise/all_student/')


def del_choice(request):
    questionId = json.loads(request.GET.get('list'))
    # list1 = request.POST['list']
    # list1 = request.GET.get('list')
    questionId = questionId[0].encode('utf-8')
    # print(list1)
    models.choice_questions.objects.get(questionId=questionId).delete()

    return redirect('/exercise/question_bank/')


def del_fillin(request):
    fillinId = json.loads(request.GET.get('list'))
    # list1 = request.POST['list']
    # list1 = request.GET.get('list')
    fillinId = fillinId[0].encode('utf-8')
    # print(list1)
    models.fillin_questions.objects.get(fillinId=fillinId).delete()

    return redirect('/exercise/question_bank/')


def all_student(request):
    # print(student.objects.get(stu_Id='1500502257').__getattribute__(student))
    teacher = request.session.get('user_id')
    student_list = student.objects.order_by('stu_Id').filter(teacher=teacher)
    major_list = student.objects.values('stu_major').filter(teacher=teacher).distinct().order_by('stu_major')
    class_list = student.objects.values('stu_class').filter(teacher=teacher).distinct().order_by('stu_class')

    # 分页
    paginator = Paginator(student_list, 8)
    page = request.GET.get('page')
    try:
        stu_list = paginator.page(page)
    except PageNotAnInteger:
        stu_list = paginator.page(1)
    except EmptyPage:
        stu_list = paginator.page(paginator.num_pages)

    return render(request, 'teacher/all_student.html', locals())


def filter_student(request):
    my_major = request.GET.get('my_major')
    my_class = request.GET.get('stu_class')
    major_list = student.objects.values('stu_major').distinct().order_by('stu_major')
    class_list = student.objects.values('stu_class').distinct().order_by('stu_class')
    student_list = student.objects.filter(stu_major=my_major, stu_class=my_class)
    return render(request, 'teacher/all_student.html', locals())


def view_student(request):
    stu_Id = request.GET.get('stu_Id')
    my_student = student.objects.get(stu_Id=stu_Id)
    return render(request, 'teacher/view_student.html', locals())


def view_choice(request):
    questionId = request.GET.get('questionId')
    my_choice = models.choice_questions.objects.get(questionId=questionId)
    # ans = models.choice_ans.objects.filter(questionId=questionId)
    # compose_ans = models.compose_choice_ans.objects.filter(questionId=questionId)
    numberA = len(models.choice_ans.objects.filter(questionId=questionId, answer='A')) + len(
        models.compose_choice_ans.objects.filter(questionId=questionId, answer='A'))
    numberB = len(models.choice_ans.objects.filter(questionId=questionId, answer='B')) + len(
        models.compose_choice_ans.objects.filter(questionId=questionId, answer='B'))
    numberC = len(models.choice_ans.objects.filter(questionId=questionId, answer='C')) + len(
        models.compose_choice_ans.objects.filter(questionId=questionId, answer='C'))
    numberD = len(models.choice_ans.objects.filter(questionId=questionId, answer='D')) + len(
        models.compose_choice_ans.objects.filter(questionId=questionId, answer='D'))

    rightNum = len(models.choice_ans.objects.filter(questionId=questionId, answer=my_choice.rightAnswer)) + len(
        models.compose_choice_ans.objects.filter(questionId=questionId, answer=my_choice.rightAnswer))
    wrongNum = (len(models.choice_ans.objects.filter(questionId=questionId)) + len(
        models.compose_choice_ans.objects.filter(questionId=questionId))) - rightNum
    print(rightNum)
    print(wrongNum)
    return render(request, 'teacher/view_choice.html', locals())


def view_fillin(request):
    fillinId = request.GET.get('fillinId')
    my_fillin = models.fillin_questions.objects.get(fillinId=fillinId)
    chart = [0, 0, 0, 0]
    fillin_ans = models.fillin_ans.objects.filter(fillinId=fillinId)
    for li in fillin_ans:
        chart[li.correct] += 1
    return render(request, 'teacher/view_fillin.html', locals())


def update_student(request):
    # 原本的stu_Id
    stu_Id0 = request.POST['stu_Id0']

    stu_Id = request.POST['stu_Id']
    name = request.POST['name']
    # password = request.POST['password']
    stu_major = request.POST['stu_major']
    stu_class = request.POST['stu_class']
    sex = request.POST['sex']

    new_student = student.objects.get(stu_Id=stu_Id0)
    new_student.stu_Id = stu_Id
    new_student.name = name
    # new_student.password = password
    new_student.stu_major = stu_major
    new_student.stu_class = stu_class
    new_student.sex = sex
    new_student.save()

    return redirect('/exercise/all_student/')


def update_choice(request):
    # 原本的stu_Id
    questionId = request.POST['questionId']

    questionContent = request.POST['questionContent']
    questionSection = request.POST['questionSection']
    answer1 = request.POST['answer1']
    answer2 = request.POST['answer2']
    answer3 = request.POST['answer3']
    answer4 = request.POST['answer4']
    rightAnswer = request.POST['rightAnswer']
    diff = request.POST['diff']

    new_choice = models.choice_questions.objects.get(questionId=questionId)
    new_choice.questionContent = questionContent
    new_choice.questionSection = questionSection
    new_choice.answer1 = answer1
    new_choice.answer2 = answer2
    new_choice.answer3 = answer3
    new_choice.answer4 = answer4
    new_choice.rightAnswer = rightAnswer
    new_choice.diff = diff
    new_choice.save()
    return redirect('/exercise/question_bank/')


def update_fillin(request):
    # 原本的stu_Id
    fillinId = request.POST['fillinId']

    fillinContent = request.POST['questionContent']

    answer1 = request.POST['answer1']
    answer2 = request.POST['answer2']
    answer3 = request.POST['answer3']

    is_order = request.POST['is_order']
    fillinSection = request.POST['fillinSection']

    diff = request.POST['diff']

    new_fillin = models.fillin_questions.objects.get(fillinId=fillinId)
    new_fillin.fillinContent = fillinContent
    new_fillin.answer1 = answer1
    new_fillin.answer2 = answer2
    new_fillin.answer3 = answer3
    new_fillin.is_order = is_order
    new_fillin.fillinSection = fillinSection
    new_fillin.diff = diff
    new_fillin.save()
    return redirect('/exercise/question_bank/')


def set_rules(request):
    teacher = request.session.get('user_id')
    rule_list = models.question_strategy.objects.filter(teacher=teacher)

    if request.method == "POST":
        is_final = request.POST['is_final']
        choice_number = request.POST['choice_num']
        fillin_number = request.POST['fillin_num']

        question_strategy = models.question_strategy.objects.get(teacher=teacher, is_final=is_final)
        question_strategy.choice_number = choice_number
        question_strategy.fillin_number = fillin_number
        question_strategy.save()
        message = '修改成功'
        return render(request, 'teacher/set_rules.html', {'rule_list': rule_list, 'message': message})
    return render(request, 'teacher/set_rules.html', {'rule_list': rule_list})


def choice_upload(request):
    max_choice = models.choice_questions.objects.all().aggregate(Max('questionId'))['questionId__max']
    # print(type(max_choice['questionId__max']))
    return render(request, 'teacher/choice_upload.html', locals())


def fillin_upload(request):
    max_fillin = models.fillin_questions.objects.all().aggregate(Max('fillinId'))['fillinId__max']
    return render(request, 'teacher/fillin_upload.html', locals())


def student_upload(request):
    pass
    return render(request, 'teacher/student_upload.html')


def question_bank(request):
    choice_list = models.choice_questions.objects.all()
    # print(choice_list.get)
    fillin_list = models.fillin_questions.objects.all()

    # 选择题分页
    paginator = Paginator(choice_list, 8)
    page = request.GET.get('page')
    try:
        choice = paginator.page(page)
    except PageNotAnInteger:
        choice = paginator.page(1)
    except EmptyPage:
        choice = paginator.page(paginator.num_pages)

    # 填空题分页
    paginator1 = Paginator(fillin_list, 8)
    page1 = request.GET.get('page1')
    try:
        fillin = paginator1.page(page1)
    except PageNotAnInteger:
        fillin = paginator1.page(1)
    except EmptyPage:
        fillin = paginator1.page(paginator1.num_pages)
    # request.session['fillin_list'] = fillin_list
    flag = request.GET.get('flag')
    # print(flag)
    return render(request, 'teacher/question_bank.html', locals())


def insert_choice(request):
    questionId = request.POST['questionId']
    questionSection = request.POST['questionSection']
    questionContent = request.POST['questionContent']
    answer1 = request.POST['answer1']
    answer2 = request.POST['answer2']
    answer3 = request.POST['answer3']
    answer4 = request.POST['answer4']
    rightAnswer = request.POST['rightAnswer']

    new_choice = models.choice_questions.objects.create(questionId=questionId, questionSection=questionSection,
                                                        questionContent=questionContent, answer1=answer1,
                                                        answer2=answer2, answer3=answer3, answer4=answer4,
                                                        rightAnswer=rightAnswer)

    new_choice.save()
    max_choice = models.choice_questions.objects.all().aggregate(Max('questionId'))['questionId__max']
    return render(request, 'teacher/choice_upload.html', {'message': '新增成功', 'max_choice': max_choice})


def insert_fillin(request):
    fillinId = request.POST['fillinId']
    fillinSection = request.POST['fillinSection']
    fillinContent = request.POST['fillinContent']
    answer1 = request.POST['answer1']
    answer2 = request.POST['answer2']
    answer3 = request.POST['answer3']
    is_order = request.POST['is_order']
    diff = request.POST['diff']

    new_fillin = models.fillin_questions.objects.create(fillinId=fillinId, fillinSection=fillinSection,
                                                        fillinContent=fillinContent, answer1=answer1, answer2=answer2,
                                                        answer3=answer3, is_order=is_order, diff=diff)

    new_fillin.save()
    max_fillin = models.fillin_questions.objects.all().aggregate(Max('fillinId'))['fillinId__max']
    return render(request, 'teacher/fillin_upload.html', {'message': '新增成功', 'max_fillin': max_fillin})


def insert_student(request):
    stu_Id = request.POST['stu_Id']

    if len(student.objects.filter(stu_Id=stu_Id)) != 0:
        message1 = '数据库中已存在该学生！'
    else:
        teacher = request.session.get('user_id')
        name = request.POST['name']
        stu_major = request.POST['stu_major']
        stu_class = request.POST['stu_class']
        email = request.POST['email']
        sex = request.POST['sex']

        new_student = student.objects.create(stu_Id=stu_Id, teacher=teacher, name=name, stu_major=stu_major,
                                             stu_class=stu_class, email=email, sex=sex)

        new_student.save()

        # 要插入学生专属的成绩表
        new_score = models.score.objects.create(stu_Id=stu_Id)
        new_score.save()

        message1 = '插入成功！'

    return render(request, 'teacher/student_upload.html', {'message1': message1})


def uploadGrade(request):
    '''
    单选题导入
    :param request:
    :return:
    '''
    # print("I love u ")
    if request.method == 'POST':
        f = request.FILES.get('file')
        excel_type = f.name.split('.')[1]
        if excel_type in ['xlsx', 'xls']:
            # 开始解析上传的excel表格
            wb = xlrd.open_workbook(filename=None, file_contents=f.read())
            table = wb.sheets()[0]
            rows = table.nrows  # 总行数

            try:
                with transaction.atomic():  # 控制数据库事务交易
                    for i in range(1, rows):
                        rowValues = table.row_values(i)
                        # major = models.TMajor.objects.filter(majorid=rowVlaues[1]).first()
                        models.choice_questions.objects.create(questionId=rowValues[0],
                                                               grade=rowValues[1],
                                                               questionContent=rowValues[2],
                                                               questionSection=rowValues[3],
                                                               answer1=rowValues[4],
                                                               answer2=rowValues[5],
                                                               answer3=rowValues[6],
                                                               answer4=rowValues[7],
                                                               rightAnswer=rowValues[8],
                                                               diff=rowValues[9],
                                                               )
            except:
                logger.error('解析excel文件或者题库已存在该题')
                return render(request, 'teacher/choice_upload.html', {'message': '解析excel文件或者题库已存在该题'})

            return render(request, 'teacher/choice_upload.html', {'message': '导入成功'})
        else:
            logger.error('上传文件类型错误！')
            return render(request, 'teacher/choice_upload.html', {'message': '导入失败'})


def uploadFillin(request):
    '''
    填空信息导入
    :param request:
    :return:
    '''
    if request.method == 'POST':
        f = request.FILES.get('file')
        excel_type = f.name.split('.')[1]
        if excel_type in ['xlsx', 'xls']:
            # 开始解析上传的excel表格
            wb = xlrd.open_workbook(filename=None, file_contents=f.read())
            table = wb.sheets()[0]
            rows = table.nrows  # 总行数
            try:
                with transaction.atomic():  # 控制数据库事务交易
                    for i in range(1, rows):
                        rowValues = table.row_values(i)
                        # major = models.TMajor.objects.filter(majorid=rowVlaues[1]).first()
                        models.fillin_questions.objects.create(fillinId=rowValues[0],
                                                               grade=rowValues[1],
                                                               fillinContent=rowValues[2],
                                                               answer1=rowValues[3],
                                                               answer2=rowValues[4],
                                                               answer3=rowValues[5],
                                                               is_order=rowValues[6],
                                                               fillinSection=rowValues[7],
                                                               diff=rowValues[8],
                                                               )
            except:
                # logger.error('解析excel文件或者题库已存在该题')
                return render(request, 'teacher/fillin_upload.html', {'message': '解析excel文件或者题库已存在该题'})

            return render(request, 'teacher/fillin_upload.html', {'message': '导入成功'})
        else:
            logger.error('上传文件类型错误！')
            return render(request, 'teacher/fillin_upload.html', {'message': '导入失败'})


def uploadStudent(request):
    '''
    学生信息一键导入
    :param request:
    :return:
    '''
    if request.method == 'POST':
        teacher = request.session.get('user_id')
        f = request.FILES.get('file')
        excel_type = f.name.split('.')[1]
        if excel_type in ['xlsx', 'xls']:
            # 开始解析上传的excel表格
            wb = xlrd.open_workbook(filename=None, file_contents=f.read())
            table = wb.sheets()[0]
            rows = table.nrows  # 总行数

            try:
                with transaction.atomic():  # 控制数据库事务交易
                    for i in range(1, rows):
                        rowValues = table.row_values(i)
                        print(rowValues[0])
                        student.objects.create(stu_Id=str(int(rowValues[0])), name=rowValues[1], stu_major=rowValues[2],
                                               stu_class=str(int(rowValues[3])), email=rowValues[4], sex=rowValues[5],
                                               teacher=teacher)
                        # 插入成绩表
                        models.score.objects.create(stu_Id=str(int(rowValues[0])))
            except:
                logger.error('解析excel文件或者数据库已存在该学生')
                return render(request, 'teacher/student_upload.html', {'message': '解析excel文件或者数据库已存在该学生'})

            return render(request, 'teacher/student_upload.html', {'message': '导入成功'})
        else:
            logger.error('上传文件类型错误！')
            return render(request, 'teacher/student_upload.html', {'message': '导入失败'})
