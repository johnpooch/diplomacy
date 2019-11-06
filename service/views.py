from rest_framework import views
from rest_framework.response import Response

from core import models
from service import serializers


class GameStateView(views.APIView):
    """
    """
    def get(self, request, format=None, **kwargs):

        pieces = models.Piece.objects.all()
        piece_serializer = serializers\
            .PieceSerializer(pieces, many=True)

        supply_centers = models.SupplyCenter.objects.all()
        supply_center_serializer = serializers\
            .SupplyCenterSerializer(supply_centers, many=True)

        territories = models.Territory.objects.all()
        territory_serializer = serializers\
            .TerritorySerializer(territories, many=True)

        return Response(
            {
                'pieces': piece_serializer.data,
                'supply_centers': supply_center_serializer.data,
                'territories': territory_serializer.data
            }
        )
