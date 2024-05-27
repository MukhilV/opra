from django.urls import re_path
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from . import views
from . import email
from . import record
from . import experiment

app_name = 'polls'
urlpatterns = [
    re_path(r'^$', login_required(views.IndexView.as_view()), name='index'),
    re_path(r'^main$', views.MainView.as_view(), name='index_guest'),
    
    #for IRB experiment
    re_path(r'^Exp/(?P<pk>[0-9]+)/$', views.IRBDetailView.as_view(), name='IRBdetail'),
    re_path(r'^Exp/(?P<question_id>[0-9]+)/MTurkvote/$', views.MturkVote, name='Mturkvote'),
    re_path(r'^Exp/addComments/$', views.ExpAddComment, name='ExpAddComment'),
    re_path(r'^Exp/SurveyCode/$', views.SurveyFinalView.as_view(), name='SurveyCode'),
    re_path(r'^Exp/End/$', views.SurveyEndView.as_view(), name='SurveyEnd'),


    #Two main types of polls
    re_path(r'^regular_polls$', login_required(views.RegularPollsView.as_view()), name='regular_polls'),
    re_path(r'^allocation_tab$', login_required(views.RegularAllocationView.as_view()), name='allocation_tab'),
    re_path(r'^regular_polls/(?P<pk>[0-9]+)/folder$', login_required(views.RegularPollsFolderView.as_view()), name='regular_polls_folder'),
    re_path(r'^m_polls$', login_required(views.MultiPollsView.as_view()), name='m_polls'),
    re_path(r'^(?P<pk>[0-9]+)/demo$', views.DemoView.as_view(), name='voting_demo'),
    re_path(r'^classes$', login_required(views.ClassesView.as_view()), name='classes'),
   
    # Create a new poll
    re_path(r'^add_step1/$', views.AddStep1View, name='AddStep1'), 
    re_path(r'^(?P<pk>[0-9]+)/add_step2/$', views.AddStep2View.as_view(), name='AddStep2'), 
    re_path(r'^(?P<pk>[0-9]+)/add_step3/$', views.AddStep3View.as_view(), name='AddStep3'),
    re_path(r'^(?P<pk>[0-9]+)/add_step4/$', views.AddStep4View.as_view(), name='AddStep4'),

    # Create a new folder
    re_path(r'^add_folder/$', views.addFolder, name='addFolder'),

    # delete folder
    re_path(r'^regular_polls/(?P<folder_id>[0-9]+)/delete_folder/$', views.deleteFolder, name='deleteFolder'),
        
    # choices
    re_path(r'^(?P<question_id>[0-9]+)/choice/add/$', views.addChoice, name='addchoice'),
    re_path(r'^(?P<question_id>[0-9]+)/editchoice/$', views.editChoice, name='editchoice'),
    re_path(r'^(?P<question_id>[0-9]+)/edit/basic/$', views.editBasicInfo, name='editBasicInfo'),
    re_path(r'^choice/delete/([0-9]+)/$', views.deleteChoice, name='delchoice'),
    
    # voters
    re_path(r'^(?P<question_id>[0-9]+)/addvoter/$', views.addVoter, name='addvoter'),
    re_path(r'^(?P<question_id>[0-9]+)/delvoter/$', views.removeVoter, name='delvoter'),

    # save the uploaded csv text
    re_path(r'^(?P<question_id>[0-9]+)/savelatestcsv/$', views.saveLatestCSV, name='savelatestcsv'),

    # send email invite to participants
    re_path(r'^(?P<question_id>[0-9]+)/sendemailinvite/$', views.sendEmailInvite, name='sendemailinvite'),
    
    # vote
    re_path(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    re_path(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),    
    re_path(r'^(?P<pk>[0-9]+)/confirmation/$', views.ConfirmationView.as_view(), name='confirmation'),
    re_path(r'^(?P<question_id>[0-9]+)/start/$', views.startPoll, name='start'),
    re_path(r'^(?P<question_id>[0-9]+)/pause/$', views.pausePoll, name='pause'),
    re_path(r'^(?P<question_id>[0-9]+)/resume/$', views.resumePoll, name='resume'),
    re_path(r'^(?P<question_id>[0-9]+)/stop/$', views.stopPoll, name='stop'),
    re_path(r'^delete/([0-9]+)/$', views.deletePoll, name='delpoll'),
    re_path(r'^quit/([0-9]+)/$', views.quitPoll, name='quitpoll'),
    re_path(r'^(?P<pk>[0-9]+)/vote/results/$', cache_page(60)(views.VoteResultsView.as_view()), name='voteresults'),
    re_path(r'^(?P<pk>[0-9]+)/allocate/results/$', views.AllocateResultsView.as_view(), name='allocate_results'),
    
    # settings
    re_path(r'^(?P<pk>[0-9]+)/pollinfo/$', views.PollInfoView.as_view(), name='pollinfo'),
    re_path(r'^(?P<resp_id>[0-9]+)/(?P<key>\w+)/voteEmail/$', email.voteEmail, name='voteEmail'),
    re_path(r'^(?P<question_id>[0-9]+)/settings/initial$', views.setInitialSettings, name='setinitial'),    
    re_path(r'^(?P<question_id>[0-9]+)/settings/algorithm$', views.setPollingSettings, name='setPollingSettings'),
    re_path(r'^(?P<pk>[0-9]+)/allocate/order$', views.AllocationOrder.as_view(), name='viewAllocationOrder'),
    re_path(r'^(?P<question_id>[0-9]+)/allocate/order/set/$', views.setAllocationOrder, name='setAllocationOrder'),
    #re_path(r'^(?P<question_id>[0-9]+)/sendEmail/$', views.sendEmail, name='sendEmail'),
    re_path(r'^(?P<question_id>[0-9]+)/emailNow/$', email.emailNow, name='emailNow'),
    re_path(r'^(?P<question_id>[0-9]+)/emailOptions/$', email.emailOptions, name='emailOptions'),
    re_path(r'^(?P<question_id>[0-9]+)/emailSettings/$', email.emailSettings, name='emailSettings'),
    re_path(r'^(?P<question_id>[0-9]+)/changeType/$', views.changeType, name='changeType'),
    re_path(r'^(?P<question_id>[0-9]+)/duplicatepoll/$', views.duplicatePoll, name='duppoll'), 
    re_path(r'^(?P<response_id>[0-9]+)/deleteuservotes/$', views.deleteUserVotes, name='deluservotes'), 
    re_path(r'^(?P<response_id>[0-9]+)/restoreuservotes/$', views.restoreUserVotes, name='resuservotes'), 
       
    # anonymous voting
    re_path(r'^(?P<question_id>[0-9]+)/anonymousjoin/$', views.anonymousJoin, name='anonymousjoin'),
    re_path(r'^(?P<question_id>[0-9]+)/anonymousvote/$', views.anonymousVote, name='anonymousvote'),
    
    # vote result
    re_path(r'^(?P<question_id>[0-9]+)/calculateprev/$', views.calculatePreviousResults, name='calculateprev'),
    re_path(r'^(?P<question_id>[0-9]+)/recalculateResult/$', views.recalculateResult, name='recalcResult'),
    
    # user records
    re_path(r'^(?P<question_id>[0-9]+)/record/$', record.writeUserAction, name='record'),
    re_path(r'^(?P<pk>[0-9]+)/recordView/$', record.RecordView.as_view(), name='recordView'),
    re_path(r'^(?P<question_id>[0-9]+)/downloadrecord/$', record.downloadRecord, name='downloadrecord'),
    re_path(r'^(?P<user_id>[0-9]+)/downloadallrecord/$', record.downloadAllRecord, name='downloadallrecord'),
    re_path(r'^downloadpolls/$', record.downloadPolls, name='downloadpolls'),
    re_path(r'^downloadparticipants/$', record.downloadParticipants, name='downloadparticipants'),
    re_path(r'^downloadallrecords/$', record.downloadRecords, name='downloadallrecords'),
    re_path(r'^downloadspecrecords/$', record.downloadSpecificRecords, name='downloadspecrecords'),

    # API
    re_path(r'^API/mixtures/$', views.mixtureAPI, name='mixture_api'),
    re_path(r'^api/get_polls/', views.get_polls, name='get_polls'),
    re_path(r'^api/get_voters/', views.get_voters, name='get_voters'),

    # API test
    re_path(r'^API/mixtures_test/$', views.mixtureAPI_test, name='mixture_api_test'),
    re_path(r'^testServer/$', views.test_server, name='test_server'),
    re_path(r'^delete_messages/$', views.delete_messages, name='delete_messages'),
    re_path(r'^get_resp_num/$', views.get_num_responses, name='get_resp_num'),
    
    # Mturk
    re_path(r'^getmturklist/$', views.getMturkPollList, name='getmturklist'),
    re_path(r'^experiment/add$', experiment.createNewExperiment, name='experimentcreate'),
    re_path(r'^experiment/(?P<pk>[0-9]+)/detail$', experiment.ExperimentSetup.as_view(), name='experimentdetail'),
    re_path(r'^experiment/addpoll/(?P<exp_id>[0-9]+)$', experiment.addPollToExperiment, name='addpolltoexp'),

    # classes
    re_path(r'^newClass/$', views.newClass, name='newClass'),
    re_path(r'^class/(?P<pk>[0-9]+)/takeAttendance/$', views.takeAttendance, name='takeAttendance'),
    re_path(r'^class/(?P<pk>[0-9]+)/stopAttendance/$', views.stopAttendance, name='stopAttendance'),
    re_path(r'^class/(?P<pk>[0-9]+)/classSignIn/$', views.classSignIn, name='classSignIn'),
    re_path(r'^class/(?P<pk>[0-9]+)/newQuiz/$', views.newQuiz, name='newQuiz'),
    re_path(r'^class/(?P<pk>[0-9]+)/grades/$', views.GradesView.as_view(), name='grades'),
    re_path(r'^class/(?P<pk>[0-9]+)/gradesCSV/$', views.GradesDownload, name='gradesCSV'),
    re_path(r'^class/(?P<question_id>[0-9]+)/attendclass/$', views.attendanceSignIn, name='attendclass'),
    #re_path(r'^(?P<pk>[0-9]+)/qrcode/$', views.QRView.as_view(), name='qrview'),

    # self sign up
    re_path(r'^(?P<question_id>[0-9]+)/changeselfsignup/$', views.change_self_sign_up, name='changeselfsignup'),
    re_path(r'^(?P<question_id>[0-9]+)/selfsignup/$', views.self_sign_up, name='selfsignup'),
    re_path(r'^request/(?P<request_id>[0-9]+)/approve/$', views.approve_request, name='approverequest'),
    re_path(r'^(?P<pk>[0-9]+)/selfregister/$', views.SelfRegisterView.as_view(), name='selfregister'),

]
