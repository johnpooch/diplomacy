from django.urls import path, include

from . import views


urlpatterns = [
    path('games', views.Games.as_view(), name='all-games'),
    path('games/<slug:filter>', views.Games.as_view(), name='games'),
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
