from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from . import views
from . import email
from . import record

app_name = 'polls'
urlpatterns = [
    url(r'^$', login_required(views.IndexView.as_view()), name='index'),
    url(r'^main$', views.MainView.as_view(), name='index_guest'),
    
    #for IRB experiment
    url(r'^IRB/(?P<pk>[0-9]+)/$', views.IRBDetailView.as_view(), name='IRBdetail'),
    url(r'^IRB/(?P<question_id>[0-9]+)/MTurkvote/$', views.MturkVote, name='Mturkvote'),

    #Two main types of polls
    url(r'^regular_polls$', login_required(views.RegularPollsView.as_view()), name='regular_polls'),
    url(r'^regular_polls/(?P<pk>[0-9]+)/folder$', login_required(views.RegularPollsFolderView.as_view()), name='regular_polls_folder'),
    url(r'^m_polls$', login_required(views.MultiPollsView.as_view()), name='m_polls'),
    url(r'^(?P<pk>[0-9]+)/demo$', views.DemoView.as_view(), name='voting_demo'),
   
    # Create a new poll
    url(r'^add_step1/$', views.AddStep1View, name='AddStep1'), 
    url(r'^(?P<pk>[0-9]+)/add_step2/$', views.AddStep2View.as_view(), name='AddStep2'), 
    url(r'^(?P<pk>[0-9]+)/add_step3/$', views.AddStep3View.as_view(), name='AddStep3'),
    url(r'^(?P<pk>[0-9]+)/add_step4/$', views.AddStep4View.as_view(), name='AddStep4'),

    # Create a new folder
    url(r'^add_folder/$', views.addFolder, name='addFolder'),
        
    # choices
    url(r'^(?P<question_id>[0-9]+)/choice/add/$', views.addChoice, name='addchoice'),
    url(r'^(?P<question_id>[0-9]+)/editchoice/$', views.editChoice, name='editchoice'),
    url(r'^(?P<question_id>[0-9]+)/edit/basic/$', views.editBasicInfo, name='editBasicInfo'),
    url(r'^choice/delete/([0-9]+)/$', views.deleteChoice, name='delchoice'),
    
    # voters
    url(r'^(?P<question_id>[0-9]+)/addvoter/$', views.addVoter, name='addvoter'),
    url(r'^(?P<question_id>[0-9]+)/delvoter/$', views.removeVoter, name='delvoter'),
    
    # vote
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),    
    url(r'^(?P<pk>[0-9]+)/confirmation/$', views.ConfirmationView.as_view(), name='confirmation'),
    url(r'^(?P<question_id>[0-9]+)/start/$', views.startPoll, name='start'),
    url(r'^(?P<question_id>[0-9]+)/pause/$', views.pausePoll, name='pause'),
    url(r'^(?P<question_id>[0-9]+)/resume/$', views.resumePoll, name='resume'),
    url(r'^(?P<question_id>[0-9]+)/stop/$', views.stopPoll, name='stop'),
    url(r'^delete/([0-9]+)/$', views.deletePoll, name='delpoll'),
    url(r'^quit/([0-9]+)/$', views.quitPoll, name='quitpoll'),
    url(r'^(?P<pk>[0-9]+)/vote/results/$', cache_page(60)(views.VoteResultsView.as_view()), name='voteresults'),
    url(r'^(?P<pk>[0-9]+)/allocate/results/$', views.AllocateResultsView.as_view(), name='allocate_results'),
    
    # settings
    url(r'^(?P<pk>[0-9]+)/pollinfo/$', views.PollInfoView.as_view(), name='pollinfo'),
    url(r'^(?P<resp_id>[0-9]+)/(?P<key>\w+)/voteEmail/$', email.voteEmail, name='voteEmail'),
    url(r'^(?P<question_id>[0-9]+)/settings/initial$', views.setInitialSettings, name='setinitial'),    
    url(r'^(?P<question_id>[0-9]+)/settings/algorithm$', views.setPollingSettings, name='setPollingSettings'),
    url(r'^(?P<pk>[0-9]+)/allocate/order$', views.AllocationOrder.as_view(), name='viewAllocationOrder'),
    url(r'^(?P<question_id>[0-9]+)/allocate/order/set/$', views.setAllocationOrder, name='setAllocationOrder'),
    #url(r'^(?P<question_id>[0-9]+)/sendEmail/$', views.sendEmail, name='sendEmail'),
    url(r'^(?P<question_id>[0-9]+)/emailNow/$', email.emailNow, name='emailNow'),
    url(r'^(?P<question_id>[0-9]+)/emailOptions/$', email.emailOptions, name='emailOptions'),
    url(r'^(?P<question_id>[0-9]+)/emailSettings/$', email.emailSettings, name='emailSettings'),
    url(r'^(?P<question_id>[0-9]+)/changeType/$', views.changeType, name='changeType'),
    url(r'^(?P<question_id>[0-9]+)/duplicatepoll/$', views.duplicatePoll, name='duppoll'), 
    url(r'^(?P<response_id>[0-9]+)/deleteuservotes/$', views.deleteUserVotes, name='deluservotes'), 
    url(r'^(?P<response_id>[0-9]+)/restoreuservotes/$', views.restoreUserVotes, name='resuservotes'), 
       
    # anonymous voting
    url(r'^(?P<question_id>[0-9]+)/anonymousjoin/$', views.anonymousJoin, name='anonymousjoin'),
    url(r'^(?P<question_id>[0-9]+)/anonymousvote/$', views.anonymousVote, name='anonymousvote'),
    
    # vote result
    url(r'^(?P<question_id>[0-9]+)/calculateprev/$', views.calculatePreviousResults, name='calculateprev'),
    url(r'^(?P<question_id>[0-9]+)/recalculateResult/$', views.recalculateResult, name='recalcResult'),
    
    # user records
    url(r'^(?P<question_id>[0-9]+)/record/$', record.writeUserAction, name='record'),
    url(r'^(?P<pk>[0-9]+)/recordView/$', record.RecordView.as_view(), name='recordView'),
    url(r'^(?P<question_id>[0-9]+)/downloadrecord/$', record.downloadRecord, name='downloadrecord'),
    url(r'^(?P<user_id>[0-9]+)/downloadallrecord/$', record.downloadAllRecord, name='downloadallrecord'),

    # API
    url(r'^API/mixtures/$', views.mixtureAPI, name='mixture_api'),
    url(r'^api/get_polls/', views.get_polls, name='get_polls'),

    # API test
    url(r'^API/mixtures_test/$', views.mixtureAPI_test, name='mixture_api_test'),
    
    # Mturk
    url(r'^getmturklist/$', views.getMturkPollList, name='getmturklist'),
]
