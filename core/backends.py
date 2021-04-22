from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):

    def authenticate(self, *args, email=None, **kwargs):
        """
        Override default authenticate method to allow email to be passed
        instead of username.
        """
        UserModel = get_user_model()
        if email:
            try:
                user = UserModel.objects.get(email=email)
                kwargs['username'] = user.username
            except UserModel.DoesNotExist:
                pass
        return super().authenticate(*args, **kwargs)
