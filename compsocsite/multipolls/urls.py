from django.urls import re_path

from . import views

app_name = 'multipolls'
urlpatterns = [
    # create
    re_path(r'^add_step1/$', views.AddStep1, name='AddStep1'), 
    re_path(r'^(?P<pk>[0-9]+)/add_step2/$', views.AddStep2View.as_view(), name='AddStep2'), 
    re_path(r'^(?P<multipoll_id>[0-9]+)/setquestion/$', views.setQuestion, name='setquestion'),     
    re_path(r'^(?P<pk>[0-9]+)/add_step3/$', views.AddStep3View.as_view(), name='AddStep3'),
    re_path(r'^(?P<multipoll_id>[0-9]+)/initial/$', views.setInitialSettings, name='setinitial'), 
    re_path(r'^(?P<pk>[0-9]+)/setvoters/$', views.SetVotersView.as_view(), name='SetVoters'),
    re_path(r'^(?P<multipoll_id>[0-9]+)/voter/add$', views.addVoter, name='addvoter'),
    re_path(r'^(?P<multipoll_id>[0-9]+)/voter/delete$', views.removeVoter, name='delvoter'),
    re_path(r'^(?P<multipoll_id>[0-9]+)/voter/add/group/$', views.addGroupVoters, name='addGroupVoters'),      
    re_path(r'^(?P<multipoll_id>[0-9]+)/voter/delete/group/$', views.removeGroupVoters, name='removeGroupVoters'),      
    
    # settings
    re_path(r'^(?P<pk>[0-9]+)/mpollinfo/$', views.mpollinfoView.as_view(), name='mpollinfo'), 
    re_path(r'^(?P<multipoll_id>[0-9]+)/delete/$', views.deleteMpoll, name='delmpoll'),
    re_path(r'^(?P<multipoll_id>[0-9]+)/edit/basic$', views.editBasicInfo, name='editBasicInfo'),

    # start
    re_path(r'^(?P<multipoll_id>[0-9]+)/progress/$', views.progress, name='progress'), 
    re_path(r'^(?P<multipoll_id>[0-9]+)/start/$', views.start, name='start'), 
        
    # subpoll voting
    re_path(r'^dependency/(?P<combination_id>[0-9]+)/get/$', views.getConditionalResponse, name='dependencyget'),
    re_path(r'^subpoll/(?P<pk>[0-9]+)/dependency/view/$', views.DependencyView.as_view(), name='dependencyview'),
    re_path(r'^subpoll/(?P<question_id>[0-9]+)/dependency/view/prefgraph$', views.updatePrefGraph, name='updatePrefGraph'),
    re_path(r'^subpoll/(?P<question_id>[0-9]+)/dependency/choose$', views.chooseDependency, name='choosedependency'),
    re_path(r'^pref/(?P<combination_id>[0-9]+)/assign$', views.assignPreference, name='assignpreference'),   
]

