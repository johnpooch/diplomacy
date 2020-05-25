from django.contrib.auth.models import User
from rest_framework import serializers

from core import models


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'id')


class PieceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Piece
        fields = (
            'id',
            'type',
            'nation',
        )


class PieceStateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PieceState
        fields = (
            'piece',
            'territory',
            'named_coast',
            'dislodged',
            'dislodged_by',
            'attacker_territory',
        )


class NamedCoastSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.NamedCoast
        fields = (
            'id',
            'parent',
            'name',
        )


class NamedCoastMapDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.NamedCoastMapData
        fields = (
            'pk',
            'named_coast',
            'name',
            'abbreviation',
            'text_x',
            'text_y',
            'piece_x',
            'piece_y',
            'dislodged_piece_x',
            'dislodged_piece_y',
        )


class TerritorySerializer(serializers.ModelSerializer):

    named_coasts = NamedCoastSerializer(many=True)

    class Meta:
        model = models.Territory
        fields = (
            'id',
            'name',
            'type',
            'supply_center',
            'named_coasts',
        )


class TerritoryMapDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TerritoryMapData
        fields = (
            'pk',
            'territory',
            'type',
            'name',
            'abbreviation',
            'path',
            'text_x',
            'text_y',
            'piece_x',
            'piece_y',
            'dislodged_piece_x',
            'dislodged_piece_y',
            'supply_center_x',
            'supply_center_y',
        )


class MapDataSerializer(serializers.ModelSerializer):

    territory_data = TerritoryMapDataSerializer(many=True)
    named_coast_data = NamedCoastMapDataSerializer(many=True)

    class Meta:
        model = models.MapData
        fields = (
            'id',
            'identifier',
            'width',
            'height',
            'territory_data',
            'named_coast_data',
        )


class TerritoryStateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TerritoryState
        fields = ('territory', 'controlled_by',)


class NationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Nation
        fields = ('id', 'name', )


class NationStateSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    nation = NationSerializer()

    class Meta:
        model = models.NationState
        fields = (
            'user',
            'nation',
            'surrendered',
            'orders_finalized'  # TODO should only see this if user
        )


class VariantSerializer(serializers.ModelSerializer):

    territories = TerritorySerializer(many=True)
    nations = NationSerializer(many=True)
    map_data = MapDataSerializer(many=True)

    class Meta:
        model = models.Variant
        fields = (
            'id',
            'name',
            'territories',
            'map_data',
            'nations',
        )


class GameSerializer(serializers.ModelSerializer):

    participants = UserSerializer(many=True)
    winners = NationStateSerializer(many=True)

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
            'winners',
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
    piece_states = PieceStateSerializer(many=True, source='piecestates')
    nation_states = NationStateSerializer(many=True, source='nationstates')
    orders = OrderSerializer(many=True)
    next_turn = serializers.SerializerMethodField()
    previous_turn = serializers.SerializerMethodField()

    class Meta:
        model = models.Turn
        fields = (
            'id',
            'next_turn',
            'previous_turn',
            'current_turn',
            'year',
            'season',
            'phase',
            'territory_states',
            'piece_states',
            'nation_states',
            'orders',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            if self.instance.current_turn:
                self.fields.pop('orders')

    def get_next_turn(self, obj):
        turn = models.Turn.get_next(obj)
        return getattr(turn, 'id', None)

    def get_previous_turn(self, obj):
        turn = models.Turn.get_previous(obj)
        return getattr(turn, 'id', None)


class GameStateSerializer(serializers.ModelSerializer):

    turns = TurnSerializer(many=True)
    variant = VariantSerializer()
    pieces = PieceSerializer(many=True)
    participants = UserSerializer(many=True)

    class Meta:
        model = models.Game
        fields = (
            'id',
            'name',
            'turns',
            'variant',
            'pieces',
            'status',
            'participants',
            'winners',
        )
