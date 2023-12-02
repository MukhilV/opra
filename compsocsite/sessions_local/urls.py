from . import views
from django.urls import re_path
from django.contrib.auth.decorators import login_required

app_name = 'sessions_local'
urlpatterns = [
    #Two main types of polls
    re_path(r'^$', login_required(views.SessionsMainView.as_view()), name='sessions_main'),
    re_path(r'^(?P<pk>[0-9]+)/$', views.SessionView.as_view(), name='info'),
    re_path(r'^createsession/$', views.createSession, name='create_session'), 
]