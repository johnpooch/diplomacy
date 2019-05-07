from django.contrib.auth.models import User, Group
from . import models
from rest_framework import serializers


class SupplyCenterSerializer(serializers.ModelSerializer):
    controlled_by = serializers.StringRelatedField()
    nationality = serializers.StringRelatedField()
    territory = serializers.StringRelatedField()

    class Meta:
        model = models.SupplyCenter
        fields = '__all__'


class NationSerializer(serializers.ModelSerializer):
    pieces = serializers.StringRelatedField(many=True, read_only=True)
    supply_centers = serializers.StringRelatedField(many=True, read_only=True,
            source='controlled_supply_centers')

    class Meta:
        model = models.Nation
        fields = ['name', 'supply_centers', 'pieces']


class PieceSerializer(serializers.ModelSerializer):
    nation = serializers.StringRelatedField()
    territory = serializers.StringRelatedField()
    class Meta:
        model = models.Piece
        fields = '__all__'


class NeighbourSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Territory
        fields = ('display_name',)

    def to_representation(self, value):
        return value.abbreviation

class TerritorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Territory
        depth = 1
        fields = '__all__'
 
    neighbours = NeighbourSerializer(many=True)
