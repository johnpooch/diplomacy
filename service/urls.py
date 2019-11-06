from django.urls import path, include

from . import views


urlpatterns = [
    path('game-state/', views.GameStateView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
