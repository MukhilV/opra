from django.urls import re_path, include
#import cas.middleware

from . import views

app_name = 'appauth'
urlpatterns = [
    re_path(r'^register/$', views.register, name='register'),
    re_path(r'^login/$', views.user_login, name='login'),
    re_path(r'^login/forgetpassword/$', views.forgetPassword, name='forgetpassword'),
    re_path(r'^login/forgetpasswordview/$', views.forgetPasswordView, name='forgetpasswordview'),
    re_path(r'^resetpassword/(?P<key>\w+)/$', views.resetPage, name='resetpasswordview'),
    re_path(r'^resetpassword/change/(?P<key>\w+)/$', views.resetPassword, name='resetpassword'),
    re_path(r'^logout/$', views.user_logout, name='logout'),
    re_path(r'^settings/$', views.displaySettings, name='settings'),
    re_path(r'^passwordpage/$', views.changePasswordView, name='passwordpage'),
    re_path(r'^passwordpage/changepassword/$', views.changepassword, name='changepassword'),
    re_path(r'^settings/global/$', views.globalSettings, name='globalSettings'),
    re_path(r'^settings/update/$', views.updateSettings, name='updateSettings'),
    re_path(r'^settings/diablehint/$', views.disableHint, name='disableHint'),
    re_path(r'^settings/update/global$', views.updateGlobalSettings, name='updateGlobalSettings'),
	re_path(r'^register/confirm/(?P<key>\w+)/$',views.confirm, name='confirm'),
    re_path(r'^messages$', views.MessageView.as_view(), name='messages'),
    re_path(r'^(?P<question_id>[0-9]+)/quickregister/$', views.quickRegister, name='quickregister'),
    re_path(r'^(?P<question_id>[0-9]+)/quickconfirm/(?P<key>\w+)/$', views.quickConfirm, name='quickconfirm'),
    re_path(r'^(?P<key>\w+)/(?P<question_id>[0-9]+)/quicklogin/$', views.quickLogin, name='quickLogin'),
    re_path(r'^createmturk/$', views.createMturkUser, name='createmturk'),
    re_path(r'^resetfinish/$', views.resetAllFinish, name='resetfinish'),
    re_path('accounts/', include('allauth.urls'))
]