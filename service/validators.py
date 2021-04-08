from rest_framework import serializers

from core import models
from core.models.nation import get_combined_strength
from core.models.base import DrawStatus, GameStatus, SurrenderStatus


class NotSurrenderingValidator:

    requires_context = True
    message = 'Not possible if surrendering.'

    def __call__(self, data, serializer):
        nation_state = serializer.context.get('user_nation_state')
        if models.Surrender.objects.filter(
            user=nation_state.user,
            nation_state=nation_state,
            status=SurrenderStatus.PENDING,
        ).exists():
            raise serializers.ValidationError(self.message)


class CurrentTurnValidator:

    message = 'Not possible on inactive turn.'

    def __call__(self, turn):
        if not turn.current_turn or turn.game.status != GameStatus.ACTIVE:
            raise serializers.ValidationError(self.message)


class NationsInVariantValidator:

    message = 'All nations must belong to the current variant.'

    def __call__(self, data):
        nations = data['nations']
        variant = data['turn'].game.variant
        if not all([n.variant == variant for n in nations]):
            raise serializers.ValidationError(self.message)


class NationsActiveValidator:

    message = 'All nations must be active (has user and not surrendering).'

    def __call__(self, data):
        nations = data['nations']
        nation = data['proposed_by']
        turn = data['turn']
        nation_states = models.NationState.objects.filter(
            turn=turn,
            nation__in=[*nations, nation],
        )
        if any([ns.civil_disorder for ns in nation_states]):
            raise serializers.ValidationError(self.message)


class OneProposedDrawValidator:

    message = 'Cannot propose multiple draws.'

    def __call__(self, data):
        turn = data['turn']
        nation = data['proposed_by']
        if models.Draw.objects.filter(
            proposed_by=nation,
            turn=turn,
            status=DrawStatus.PROPOSED,
        ).exists():
            raise serializers.ValidationError(self.message)


class ProposedDrawStrengthValidator:

    message = 'Proposed draw does not have enough strength: %s.'

    def __call__(self, data):
        turn = data['turn']
        variant = turn.game.variant
        required_strength = variant.num_supply_centers_to_win
        nation = data['proposed_by']
        nations = data['nations']
        nation_states = models.NationState.objects.filter(
            turn=turn,
            nation__in=[*nations, nation],
        ).distinct()
        if get_combined_strength(nation_states) < required_strength:
            raise serializers.ValidationError(self.message % required_strength)


class DrawNationCountValidator:

    message = 'Proposed draw cannot include more than %s nations.'

    def __call__(self, data):
        turn = data['turn']
        variant = turn.game.variant
        max_nations = variant.max_nations_in_draw
        nation = data['proposed_by']
        nations = data['nations']
        if len([*nations, nation]) > max_nations:
            raise serializers.ValidationError(self.message % max_nations)


class DistinctNationsValidator:

    message = 'Nations must not include duplicates'

    def __call__(self, data):
        nations = data['nations']
        if len(nations) != len(list(set([n.id for n in nations]))):
            raise serializers.ValidationError(self.message)


class DrawProposedValidator:

    message = 'Not possible if draw is not proposed.'

    def __call__(self, draw):
        if not draw.status == DrawStatus.PROPOSED:
            raise serializers.ValidationError(self.message)
