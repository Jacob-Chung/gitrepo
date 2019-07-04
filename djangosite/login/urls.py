from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^index/$', views.index),
    url(r'^login/$', views.login),
    url(r'^register/$', views.register),
    url(r'^logout/$', views.logout),
    url(r'^teacherindex/$', views.teacherindex),
    url(r'^studentindex/$', views.studentindex),
    url(r'^student_center/$', views.student_center),
    url(r'^upload/$', views.uploadImg),
    url(r'^alter_password/$', views.alter_password),
    url(r'^teacher_center/$', views.teacher_center),
    url(r'^teacher_alter_password/$', views.teacher_alter_password),
    url(r'^alter_teacher/$', views.alter_teacher),
    url(r'^bbs_index/$', views.bbs_index),
    url(r'^send_post/$', views.send_post),
    url(r'^add_comment/$', views.add_comment),
    url(r'^post_detail/$', views.post_detail),
    url(r'^support_post/$', views.support_post),
    url(r'^against_post/$', views.against_post),
    url(r'^support_comment/$', views.support_comment),
    url(r'^against_post/$', views.against_comment),
    url(r'^my_post/$', views.my_post),
    url(r'^del_post/$', views.del_post),



    url(r'^test_vi/$', views.test_vi),
]
