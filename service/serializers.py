from django.contrib.auth.models import User
from rest_framework import serializers

from core import models
from core.models.base import OrderType, Phase


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
            'id',
            'piece',
            'territory',
            'named_coast',
            'dislodged',
            'dislodged_by',
            'attacker_territory',
            'must_retreat',
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
            'id',
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
            'id',
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
        fields = (
            'id',
            'territory',
            'controlled_by',
        )


class NationSerializer(serializers.ModelSerializer):

    flag_as_data = serializers.SerializerMethodField()

    class Meta:
        model = models.Nation
        fields = (
            'id',
            'name',
            'flag_as_data',
        )

    def get_flag_as_data(self, nation):
        return nation.flag_as_data


class PublicNationStateSerializer(serializers.ModelSerializer):

    orders_finalized = serializers.SerializerMethodField()
    num_orders_remaining = serializers.SerializerMethodField()

    class Meta:
        model = models.NationState
        fields = (
            'id',
            'user',
            'nation',
            'orders_finalized',
            'num_orders_remaining',
            'surrendered',
            'supply_delta',
            'num_builds',
            'num_disbands',
        )

    def get_orders_finalized(self, nation_state):
        user = self.context['request'].user
        if user.id == nation_state.user.id:
            return nation_state.orders_finalized
        return None

    def get_num_orders_remaining(self, nation_state):
        user = self.context['request'].user
        if user.id == nation_state.user.id:
            return nation_state.num_orders_remaining
        return None

    def update(self, instance, validated_data):
        """
        Set nation's `orders_finalized` field. Process game if turn is ready.
        """
        instance.orders_finalized = not(instance.orders_finalized)
        instance.save()
        if instance.turn.ready_to_process:
            instance.turn.game.process()
        return instance


class PrivateNationStateSerializer(serializers.ModelSerializer):

    build_territories = serializers.SerializerMethodField()

    class Meta:
        model = models.NationState
        fields = (
            'id',
            'user',
            'nation',
            'surrendered',
            'orders_finalized',
            'num_orders_remaining',
            'supply_delta',
            'build_territories',
            'num_builds',
            'num_disbands',
        )

    def get_build_territories(self, nation_state):
        """
        Get a list of territory ids for each territory in which the user can
        build.
        """
        if nation_state.turn.phase != Phase.BUILD:
            return None
        return [ts.territory.id for ts
                in nation_state.unoccupied_controlled_home_supply_centers]


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


class CreateGameSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Game
        fields = (
            'id',
            'slug',
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


class OrderTurnGameSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Game
        fields = (
            'id',
            'slug',
        )


class OrderTurnSerializer(serializers.ModelSerializer):

    game = OrderTurnGameSerializer(read_only=True)

    class Meta:
        model = models.Turn
        fields = (
            'id',
            'game',
        )


class OrderSerializer(serializers.ModelSerializer):

    turn = OrderTurnSerializer(read_only=True)

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
            'turn',
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
    nation_states = PublicNationStateSerializer(many=True, source='nationstates')
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
        qs = models.Order.objects.filter(
            turn__current_turn=False,
            turn=obj
        )
        serializer = OrderSerializer(instance=qs, many=True)
        return serializer.data


class ListNationStatesSerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = models.NationState
        fields = (
            'id',
            'user',
            'nation',
        )


class ListTurnSerializer(serializers.ModelSerializer):

    phase = serializers.CharField(source='get_phase_display')
    nation_states = ListNationStatesSerializer(many=True, source='nationstates')

    class Meta:
        model = models.Turn
        fields = (
            'id',
            'year',
            'season',
            'phase',
            'nation_states',
        )


class ListVariantsSerializer(serializers.ModelSerializer):

    territories = TerritorySerializer(many=True)
    nations = NationSerializer(many=True)
    map_data = MapDataSerializer(many=True)

    class Meta:
        model = models.Variant
        fields = (
            'id',
            'name',
            'territories',
            'nations',
            'map_data',
        )


class LightVariantsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Variant
        fields = (
            'id',
            'name',
        )


class ListGamesSerializer(serializers.ModelSerializer):

    current_turn = serializers.SerializerMethodField()
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = models.Game
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'variant',
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
            'initialized_at',
            'status',
            'current_turn',
        )

    def get_current_turn(self, game):
        try:
            current_turn = game.get_current_turn()
            return ListTurnSerializer(current_turn).data
        except models.Turn.DoesNotExist:
            return None


class GameSerializer(serializers.ModelSerializer):

    participants = UserSerializer(many=True, read_only=True)
    current_turn = serializers.SerializerMethodField()
    winners = PublicNationStateSerializer(many=True, read_only=True)
    pieces = PieceSerializer(many=True)

    class Meta:
        model = models.Game
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'variant',
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
            'current_turn',
            'pieces',
        )
        read_only_fields = (
            'id',
            'participants',
            'winners',
            'created_by',
            'created_at',
            'status',
        )

    def get_current_turn(self, game):
        try:
            current_turn = game.get_current_turn()
            return TurnSerializer(current_turn).data
        except models.Turn.DoesNotExist:
            return None

    def update(self, instance, validated_data):
        """
        Add user as participant.
        """
        user = self.context['request'].user
        if user in instance.participants.all():
            instance.participants.remove(user)
            return instance
        instance.participants.add(user)
        if instance.ready_to_initialize:
            instance.initialize()
        return instance


class GameStateSerializer(serializers.ModelSerializer):

    turns = TurnSerializer(many=True)
    pieces = PieceSerializer(many=True)

    class Meta:
        model = models.Game
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'turns',
            'variant',
            'pieces',
            'status',
        )


class NationFlagSerializer(serializers.ModelSerializer):

    flag_as_data = serializers.SerializerMethodField()

    class Meta:
        model = models.Nation
        fields = (
            'id',
            'flag_as_data',
        )

    def get_flag_as_data(self, nation):
        return nation.flag_as_data
