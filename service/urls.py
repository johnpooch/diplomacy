from django.urls import path, re_path, include

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
    re_path(
        r'game/(?P<slug>[_\-\w]+)/join',
        views.ToggleJoinGame.as_view(),
        name='toggle-join-game'
    ),
    re_path(
        r'game/finalize/(?P<pk>[0-9]+)',
        views.ToggleFinalizeOrdersView.as_view(),
        name='toggle-finalize-orders'
    ),
    # TODO these three should be a ViewSet
    re_path(
        r'game/(?P<slug>[_\-\w]+)/order$',
        views.CreateOrderView.as_view(),
        name='order'
    ),
    re_path(
        r'game/(?P<pk>[0-9]+)/orders$',
        views.ListOrdersView.as_view(),
        name='orders'
    ),
    re_path(
        r'game/order/(?P<pk>[0-9]+)$',
        views.DestroyOrderView.as_view(),
        name='destroy-order'
    ),
    re_path(
        r'game/(?P<slug>[_\-\w]+)$',
        views.GameStateView.as_view(),
        name='game-state'
    ),
    path(
        'variants',
        views.ListVariants.as_view(),
        name='list-variants'
    ),
    re_path(
        r'surrender/(?P<turn>[0-9]+)/(?P<pk>[0-9]+)',
        views.ToggleSurrenderView.as_view(),
        name='cancel-surrender',
    ),
    re_path(
        r'surrender/(?P<turn>[0-9]+)',
        views.ToggleSurrenderView.as_view(),
        name='surrender',
    ),
    re_path(
        r'cancel-draw/(?P<turn>[0-9]+)/(?P<pk>[0-9]+)',
        views.CancelDraw.as_view(),
        name='cancel-draw',
    ),
    re_path(
        r'propose-draw/(?P<turn>[0-9]+)',
        views.ProposeDraw.as_view(),
        name='propose-draw',
    ),
    re_path(
        r'draw-response/(?P<draw>[0-9]+)/(?P<pk>[0-9]+)',
        views.DrawResponse.as_view(),
        name='cancel-draw-response',
    ),
    re_path(
        r'draw-response/(?P<draw>[0-9]+)',
        views.DrawResponse.as_view(),
        name='draw-response',
    ),
    path(
        'password_reset/',
        include('django_rest_passwordreset.urls', namespace='password_reset')
    ),
    path(
        'api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    ),
]
