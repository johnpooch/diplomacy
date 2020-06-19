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
        name='list-games'
    ),
    path(
        'games/create',
        views.CreateGameView.as_view(),
        name='create-game'
    ),
    path(
        'game/<int:pk>/join',
        views.ToggleJoinGame.as_view(),
        name='toggle-join-game'
    ),
    path(
        'game/finalize/<int:pk>',
        views.FinalizeOrdersView.as_view(),
        name='finalize-orders'
    ),
    path(
        'game/<int:pk>',
        views.GameStateView.as_view(),
        name='game-state'
    ),
    path(
        'game/<int:game>/order',
        views.CreateOrderView.as_view(),
        name='order'
    ),
    path(
        'game/<int:game>/orders',
        views.ListOrdersView.as_view(),
        name='orders'
    ),
    path(
        'game/<int:game>/nation-state',
        views.RetrievePrivateNationStateView.as_view(),
        name='private-nation-state'
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
