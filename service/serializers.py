from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import exceptions, serializers

from core import models
from core.models.base import GameStatus, OrderType


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

    user = UserSerializer(required=False)
    nation = NationSerializer(required=False)

    class Meta:
        model = models.NationState
        fields = (
            'user',
            'nation',
            'surrendered',
            'orders_finalized'  # TODO should only see this if user
        )

    def update(self, instance, validated_data):
        """
        Set nation's `orders_finalized` field. Finalize if turn is ready.
        """
        instance.orders_finalized = not(instance.orders_finalized)
        instance.save()
        if instance.turn.ready_to_process:
            instance.turn.game.process()
        return instance


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

    participants = UserSerializer(many=True, read_only=True)
    winners = NationStateSerializer(many=True, read_only=True)

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
            'initialized_at',
            'status',
        )
        read_only_fields = (
            'id',
            'participants',
            'winners',
            'created_by',
            'created_at',
            'status',
        )

    def update(self, instance, validated_data):
        """
        Add user as participant.
        """
        user = self.context['request'].user
        instance.participants.add(user)
        if instance.ready_to_initialize:
            instance.initialize()
        return instance


class CreateGameSerializer(serializers.ModelSerializer):

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
        )

    def create(self, validated_data):
        game = models.Game.objects.create(
            created_by=self.context['request'].user,
            **validated_data
        )
        game.participants.add(self.context['request'].user)
        return game


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

    def validate(self, data):
        nation_state = self.context['nation_state']
        data['type'] = data.get('type', OrderType.HOLD)
        data['nation'] = nation_state.nation
        data['turn'] = nation_state.turn
        models.Order.validate(nation_state, data)
        return data


class TurnSerializer(serializers.ModelSerializer):

    territory_states = TerritoryStateSerializer(many=True, source='territorystates')
    piece_states = PieceStateSerializer(many=True, source='piecestates')
    nation_states = NationStateSerializer(many=True, source='nationstates')
    orders = serializers.SerializerMethodField()
    phase = serializers.CharField(source='get_phase_display')
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

    def get_next_turn(self, obj):
        turn = models.Turn.get_next(obj)
        return getattr(turn, 'id', None)

    def get_previous_turn(self, obj):
        turn = models.Turn.get_previous(obj)
        return getattr(turn, 'id', None)

    def get_orders(self, obj):
        # Only get orders for previous turns
        qs = models.Order.objects.filter(turn__current_turn=False, turn=obj)
        serializer = OrderSerializer(instance=qs, many=True)
        return serializer.data


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
