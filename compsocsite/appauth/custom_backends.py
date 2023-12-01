from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CustomUserModelBackend(ModelBackend):
    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel._default_manager.get(email=username)
        except UserModel.DoesNotExist:
            return None

        if user.password == password:
            return user
        return None