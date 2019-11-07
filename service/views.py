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

        pieces = models.Piece.objects.filter(turn=turn)
        piece_serializer = serializers\
            .PieceSerializer(pieces, many=True)

        supply_centers = models.SupplyCenter.objects.all()
        supply_center_serializer = serializers\
            .SupplyCenterSerializer(supply_centers, many=True)

        territories = models.Territory.objects.all()
        territory_serializer = serializers\
            .TerritoryStateSerializer(territories, many=True)

        territory_states = models.TerritoryState.objects.filter(turn=turn)
        territory_states_serializer = serializers\
            .TerritoryStateSerializer(territory_states, many=True)

        return Response(
            {
                'pieces': piece_serializer.data,
                'supply_centers': supply_center_serializer.data,
                'territories': territory_serializer.data,
                'territory_states': territory_states_serializer.data
            }
        )
