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

    piece = PieceSerializer()

    class Meta:
        model = models.Territory
        fields = ('id', 'name', 'piece')


class TerritoryStateSerializer(serializers.ModelSerializer):

    territory = TerritorySerializer()

    class Meta:
        model = models.TerritoryState
        depth = 1
        fields = ('territory', 'controlled_by')

    def to_representation(self, obj):
        """
        Flatten territory state and territory.
        """
        representation = super().to_representation(obj)
        territory_representation = representation.pop('territory')
        for key in territory_representation:
            representation[key] = territory_representation[key]

        return representation


class NationStateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.NationState
        depth = 1
        fields = ('nation', 'surrendered', 'surrendered_turn')
