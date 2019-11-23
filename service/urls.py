from django.urls import path, include

from . import views


urlpatterns = [
    path(
        'games',
        views.Games.as_view(),
        name='all-games'
    ),
    path(
        'games/mygames',
        views.UserGames.as_view(),
        name='user-games'
    ),
    path(
        'games/mygames/<slug:status>',
        views.UserGames.as_view(),
        name='user-games-by-type'
    ),
    path(
        'games/<slug:status>',
        views.Games.as_view(),
        name='games-by-type'
    ),

    # GET: game state of current turn
    # path('game/<int:game>', views.GameStateView.as_view()),
    # # create command
    # path(
    #     'game/<int:game>/command',
    #     views.OrderView.as_view()
    # ),
    # # history of previous turn
    # path('game/<int:game>/<int:turn>', views.GameStateView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
