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


class VariantSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Variant
        fields = ('name', 'max_num_players', 'nations')


class GameSerializer(serializers.ModelSerializer):

    variant = VariantSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(
        source='variant',
        queryset=models.Variant.objects.all(),
    )

    class Meta:
        model = models.Game
        fields = (
            'name',
            'variant',
            'variant_id',
            'private',
            'password',
            'order_deadline',
            'retreat_deadline',
            'build_deadline',
            'process_on_finalized_orders',
            'nation_choice_mode',
            'num_players',
            'participants',
            'created_at',
            'created_by',
            'status',
        )
        read_only_fields = (
            'participants',
            'created_by',
            'created_at',
            'status',
        )


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Order
        fields = (
            'id',
            'type',
            'nation_state',
            'source',
            'piece',
            'target',
            'target_coast',
            'aux',
            'piece_type',
            'via_convoy',
            'illegal',
            'illegal_message',
        )
        read_only_fields = (
            'nation_state',
            'illegal',
            'illegal_message',
        )
