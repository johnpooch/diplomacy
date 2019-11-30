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
        fields = ('territory', 'controlled_by')


class NationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Nation
        fields = ('name', )


class NationStateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.NationState
        fields = ('nation', 'surrendered', 'surrendered_turn')


class VariantSerializer(serializers.ModelSerializer):

    territories = TerritorySerializer(many=True)
    nations = NationSerializer(many=True)

    class Meta:
        model = models.Variant
        fields = (
            'id',
            'name',
            'territories',
            'nations',
        )


class GameSerializer(serializers.ModelSerializer):

    variant = VariantSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(
        source='variant',
        queryset=models.Variant.objects.all(),
    )

    class Meta:
        model = models.Game
        fields = (
            'id',
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
            'id',
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
            'nation',
            'source',
            'target',
            'target_coast',
            'aux',
            'piece_type',
            'via_convoy',
        )
        read_only_fields = (
            'nation',
        )


class TurnSerializer(serializers.ModelSerializer):

    territory_states = TerritoryStateSerializer(many=True, source='territorystates')
    nation_states = NationStateSerializer(many=True, source='nationstates')
    pieces = PieceSerializer(many=True)
    orders = OrderSerializer(many=True)

    class Meta:
        model = models.Turn
        fields = (
            'id',
            'year',
            'season',
            'phase',
            'territory_states',
            'pieces',
            'nation_states',
            'orders',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            if self.instance.current_turn:
                self.fields.pop('orders')


class GameStateSerializer(serializers.ModelSerializer):

    turns = TurnSerializer(many=True)
    variant = VariantSerializer()

    class Meta:
        model = models.Game
        fields = (
            'id',
            'name',
            'turns',
            'variant',
        )
