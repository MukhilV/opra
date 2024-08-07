import bcrypt
from django.utils import timezone

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from appauth.models import UserProfile
from polls.models import UnregisteredUser

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def get_user_search_fields(self):
        """
        Return a list of fields that are used to lookup users.
        """
        return ['email']
    
    def is_safe_url(self, url, allowed_hosts, require_https=False):
        """
        This method ensures that URLs are safe.
        """
        return super().is_safe_url(url, allowed_hosts, require_https=require_https)
    
    def new_user(self, request, sociallogin):
        user = super().new_user(request, sociallogin)
        # custom logic here
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin , form)
        email = sociallogin.account.extra_data.get('email')
        user.email = email 
        user.username = email
        user.save()
        
        # If the registering user is invited for any poll, register him automatically to that poll.
        try:
            invited_user = UnregisteredUser.objects.get(email=email)

            # Transfer the invitations
            user.poll_participated.set(invited_user.polls_invited.all())

            # save user
            user.save()

            # Delete the invited user record
            invited_user.delete()
        
        # Do nothing, if the registering user is not invited to any polls
        except UnregisteredUser.DoesNotExist:
            pass

        # Create user profile for the new user
        salt = bcrypt.gensalt()
        profile = UserProfile(user=user, displayPref = 1, time_creation=timezone.now(), salt = salt.decode('utf-8'))
        profile.save()
        
        return user