# coding=UTF-8
from django.conf.urls import url

from djangosite import settings
from exercise import views

urlpatterns = [
    # 学生
    url(r'^my_mission/$', views.my_mission),
    url(r'^do_compose/$', views.do_compose),
    url(r'^submit_compose/$', views.submit_compose),
    url(r'^change_chapter/$', views.change_chapter),
    url(r'^chapter_test/$', views.chapter_test),
    url(r'^submit_paper/$', views.submit_paper),
    url(r'^submit_final/$', views.submit_final),
    url(r'^final_test/$', views.final_test),
    url(r'^mytest/$', views.mytest),
    url(r'^my_compose_test/$', views.my_compose_test),
    url(r'^change_chapter_mytest/$', views.change_chapter_mytest),

    # 测试
    url(r'^select_chapter/$', views.select_chapter),
    url(r'^upload/$', views.uploadImg),
    url(r'^getUpload/$', views.getUpload),
    url(r'^show/$', views.show_pic),
    url(r'^tetest/$', views.tetest),


    # 老师
    url(r'^compose_test/$', views.compose_test),
    url(r'^compose_choice/$', views.compose_choice),
    url(r'^compose_situation/$', views.compose_situation),
    url(r'^submit_choice/$', views.submit_choice),
    url(r'^compose_fillin/$', views.compose_fillin),
    url(r'^submit_fillin/$', views.submit_fillin),
    url(r'^test_situation/$', views.test_situation),
    url(r'^chapter_situation/$', views.chapter_situation),
    url(r'^set_rules/$', views.set_rules),
    url(r'^uploadFillin/$', views.uploadFillin),
    url(r'^fillin_upload/$', views.fillin_upload),
    url(r'^choice_upload/$', views.choice_upload),
    url(r'^uploadGrade/$', views.uploadGrade),
    url(r'^question_bank/$', views.question_bank),
    url(r'^all_student/$', views.all_student),
    url(r'^del_student/$', views.del_student),
    url(r'^filter_student/$', views.filter_student),
    url(r'^view_student/$', views.view_student),
    url(r'^update_student/$', views.update_student),
    url(r'^del_choice/$', views.del_choice),
    url(r'^view_choice/$', views.view_choice),
    url(r'^update_choice/$', views.update_choice),
    url(r'^del_fillin/$', views.del_fillin),
    url(r'^view_fillin/$', views.view_fillin),
    url(r'^update_fillin/$', views.update_fillin),
    url(r'^insert_choice/$', views.insert_choice),
    url(r'^insert_fillin/$', views.insert_fillin),
    url(r'^student_upload/$', views.student_upload),
    url(r'^uploadStudent/$', views.uploadStudent),
    url(r'^insert_student/$', views.insert_student),


    # url(r'asset_show_table/$', views.show_asset_in_table, name='show_asset_in_table'),  # 展示资产信息在bootstrap-table里面


]

