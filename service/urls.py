from django.urls import path, include

from . import views


urlpatterns = [
    path('game', views.GameList.as_view()),
    path('game-state/<int:game>', views.GameStateView.as_view()),
    path('game-state/<int:game>/<int:turn>', views.GameStateView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
