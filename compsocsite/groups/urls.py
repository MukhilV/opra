from django.urls import re_path

from . import views

app_name = 'groups'
urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(r'^add/$', views.addGroupView.as_view(), name='addgroup'),
    re_path(r'^addgroupfunc/$', views.addgroup, name='addgroupfunc'),
    re_path(r'^delete/([0-9]+)/$', views.deletegroup, name='deletegroup'),
    re_path(r'^(?P<pk>[0-9]+)/members/$', views.MembersView.as_view(), name='members'),
    re_path(r'^(?P<group_id>[0-9]+)/members/add/$', views.addmember, name='addmember'),    
    re_path(r'^(?P<group_id>[0-9]+)/members/remove/$', views.removemember, name='removemember'),
    re_path(r'^(?P<question_id>[0-9]+)/addgroupvoters/$', views.addgroupvoters, name='addgroupvoters'),    
    re_path(r'^(?P<question_id>[0-9]+)/removegroupvoters/$', views.removegroupvoters, name='removegroupvoters'),  
    re_path(r'^(?P<group_id>[0-9]+)/join/$', views.joingroup, name='join'),
    re_path(r'^(?P<group_id>[0-9]+)/open/$', views.opengroup, name='open'),
    re_path(r'^(?P<group_id>[0-9]+)/close/$', views.closegroup, name='close'),
]