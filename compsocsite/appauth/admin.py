from django.contrib import admin
from .models import *

class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user','sequence')
	list_filter = ['user']


admin.site.register(UserProfile, UserProfileAdmin)
