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

        game_id = kwargs['game']
        turn_id = kwargs.get('turn')

        try:
            game = models.Game.objects.get(id=game_id)
        except models.Game.DoesNotExist:
            error404()

        if turn_id:
            try:
                turn = models.Turn.objects.get(id=turn_id)
            except models.Turn.DoesNotExist:
                error404()
        else:
            try:
                turn = game.get_current_turn()
            except models.Turn.DoesNotExist:
                error404()

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
