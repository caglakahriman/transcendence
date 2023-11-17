from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
'''
class UserBackend(ModelBackend):

    def authenticate(self, request, login=None, token=None):
        
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(login=login)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(token):
                return user

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

        
    def login_required(self, login_url=None):
        if (self.is_authenticated):
            return True
        else:
            return redirect_to_login(login_url=login_url)
        
    @login_required
    def required(self, request):
        return True'''