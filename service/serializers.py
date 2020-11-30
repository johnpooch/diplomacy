from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from core import models
from core.models.base import DrawStatus, OrderType, Phase, SurrenderStatus

from . import validators as custom_validators


def get_nation_state_from_draw(data):
    return models.NationState.objects.get(
        turn=data.get('draw').turn,
        nation=data.get('proposed_by')
    )


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


class SurrenderSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Surrender
        fields = (
            'id',
            'nation_state',
            'user',
            'status',
            'replaced_by',
            'resolved_at',
            'created_at',
        )

    def create(self, validated_data):
        nation_state = validated_data['nation_state']
        return models.Surrender.objects.create(
            user=self.context['request'].user,
            nation_state=nation_state,
        )

    def update(self, surrender, validated_data):
        surrender.status = SurrenderStatus.CANCELED
        surrender.resolved_at = timezone.now()
        surrender.save()
        return surrender


class CreateDrawSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Draw
        fields = (
            'id',
            'proposed_by',
            'proposed_by_user',
            'proposed_at',
            'nations',
            'status',
            'turn',
            'resolved_at',
        )
        validators = [
            custom_validators.DistinctNationsValidator(),
            custom_validators.NotSurrenderingValidator(),
            custom_validators.NationsInVariantValidator(),
            custom_validators.NationsActiveValidator(),
            custom_validators.OneProposedDrawValidator(),
            custom_validators.ProposedDrawStrengthValidator(),
            custom_validators.DrawNationCountValidator(),
        ]
        extra_kwargs = {
            'turn': {
                'validators': [custom_validators.CurrentTurnValidator()]
            },
        }


class CancelDrawSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Draw
        fields = (
            'id',
            'proposed_by',
            'proposed_by_user',
            'proposed_at',
            'nations',
            'status',
            'turn',
            'resolved_at',
        )

    def update(self, draw, validated_data):
        draw.status = DrawStatus.CANCELED
        draw.save()
        return draw


class DrawResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DrawResponse
        fields = (
            'id',
            'draw',
            'nation',
            'user',
            'response',
            'created_at',
        )
        validators = [
            custom_validators.NotSurrenderingValidator(),
            UniqueTogetherValidator(
                queryset=models.DrawResponse.objects.all(),
                fields=['nation', 'draw']
            )
        ]
        extra_kwargs = {
            'draw': {
                'validators': [custom_validators.DrawProposedValidator()]
            },
        }


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


class TerritorySerializer(serializers.ModelSerializer):

    named_coasts = NamedCoastSerializer(many=True)

    class Meta:
        model = models.Territory
        fields = (
            'id',
            'uid',
            'name',
            'type',
            'supply_center',
            'named_coasts',
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

    class Meta:
        model = models.Nation
        fields = (
            'id',
            'name',
        )


class PublicNationStateSerializer(serializers.ModelSerializer):

    orders_finalized = serializers.SerializerMethodField()
    num_orders_remaining = serializers.SerializerMethodField()
    num_supply_centers = serializers.SerializerMethodField()
    surrenders = SurrenderSerializer(many=True, read_only=True)

    class Meta:
        model = models.NationState
        fields = (
            'id',
            'user',
            'nation',
            'orders_finalized',
            'num_orders_remaining',
            'num_supply_centers',
            'supply_delta',
            'num_builds',
            'num_disbands',
            'surrenders',
        )
        read_only_fields = (
            'nation',
        )

    def get_num_supply_centers(self, nation_state):
        return nation_state.supply_centers.count()

    def get_orders_finalized(self, nation_state):
        request = self.context.get('request')
        if request:
            user = request.user
            if user.id == nation_state.user.id:
                return nation_state.orders_finalized
        return None

    def get_num_orders_remaining(self, nation_state):
        request = self.context.get('request')
        if request:
            user = request.user
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


class ToggleFinalizeOrdersSerializer(PublicNationStateSerializer):

    def update(self, instance, validated_data):
        """
        Set nation's `orders_finalized` field. Process game if turn is ready.
        """
        instance.orders_finalized = not(instance.orders_finalized)
        instance.save()
        if instance.turn.ready_to_process:
            instance.turn.game.process()
        return instance


class ToggleSurrenderSerializer(PublicNationStateSerializer):

    def update(self, nation_state, validated_data):
        nation_state.turn.toggle_surrender(nation_state.user)
        return nation_state


class PrivateNationStateSerializer(serializers.ModelSerializer):

    build_territories = serializers.SerializerMethodField()
    surrenders = SurrenderSerializer(many=True)

    class Meta:
        model = models.NationState
        fields = (
            'id',
            'user',
            'nation',
            'orders_finalized',
            'num_orders_remaining',
            'supply_delta',
            'build_territories',
            'num_builds',
            'num_disbands',
            'surrenders',
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

    class Meta:
        model = models.Variant
        fields = (
            'id',
            'name',
            'territories',
            'nations',
            'num_supply_centers_to_win',
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


class DrawSerializer(serializers.ModelSerializer):

    draw_responses = DrawResponseSerializer(
        many=True,
        source='drawresponse_set'
    )

    class Meta:
        model = models.Draw
        fields = (
            'id',
            'turn',
            'nations',
            'proposed_by',
            'proposed_by_user',
            'status',
            'proposed_at',
            'resolved_at',
            'draw_responses'
        )


class TurnSerializer(serializers.ModelSerializer):

    territory_states = TerritoryStateSerializer(many=True, source='territorystates')
    piece_states = PieceStateSerializer(many=True, source='piecestates')
    nation_states = PublicNationStateSerializer(many=True, source='nationstates')
    orders = serializers.SerializerMethodField()
    phase = serializers.CharField(source='get_phase_display')
    next_turn = serializers.SerializerMethodField()
    previous_turn = serializers.SerializerMethodField()
    draws = DrawSerializer(many=True)

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
            'draws',
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
    surrenders = SurrenderSerializer(many=True)

    class Meta:
        model = models.NationState
        fields = (
            'id',
            'user',
            'nation',
            'surrenders',
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

    class Meta:
        model = models.Variant
        fields = (
            'id',
            'name',
            'territories',
            'nations',
            'num_supply_centers_to_win',
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

    current_turn = serializers.SerializerMethodField()
    participants = UserSerializer(many=True, read_only=True)
    pieces = PieceSerializer(many=True)
    winners = PublicNationStateSerializer(many=True, read_only=True)

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

    participants = UserSerializer(many=True, read_only=True)
    pieces = PieceSerializer(many=True)
    turns = TurnSerializer(many=True)

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
            'participants',
        )
