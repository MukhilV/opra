import datetime
import os

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.urls import reverse
from django.views import generic

from .models import *

from django.utils import timezone
from django.template import RequestContext
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.core import mail
from prefpy.mechanism import *
from groups.models import *
from django.conf import settings
import random
import string
import threading

def switchModel(type, question, request):
    if type == 'invite' or type == 'invite-group':
        email = Email.objects.filter(question=question, type=1)
    if type == 'remove' or type == 'remove-group':
        email = Email.objects.filter(question=question, type=2)
    if type == 'start':
        email = Email.objects.filter(question=question, type=3)
    if type == 'stop':
        email = Email.objects.filter(question=question, type=4)
    if type == 'now':
        return [request.POST.get('subject'), request.POST.get('message')]
    if type == 'invite-csv':
        email = Email.objects.filter(question=question, type=5)
    if len(email) != 1:
        setupEmail(question)
    return [email[0].subject, email[0].message]

def setupEmail(question):
    title = question.question_text
    creator = question.question_owner.username

    # Setup/Update the Email subject and body for inviting users
    emailInvite = Email.objects.filter(question=question, type=1)
    if not emailInvite.exists():
        emailInvite = Email(question=question, type=1,
            subject="You have been invited to vote on " + title,
            message='Hello [user_name],\n\n' + creator
                    + ' has invited you to vote on a poll. Please login at [url] to check it out.\n\nSincerely,\nOPRA Staff')
        emailInvite.save()
    else:
        emailInvite.update(subject="You have been invited to vote on " + title,
            message='Hello [user_name],\n\n' + creator
                    + ' has invited you to vote on a poll. Please login at [url] to check it out.\n\nSincerely,\nOPRA Staff')
        
    # Setup/Update the Email subject and body for removing users
    emailRemove = Email.objects.filter(question=question, type=2)
    if not emailRemove.exists():
        emailRemove = Email(question=question, type=2,
            subject="You have been removed from " + title,
            message='Hello [user_name],\n\n' + creator
                    + ' has deleted you from a poll.\n\nSincerely,\nOPRAH Staff')
        emailRemove.save()
    else:
        emailRemove.update(subject="You have been removed from " + title,
            message='Hello [user_name],\n\n' + creator
                    + ' has deleted you from a poll.\n\nSincerely,\nOPRAH Staff')
    
    # Setup/Update the Email subject and body while starting an instance
    emailStart = Email.objects.filter(question=question, type=3)
    if not emailStart.exists():
        emailStart = Email(question=question, type=3,
            subject=title + ' has started!',
            message='Hello [user_name],\n\n' + creator
                    + ' has started a poll. It is now available to vote on at [url] \n\nSincerely,\nOPRA Staff')
        emailStart.save()
    else:
        emailStart.update(subject=title + ' has started!',
            message='Hello [user_name],\n\n' + creator
                    + ' has started a poll. It is now available to vote on at [url] \n\nSincerely,\nOPRA Staff')
    
    # Setup/Update the Email subject and body while stopping an instance
    emailStop = Email.objects.filter(question=question, type=4)
    if not emailStop.exists():
        emailStop = Email(question=question, type=4,
            subject=title + ' has stopped',
            message='Hello [user_name],\n\n' + creator
                    + ' has ended a poll. Please visit [url] to view the decision.\n\nSincerely,\nOPRA Staff')
        emailStop.save()
    else:
        emailStop.update(subject=title + ' has stopped',
            message='Hello [user_name],\n\n' + creator
                    + ' has ended a poll. Please visit [url] to view the decision.\n\nSincerely,\nOPRA Staff')
        
    # Setup/Update the Email subject and body inviting users by giving CSV email-IDs
    emailInviteCSV = Email.objects.filter(question=question, type=5)
    if not emailInviteCSV.exists():
        emailInviteCSV = Email(question=question, type=5,
            subject="You have been invited to vote on " + title,
            message='Hello [user_name],\n\n' + creator
                    + ' has invited you to vote on a poll. Please login at [url] to check it out.'
                    +' \n Email Invite from CSV. \n\nSincerely,\nOPRA Staff')
        emailInviteCSV.save()
    else:
        emailInviteCSV.update(subject="You have been invited to vote on " + title,
            message='Hello [user_name],\n\n' + creator
                    + ' has invited you to vote on a poll. Please login at [url] to check it out.'
                    +' \n Email Invite from CSV. \n\nSincerely,\nOPRA Staff')



