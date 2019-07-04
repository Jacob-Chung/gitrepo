# coding=UTF-8
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.
import exercise
from exercise.models import Pictures
from login import models
from login.forms import UserForm, RegisterForm


def test_vi(request):
    # print (request.GET.get('chapter'))
    return render(request, 'bbs/index.html')


def bbs_index(request):
    post = models.post.objects.all().order_by('-c_time')

    # 分页
    paginator = Paginator(post, 10)
    page = request.GET.get('page')
    try:
        post = paginator.page(page)
    except PageNotAnInteger:
        post = paginator.page(1)
    except EmptyPage:
        post = paginator.page(paginator.num_pages)

    return render(request, 'bbs/bbs_index.html', locals())


def my_post(request):
    post = models.post.objects.filter(user_name=request.session.get('user_id')).order_by('-c_time')

    return render(request, 'bbs/my_post.html', locals())


def send_post(request):
    if request.method == 'POST':
        user_name = request.session.get('user_id')
        title = request.POST['title']
        content = request.POST['content']
        if not request.session.get('is_teacher'):
            pic = models.student.objects.get(stu_Id=user_name).pic
            is_teacher = 0
        else:
            pic = 'teacher.jpg'
            is_teacher = 1
        new_post = models.post.objects.create(user_name=user_name, title=title, content=content,
                                              is_teacher=is_teacher, pic=pic)
        new_post.save()
        message = '发表成功'

    return render(request, 'bbs/send_post.html', locals())


def del_post(request):
    post_id = request.GET.get('post_id')
    models.post.objects.get(id=int(post_id)).delete()
    models.comment.objects.filter(post_id=int(post_id)).delete()

    return redirect('/login/my_post/')


def add_comment(request):
    user_name = request.session.get('user_id')
    post_id = request.GET.get('post_id')
    content = request.POST['content']
    # print(type(request.session.get('is_teacher')))
    if not request.session.get('is_teacher'):
        # print '进来了'
        pic = models.student.objects.get(stu_Id=user_name).pic
        is_teacher = 0
    else:
        pic = 'teacher.jpg'
        is_teacher = 1
    new_comment = models.comment.objects.create(user_name=user_name, post_id=post_id, content=content, pic=pic,
                                                is_teacher=is_teacher)
    new_comment.save()
    # message = '评论成功'
    return redirect('/login/post_detail/?post_id='+post_id)


def post_detail(request):
    post_id = request.GET.get('post_id')
    # print(post_id)
    post = models.post.objects.get(id=post_id)
    comment = models.comment.objects.filter(post_id=post_id)
    other_post = models.post.objects.filter(user_name=post.user_name)
    is_teacher = request.session.get('is_teacher')
    return render(request, 'bbs/post_detail.html', locals())


def against_post(request):
    post_id = request.GET.get('post_id')
    # print(post_id)
    post = models.post.objects.get(id=int(post_id))
    post.against += 1
    post.save()

    flag = request.GET.get('flag')
    if flag == 'index':
        return redirect('/login/bbs_index/')
    else:
        return redirect('/login/post_detail/?post_id=' + post_id)


def support_post(request):
    post_id = request.GET.get('post_id')
    post = models.post.objects.get(id=int(post_id))
    post.support += 1
    post.save()

    flag = request.GET.get('flag')
    if flag == 'index':
        return redirect('/login/bbs_index/')
    else:
        return redirect('/login/post_detail/?post_id=' + post_id)


def against_comment(request):
    comment_id = request.GET.get('comment_id')
    comment = models.comment.objects.get(id=int(comment_id))
    post_id = comment.post_id
    comment.against += 1
    comment.save()
    return redirect('/login/post_detail/?post_id=' + str(post_id))


def support_comment(request):
    comment_id = request.GET.get('comment_id')
    comment = models.comment.objects.get(id=int(comment_id))
    post_id = comment.post_id
    comment.support += 1
    comment.save()
    return redirect('/login/post_detail/?post_id=' + str(post_id))


def teacher_center(request):
    teacher = models.teacher.objects.get(teacher_id=request.session.get('user_id'))
    return render(request, 'teacher/teacher_center.html', locals())


def student_center(request):
    # print (request.GET.get('chapter'))
    # pic_obj = Pictures.objects.get(id=1)
    # return render(request, 'img_tem/showing.html', {'pic_obj': pic_obj})

    student = models.student.objects.get(stu_Id=request.session['user_id'])
    teacher = models.teacher.objects.get(teacher_id=student.teacher)
    return render(request, 'student/student_center.html', locals())


# 上传头像
def uploadImg(request):
    # 从请求当中　获取文件对象
    if request.session.get('is_teacher', None):
        stu_Id = request.POST['stu_id']
    else:
        stu_Id = request.session['user_id']

    f1 = request.FILES.get('picture')
    # 　利用模型类　将图片要存放的路径存到数据库中
    student = models.student.objects.get(stu_Id=stu_Id)
    student.pic = 'stu_Pic/' + f1.name
    student.save()

    # 改一下帖子表的头像
    post = models.post.objects.filter(user_name=stu_Id)
    for foo in post:
        foo.pic = 'stu_Pic/' + f1.name
        foo.save()

    # 改评论表的头像
    comment = models.comment.objects.filter(user_name=stu_Id)
    for foo in comment:
        foo.pic = 'stu_Pic/' + f1.name
        foo.save()

    fname = settings.MEDIA_ROOT + "/stu_Pic/" + f1.name
    with open(fname, 'wb') as pic:
        for c in f1.chunks():
            pic.write(c)

    if request.session.get('is_teacher', None):
        return redirect('/exercise/view_student/?stu_Id=' + stu_Id)
    else:
        return redirect('/login/student_center/')


