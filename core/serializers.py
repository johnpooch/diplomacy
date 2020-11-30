from rest_framework import serializers

from core import models


class NamedCoastSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.NamedCoast
        fields = (
            'name',
            'parent',
            'neighbours',
        )


class PieceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Piece
        fields = (
            'type',
            'nation',
        )


class PieceStateSerializer(serializers.ModelSerializer):

    piece = PieceSerializer()
    # TODO remove renaming
    retreating = serializers.SerializerMethodField()

    class Meta:
        model = models.PieceState
        fields = (
            'id',
            'piece',
            'retreating',
            'attacker_territory',
            'territory',
            'named_coast',
        )

    def get_retreating(self, obj):
        return obj.must_retreat

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        territory_representation = representation.pop('piece')
        for key in territory_representation:
            representation[key] = territory_representation[key]
        return representation


class TerritorySerializer(serializers.ModelSerializer):

    named_coasts = NamedCoastSerializer(many=True)

    class Meta:
        model = models.Territory
        fields = (
            'id',
            'type',
            'name',
            'named_coasts',
            'neighbours',
            'shared_coasts',
            'nationality',
            'supply_center',
        )


class TerritoryStateSerializer(serializers.ModelSerializer):

    territory = TerritorySerializer()

    class Meta:
        model = models.TerritoryState
        fields = (
            'contested',
            'controlled_by',
            'territory',
        )

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        territory_representation = representation.pop('territory')
        for key in territory_representation:
            representation[key] = territory_representation[key]
        return representation


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Order
        fields = (
            'id',
            'type',
            'nation',
            'source',
            'target',
            'target_coast',
            'aux',
            'piece_type',
            'via_convoy',
        )


class TurnSerializer(serializers.ModelSerializer):

    pieces = PieceStateSerializer(
        many=True,
        source='piecestates'
    )
    territories = TerritoryStateSerializer(
        many=True,
        source='territorystates'
    )
    orders = OrderSerializer(many=True)
    variant = serializers.SerializerMethodField()

    class Meta:
        model = models.Turn
        fields = (
            'id',
            'territories',
            'pieces',
            'orders',
            'phase',
            'variant',
        )

    def get_variant(self, obj):
        return obj.game.variant.name

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        territories_representation = representation.get('territories')
        named_coasts = []
        for territory in territories_representation:
            named_coasts = [*named_coasts, *territory.pop('named_coasts')]
        representation['named_coasts'] = named_coasts
        return representation
