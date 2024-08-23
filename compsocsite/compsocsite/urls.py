"""compsocsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  re_path(r'^blog/', include('blog.urls'))
"""
from django.urls import include, re_path
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.conf import settings
from django.views.static import serve
from appauth import views
from polls.views import GMView
from polls.views import GMResultsView
from polls.views import sendMessage
from polls.views import CSPosterView
from polls.views import RGENView
from polls.views import MturkView,RGView

urlpatterns = [
    re_path(r'^$', RedirectView.as_view(url='/polls/main')),
    re_path(r'^polls/', include('polls.urls')),
    re_path(r'^groups/', include('groups.urls')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^auth/', include('appauth.urls')),
    re_path(r'^sessions/', include('sessions_local.urls')),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    re_path(r'^multipolls/', include('multipolls.urls')),
    re_path(r'^GM2017$', GMView.as_view(), name='voting_demo'),
    re_path(r'^message$', sendMessage, name='message'),
    re_path(r'^GM2017$', GMView.as_view(), name='GM_2017'),
    re_path(r'^GM2017results$', GMResultsView.as_view(), name='GM_2017results'),
    
    re_path(r'^gm2017$', GMView.as_view(), name='gm_2017'),
    re_path(r'^CSposter$', CSPosterView.as_view(), name='CS_poster'),
    re_path(r'^csposter$', CSPosterView.as_view(), name='cs_poster'),
    re_path(r'^Exp$', MturkView.as_view(), name='Mturk'),
    re_path(r'^ResearchGroupCN$', RGView.as_view(), name='ResearchGroup'),
    re_path(r'^ResearchGroupEN$', RGENView.as_view(), name='ResearchGroupEN'),
    re_path('accounts/profile', RedirectView.as_view(url='/polls/main')),
    re_path(r'^socialSignup/$', views.socialSignup, name='socialSignup'),
    re_path('accounts/', include('allauth.urls')),  
    
    # user_guide 
    # re_path(r'^docs/$', serve, {'path': 'index.html', 'document_root': 'static/user_guide_vitepress/docs/.vitepress/dist'}),
    re_path('index.html', serve, {'path': 'index.html', 'document_root': 'static/user_guide_vitepress/docs/.vitepress/dist'}),
    re_path(r'^assets/(?P<path>.*)$', serve, {'document_root':'static/user_guide_vitepress/docs/.vitepress/dist/assets'}),
    re_path('hashmap.json', serve, {'path': 'hashmap.json', 'document_root': 'static/user_guide_vitepress/docs/.vitepress/dist'}),      
]
