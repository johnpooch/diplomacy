from django.urls import path, include

from knox.views import LogoutView

from .views import RegisterAPIView, LoginAPIView

urlpatterns = [
    path(
        '',
        include('knox.urls')
    ),
    path(
        'register',
        RegisterAPIView.as_view(),
        name='register',
    ),
    path(
        'login',
        LoginAPIView.as_view(),
        name='login'
    ),
    path(
        'logout',
        LogoutView.as_view(),
        name='knox_logout'
    )
]