from django.shortcuts import get_object_or_404
from rest_framework import views
from rest_framework.response import Response

from core import models
from service import serializers

from rest_framework.exceptions import NotFound


def error404():
    raise NotFound(detail="Error 404, page not found", code=404)


class GameStateView(views.APIView):
    """
    Provides the data necessary to render the game board at the current state.
    """
    def get(self, request, format=None, **kwargs):

        # TODO authentication

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
