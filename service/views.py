from django.db.models import Count, F
from django.shortcuts import get_object_or_404

from rest_framework import generics, mixins, status, views
from rest_framework import permissions as drf_permissions
from rest_framework.response import Response

from core import models
from core.models.base import GameStatus
from service import serializers
from service import permissions as custom_permissions

from rest_framework.exceptions import NotFound


def error404():
    raise NotFound(detail="Error 404, page not found", code=404)


# TODO all views need to be refactored using django rest mixins etc.

# TODO stub out all the views and urls before writing any more code. Also write
# these views using TDD.

# TODO ignore permissions at first. Add them in after the basic views are done.

"""
Users
* Register
* Log in
* Log out
* User status (e.g. unread messages, pending orders)

Games
* Get games (also filters)
* User's games
* Create game
* Join game

Game State
* Get game state
* Get game history
* Get order history

Orders
* Add order
* Finalize orders

Messages and announcements
* Create message
* Get messages
"""


class GameStateView(views.APIView):

    def get(self, request, format=None, **kwargs):
        """
        Provides the data necessary to render the game board state at the given
        turn.
        """
        game_id = kwargs['game']
        turn_id = kwargs.get('turn')

        game = get_object_or_404(models.Game, id=game_id)

        if not turn_id:
            turn = game.get_current_turn()
        else:
            turn = get_object_or_404(models.Turn, id=turn_id)

        territory_states = models.TerritoryState.objects.filter(turn=turn)
        territory_states_serializer = serializers\
            .TerritoryStateSerializer(territory_states, many=True)

        nation_states = models.NationState.objects.filter(turn=turn)
        nation_states_serializer = serializers\
            .NationStateSerializer(nation_states, many=True)

        return Response(
            {
                'territory_states': territory_states_serializer.data,
                'nation_states': nation_states_serializer.data,
            }
        )


class Games(generics.ListAPIView):

    permission_classes = [drf_permissions.IsAuthenticated]

    queryset = models.Game.objects.all()
    serializer_class = serializers.GameSerializer

    def get(self, request, *args, **kwargs):
        status = kwargs.get('status')

        if status:
            if status == 'joinable':
                self.queryset = self.queryset.filter_by_joinable(request.user)
            else:
                self.queryset = self.queryset.filter(status=status)

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UserGames(Games):

    def get(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(participants=request.user)
        return super().get(request, *args, **kwargs)


class OrderView(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):

    # TODO add is participant permission
    permission_classes = [drf_permissions.IsAuthenticated]

    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Override create method to save ``created_by`` field.
        """
        game_id = kwargs['game']
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        game = models.Game.objects.get(id=game_id)
        turn = game.get_current_turn()
        user_nation_state = models.NationState.objects.get(
            turn=turn,
            user=request.user
        )
        order = models.Order.objects.get_or_create(
            nation_state=user_nation_state,
        )[0]
        serializer.save(order=order)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
