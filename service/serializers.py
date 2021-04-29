from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from core import models
from core.game import process_turn
from core.models.base import DrawStatus, OrderType, SurrenderStatus

from . import validators as custom_validators


def get_nation_state_from_draw(data):
    return models.NationState.objects.get(turn=data.get('draw').turn,
                                          nation=data.get('proposed_by'))


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'id')


class PieceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Piece
        fields = (
            'id',
            'nation',
            'turn_created',
            'type',
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
            UniqueTogetherValidator(queryset=models.DrawResponse.objects.all(),
                                    fields=['nation', 'draw'])
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
            'turn',
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
            'name',
            'named_coasts',
            'nationality',
            'neighbours',
            'supply_center',
            'type',
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
            'variant',
        )


class PublicNationStateSerializer(serializers.ModelSerializer):

    surrenders = SurrenderSerializer(many=True, read_only=True)

    class Meta:
        model = models.NationState
        fields = (
            'id',
            'user',
            'nation',
            'surrenders',
        )
        read_only_fields = (
            'nation',
        )

    def update(self, instance, validated_data):
        """
        Set nation's `orders_finalized` field. Process game if turn is ready.
        """
        instance.orders_finalized = not (instance.orders_finalized)
        instance.save()
        if instance.turn.ready_to_process:
            instance.turn.game.process()
        return instance


class ToggleFinalizeOrdersSerializer(PublicNationStateSerializer):
    class Meta:
        model = models.NationState
        fields = (
            'id',
            'orders_finalized',
        )

    def update(self, instance, validated_data):
        """
        Set nation's `orders_finalized` field. Process game if turn is ready.
        """
        instance.orders_finalized = not (instance.orders_finalized)
        instance.save()

        if instance.turn.ready_to_process:
            process_turn(instance.turn)

        return instance


class ToggleSurrenderSerializer(PublicNationStateSerializer):
    def update(self, nation_state, validated_data):
        nation_state.turn.toggle_surrender(nation_state.user)
        return nation_state


class VariantSerializer(serializers.ModelSerializer):

    territories = TerritorySerializer(many=True)
    nations = NationSerializer(many=True)

    class Meta:
        model = models.Variant
        fields = (
            'id',
            'identifier',
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
            created_by=self.context['request'].user, **validated_data)
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
            'outcome',
            'illegal',
            'illegal_code',
            'illegal_verbose',
        )
        read_only_fields = (
            'nation',
            'turn',
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
        source='drawresponse_set',
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

    territory_states = TerritoryStateSerializer(
        many=True,
        source='territorystates'
    )
    piece_states = PieceStateSerializer(
        many=True,
        source='piecestates'
    )
    nation_states = PublicNationStateSerializer(
        many=True,
        source='nationstates'
    )
    orders = OrderSerializer(
        many=True,
        source='public_orders'
    )
    phase_display = serializers.CharField(
        source='get_phase_display'
    )
    season_display = serializers.CharField(
        source='get_season_display'
    )
    draws = DrawSerializer(many=True)
    turn_end = serializers.SerializerMethodField()
    next_turn = serializers.SerializerMethodField()
    previous_turn = serializers.SerializerMethodField()

    class Meta:
        model = models.Turn
        fields = (
            'id',
            'game',
            'current_turn',
            'next_turn',
            'previous_turn',
            'year',
            'season',
            'season_display',
            'phase',
            'phase_display',
            'territory_states',
            'piece_states',
            'nation_states',
            'orders',
            'draws',
            'turn_end',
        )

    def get_turn_end(self, turn):
        if turn.turn_end:
            return turn.turn_end.datetime
        return None

    def get_next_turn(self, obj):
        turn = models.Turn.get_next(obj)
        return getattr(turn, 'id', None)

    def get_previous_turn(self, obj):
        turn = models.Turn.get_previous(obj)
        return getattr(turn, 'id', None)


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

    phase_display = serializers.CharField(source='get_phase_display')
    season_display = serializers.CharField(source='get_season_display')
    nation_states = ListNationStatesSerializer(many=True,
                                               source='nationstates')
    turn_end = serializers.SerializerMethodField()

    class Meta:
        model = models.Turn
        fields = (
            'id',
            'year',
            'season',
            'season_display',
            'phase',
            'phase_display',
            'nation_states',
            'turn_end',
        )

    def get_turn_end(self, turn):
        if turn.turn_end:
            return turn.turn_end.datetime
        return None


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
        current_turn = game.get_current_turn()
        if current_turn:
            return ListTurnSerializer(current_turn).data
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


class NationStateOrdersFinalizedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.NationState
        fields = (
            'id',
            'orders_finalized',
        )


class NationStateOrdersStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.NationState
        fields = (
            'id',
            'num_orders',
            'num_supply_centers',
            'supply_delta',
            'num_builds',
            'num_disbands',
        )
