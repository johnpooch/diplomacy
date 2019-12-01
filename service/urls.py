from django.urls import path, include

from . import views


urlpatterns = [
    path(
        'games',
        views.ListGames.as_view(),
        name='all-games'
    ),
    path(
        'games/mygames',
        views.ListUserGames.as_view(),
        name='user-games'
    ),
    path(
        'games/create',
        views.CreateGame.as_view(),
        name='create-game'
    ),
    path(
        'games/mygames/<slug:status>',
        views.ListUserGames.as_view(),
        name='user-games-by-type'
    ),
    path(
        'games/<slug:status>',
        views.ListGames.as_view(),
        name='games-by-type'
    ),
    path(
        'games/<int:game>/join',
        views.JoinGame.as_view(),
        name='join-game'
    ),
    path(
        'game/<int:game>',
        views.GameStateView.as_view(),
        name='game-state'
    ),
    # create command
    path(
        'game/<int:game>/order',
        views.OrderView.as_view(),
        name='create-order'
    ),
    # # history of previous turn
    # path('game/<int:game>/<int:turn>', views.GameStateView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
