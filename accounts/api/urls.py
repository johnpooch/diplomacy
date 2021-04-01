from django.urls import path, include

from knox.views import LogoutView

from . import views

urlpatterns = [
    path(
        '',
        include('knox.urls')
    ),
    path(
        'register',
        views.RegisterAPIView.as_view(),
        name='register',
    ),
    path(
        'login',
        views.LoginAPIView.as_view(),
        name='login'
    ),
    path(
        'logout',
        LogoutView.as_view(),
        name='knox_logout'
    ),
    path(
        'change_password',
        views.ChangePasswordView.as_view(),
        name='change_password'
    ),
]
