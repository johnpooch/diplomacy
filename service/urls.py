from django.urls import path, include

from . import views


urlpatterns = [
    path(
        'game-filter-choices',
        views.GameFilterChoicesView.as_view(),
        name='game-filter-choices'
    ),
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
        'game/<int:game>/join',
        views.JoinGame.as_view(),
        name='join-game'
    ),
    path(
        'game/<int:game>/finalize',
        views.FinalizeOrdersView.as_view(),
        name='finalize-orders'
    ),
    path(
        'game/<int:game>/unfinalize',
        views.UnfinalizeOrdersView.as_view(),
        name='unfinalize-orders'
    ),
    path(
        'game/<int:game>',
        views.GameStateView.as_view(),
        name='game-state'
    ),
    path(
        'game/<int:game>/order',
        views.CreateOrderView.as_view(),
        name='order'
    ),
    path(
        'game/<int:game>/order/<int:pk>',
        views.DestroyOrderView.as_view(),
        name='order'
    ),
    path(
        'api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    )
]