def alter_password(request):
    student = models.student.objects.get(stu_Id=request.session['user_id'])
    # password =
    if request.method == 'POST':
        student = models.student.objects.get(stu_Id=request.session['user_id'])
        # 原密码
        pwd0 = request.POST['pwd0']

        if check_password(pwd0, student.password):
            password = request.POST['pwd']
            # 使用pbkdf2_sha256方式来存储和管理用的密码
            student.password = make_password(password, None, 'pbkdf2_sha256')
            student.save()
            message = '修改成功！'
            return render(request, 'student/alter_password.html', locals())
        else:
            message = '原密码错误！'
    return render(request, 'student/alter_password.html', locals())


def teacher_alter_password(request):
    teacher = models.teacher.objects.get(teacher_id=request.session['user_id'])
    # 原密码
    pwd0 = request.POST['pwd0']

    if check_password(pwd0, teacher.password):
        password = request.POST['pwd']
        # 使用pbkdf2_sha256方式来存储和管理用的密码
        teacher.password = make_password(password, None, 'pbkdf2_sha256')
        teacher.save()
        message = '修改成功！'
        return render(request, 'teacher/teacher_center.html', locals())
    else:
        message = '原密码错误！'
    return render(request, 'teacher/teacher_center.html', locals())


# 老师用户修改个人资料
def alter_teacher(request):
    teacher = models.teacher.objects.get(teacher_id=request.session['user_id'])
    # 原密码
    name = request.POST['name']
    email = request.POST['email']
    sex = request.POST['sex']
    teacher.name = name
    teacher.email = email
    teacher.sex = sex
    teacher.save()
    message1 = '修改成功！'
    # teacher = models.teacher.objects.get(teacher_id=request.session['user_id'])
    return render(request, 'teacher/teacher_center.html', {'message1': message1, 'teacher': teacher})


def homepage(request):
    return render(request, 'login/login.html')


def index(request):
    pass
    return render(request, 'login/index.html')


def teacherindex(request):
    pass
    return render(request, 'teacher/teacherindex.html')


def studentindex(request):
    pass
    return render(request, 'student/studentindex.html')


def login(request):
    # 检测当前是否有用户已登录
    if request.session.get('is_login', None):
        if request.session.get('is_teacher', None):
            return redirect('/exercise/test_situation/')
        else:
            return redirect('/login/studentindex')

    if request.method == "POST":
        user_Id = request.POST['user_Id']
        password = request.POST['password']

        message = "请检查填写的内容！"

        # 老师登录
        if models.teacher.objects.filter(teacher_id=user_Id):
            teacher = models.teacher.objects.get(teacher_id=user_Id)
            if check_password(password, teacher.password):
                request.session['is_login'] = True
                request.session['user_id'] = teacher.teacher_id
                request.session['user_name'] = teacher.name
                request.session['is_teacher'] = True
                return redirect('/exercise/test_situation/')
            else:
                message = "密码错误！"
        # 学生登录
        elif models.student.objects.filter(stu_Id=user_Id):
            student = models.student.objects.get(stu_Id=user_Id)
            if check_password(password, student.password):
                request.session['is_login'] = True
                request.session['user_id'] = student.stu_Id
                request.session['user_name'] = student.name
                request.session['is_student'] = True
                request.session['is_teacher'] = False
                return redirect('/login/studentindex/')
            else:
                message = '密码错误！'

        else:
            message = "用户不存在！"

        return render(request, 'login/login.html', locals())

    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/login/login/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            teacher_id = register_form.cleaned_data['teacher_id']
            name = register_form.cleaned_data['name']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.teacher.objects.filter(teacher_id=teacher_id)
                if same_name_user:  # 用户名唯一
                    message = '该登录名已经存在，请重新选择！'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.teacher.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())

                # 当一切都OK的情况下，创建新用户
                new_user = models.teacher.objects.create()
                new_user.teacher_id = teacher_id
                new_user.name = name
                new_user.password = make_password(password1, None, 'pbkdf2_sha256')
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                # 初始化出题数量表
                for i in range(0, 8):
                    new_num = exercise.models.question_num.objects.create(chapter=i, teacher=teacher_id)
                    new_num.save()
                # 初始化出题策略表
                for i in range(0, 2):
                    new_strategy = exercise.models.question_strategy.objects.create(is_final=i, teacher=teacher_id)
                    new_strategy.save()

                request.session['is_login'] = True
                request.session['user_id'] = teacher_id
                request.session['user_name'] = name
                request.session['is_teacher'] = True
                return redirect('/exercise/test_situation/')

    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/login/login/')
    del request.session['is_login']
    del request.session['user_id']
    del request.session['user_name']
    try:
        del request.session['is_teacher']
    except:
        del request.session['is_student']
    return redirect('/login/login/')