def emailSettings(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if(request.POST.get('mailNotificationSubject1') is not None): 
        emailInvite = Email.objects.filter(question=question, type=1)[0]
        emailInvite.subject = request.POST.get('mailNotificationSubject1')
        emailInvite.message = request.POST.get('mailNotificationBody1')
        emailInvite.save()
        question.emailInvite = request.POST.get('email') == 'email'
    
    if(request.POST.get('mailNotificationSubject') is not None): 
        emailDelete = Email.objects.filter(question=question, type=2)[0]
        emailDelete.subject = request.POST.get('mailNotificationSubject')
        emailDelete.message = request.POST.get('mailNotificationBody')
        emailDelete.save()
        question.emailDelete = request.POST.get('email') == 'email'
    
    if(request.POST.get('startSubject') is not None): 
        emailStart = Email.objects.filter(question=question, type=3)[0]
        emailStart.subject = request.POST.get('startSubject')
        emailStart.message = request.POST.get('startMessage')
        emailStart.save()
        question.emailStart = request.POST.get('emailStart') == 'email'
    
    if(request.POST.get('stopSubject') is not None): 
        emailStop = Email.objects.filter(question=question, type=4)[0]
        emailStop.subject = request.POST.get('stopSubject')
        emailStop.message = request.POST.get('stopMessage')
        emailStop.save()
        question.emailStop = request.POST.get('emailStop') == 'email'

    if(request.POST.get('mailSubject') is not None): 
        emailInviteCSV = Email.objects.filter(question=question, type=5)[0]
        emailInviteCSV.subject = request.POST.get('mailSubject')
        emailInviteCSV.message = request.POST.get('mailBody')
        emailInviteCSV.save()
        question.emailInviteCSV = request.POST.get('email') == 'email'
        
    question.save()
    request.session['setting'] = 5
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def voteEmail(request, key, resp_id):
    eResp = get_object_or_404(EmailResponse, pk=resp_id, identity=key)
    question = eResp.item.question
    if question.status == 2:
        arr = question.item_set.all().exclude(pk=eResp.item.pk)
        prefOrder = ["item" + eResp.item.item_text]
        for a in arr:
            prefOrder.append("item" + a.item_text)
        
        # make Response object to store data
        response = Response(question=question, user=eResp.user, timestamp=timezone.now())
        response.save()
        d = response.dictionary_set.create(name = eResp.user.username + " Preferences")

        # find ranking student gave for each item under the question
        item_num = 1
        for item in question.item_set.all():
            arrayIndex = prefOrder.index("item" + str(item))
            
            if arrayIndex == -1:
                # set value to lowest possible rank
                d[item] = question.item_set.all().count()
            else:
                # add 1 to array index, since rank starts at 1
                rank = (prefOrder.index("item" + str(item))) + 1
                # add pref to response dict
                d[item] = rank
            d.save()
            item_num += 1

        #get current winner
        old_winner = OldWinner(question=question, response=response)
        old_winner.save()

        return HttpResponseRedirect(reverse('polls:confirmation', args=(question.id,)))

def translateEmail(text, uname, url):
    text = text.replace("[user_name]", uname)
    text = text.replace("[url]", url)
    return text

def translateHTML(text, uname, url, options):
    text = translateEmail(text, uname, url)
    text = "<p>" + text + "</p>"
    text = text.replace("\n\n", "</p><br /><p>")
    text = text.replace("\n", "</p><p>")
    text += options
    return text


#function to send email
def emailNow(request, question_id):
    email_class = EmailThread(request, question_id, "now")
    email_class.start()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#function to send email
def emailOptions(request, question_id):
    email_class = EmailThread(request, question_id, "start")
    email_class.start()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
def getOptions(items):
    arr = []
    for item in items:
        arr.append(item.item_text)
    return arr

class EmailThread(threading.Thread):
    def __init__(self, request, question_id, type, voters=None, mail_sub = None, mail_body = None):
        threading.Thread.__init__(self)
        self.question = get_object_or_404(Question, pk=question_id)
        self.type = type
        self.request = request
        self.email = switchModel(type, self.question, request)
        self.title = self.question.question_text
        self.creator_obj = User.objects.get(id=self.question.question_owner_id)
        self.creator = self.creator_obj.username
        if self.creator_obj.first_name != "":
            self.creator = self.creator_obj.first_name + " " + self.creator_obj.last_name

        if type == 'remove':
            self.voters = request.POST.getlist('voters')
        elif type == 'invite' or  type == 'invite-group' or type == 'invite-csv' or type == 'remove-group':
            self.voters = voters
        else:
            self.voters = self.question.question_voters.all()

        if mail_sub: self.email[0] = mail_sub
        if mail_body: self.email[1] = mail_body


    def run(self):
        options = ''
        if self.type == 'invite-csv':
            for voter in self.voters:
                name, uname = voter, voter
                url = self.request.build_absolute_uri(reverse('appauth:login')+'?name='+uname)
                mail.send_mail(translateEmail(self.email[0], name, url),
                    translateEmail(self.email[1], name, url),
                    'opra@cs.binghamton.edu',[voter],
                    html_message=translateHTML(self.email[1], name, url, options))
            return 
                

        for voter in self.voters:
            if self.type == 'invite' or self.type == 'remove' or self.type == 'invite-group' or self.type == 'remove-group':
                voter = get_object_or_404(User, username=voter)
            name = voter.username
            uname = voter.username
            # if self.question.poll_algorithm == 1 and self.type == 'start':
            #     items = Item.objects.all().filter(question=self.question)
            #     item_array = getOptions(items)
            #     options = ''
            #     for i in items:
            #         rand = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
            #         response = EmailResponse(item=i, user=voter, identity=rand)
            #         response.save()
            #         options += '<p><a href=\'' + self.request.build_absolute_uri(reverse('polls:index') + str(response.pk) + "/" + rand + "/voteEmail/") + '\'>' + i.item_text + '</a></p>'
            if voter.first_name != "":
                name = voter.first_name + " " + voter.last_name
            url = self.request.build_absolute_uri(reverse('appauth:login')+'?name='+uname)
            mail.send_mail(translateEmail(self.email[0], name, url),
                translateEmail(self.email[1], name, url),
                'opra@cs.binghamton.edu',[voter.email],
                html_message=translateHTML(self.email[1], name, url, options))