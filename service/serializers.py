from core import models
from rest_framework import serializers


class SupplyCenterSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SupplyCenter
        fields = '__all__'


class PieceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Piece
        fields = (
            'id',
            'type',
            'nation',
            'territory',
            'named_coast',
            'retreat_territories',
        )


class TerritorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Territory
        fields = ('id', 'name')


class TerritoryStateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TerritoryState
        fields = ('id', 'controlled_by')
