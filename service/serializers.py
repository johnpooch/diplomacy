from django.contrib.auth.models import User, Group
from . import models
from rest_framework import serializers


class SupplyCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SupplyCenter
        fields = ['territory']


class NationSerializer(serializers.ModelSerializer):
    pieces = serializers.StringRelatedField(many=True, read_only=True)
    supply_centers = serializers.StringRelatedField(many=True, read_only=True,
            source='controlled_supply_centers')

    class Meta:
        model = models.Nation
        fields = ['name', 'supply_centers', 'pieces']


class PieceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Piece
        fields = '__all__'


class TerritorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Territory
        fields = '__all__'
 
