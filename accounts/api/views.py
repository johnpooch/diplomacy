import re

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from knox.models import AuthToken
from rest_framework import generics, permissions
from rest_framework.response import Response

from . import serializers


EMAIL_REGEX = r'^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'


class UserAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_object(self):
        return self.request.user


class RegisterAPIView(generics.GenericAPIView):
    serializer_class = serializers.RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": serializers.UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class LoginAPIView(generics.GenericAPIView):
    serializer_class = serializers.LoginSerializer

    @staticmethod
    def is_using_email(request):
        username = request.data.get('username')
        return username and re.search(EMAIL_REGEX, username)

    def post(self, request, *args, **kwargs):

        # Allow username to be username or email
        using_email = self.is_using_email(request)
        login_kwarg = 'email' if using_email else 'username'
        data = {
            login_kwarg: request.data.get('username'),
            'password': request.data.get('password')
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        user_data = serializers.UserSerializer(user).data
        return Response({
            'user': user_data,
            'token': AuthToken.objects.create(user)[1]
        })


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = serializers.ChangePasswordSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {'id': self.request.user.id}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj
