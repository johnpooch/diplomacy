from django.db.models import Count, F
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, views, exceptions
from rest_framework.response import Response

from core import models
from core.models.base import GameStatus
from service import serializers
from service.permissions import IsAuthenticated


# NOTE this could possibly be replaced by using options
def get_game_filter_choices():
    return {
        'game_statuses': models.base.GameStatus.CHOICES,
        'nation_choice_modes': models.base.NationChoiceMode.CHOICES,
        'deadlines': models.base.DeadlineFrequency.CHOICES,
        'variants': [(v.id, str(v)) for v in models.Variant.objects.all()],
    }


class GameFilterChoicesView(views.APIView):

    def get(self, request, format=None):
        return Response(get_game_filter_choices())


class BaseMixin:

    game_key = 'game'

    def get_game(self):
        return get_object_or_404(
            models.Game.objects,
            id=self.kwargs[self.game_key],
            status=GameStatus.ACTIVE,
            participants=self.request.user.id,
        )

    def get_user_nation_state(self):
        game = self.get_game()
        return get_object_or_404(
            models.NationState.objects,
            turn=game.get_current_turn(),
            user=self.request.user.id,
        )


class ListGames(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    queryset = models.Game.objects.all()
    serializer_class = serializers.GameSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        'name',
        'created_by__username'
    ]
    filterset_fields = [
        'variant',
        'status',
        'num_players',
        'nation_choice_mode',
        'order_deadline',
        'retreat_deadline',
        'build_deadline',
    ]
    ordering_fields = [
        'created_at',
        'initialized_at'
    ]


class CreateGameView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreateGameSerializer

    def create(self, request, *args, **kwargs):
        defaults = {'variant': 1, 'num_players': 7}
        request.data.update(defaults)
        return super().create(request, *args, **kwargs)


class GameStateView(BaseMixin, generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.GameStateSerializer
    queryset = models.Game.objects.all()
    game_key = 'pk'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # TODO clean this bullsh
        try:
            context['nation_state'] = self.get_user_nation_state()
        except:
            pass
        return context


class JoinGame(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.GameSerializer
    queryset = models.Game.objects \
        .annotate(participant_count=Count('participants')) \
        .filter(participant_count__lt=F('num_players')) \
        .exclude(status=GameStatus.ENDED)

    def check_object_permissions(self, request, obj):
        if request.user in obj.participants.all():
            raise exceptions.PermissionDenied(
                detail='User is already a participant.'
            )


class CreateOrderView(BaseMixin, generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.OrderSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['nation_state'] = self.get_user_nation_state()
        return context

    def perform_create(self, serializer):
        """
        Delete existing order before creating new order.
        """
        models.Order.objects.filter(
            source=serializer.validated_data['source'],
            turn=serializer.validated_data['turn'],
            nation=serializer.validated_data['nation'],
        ).delete()
        super().perform_create(serializer)


class ListOrdersView(BaseMixin, generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.OrderSerializer

    def get_queryset(self):
        user_nation_state = self.get_user_nation_state()
        return models.Order.objects.filter(
            turn=user_nation_state.turn,
            nation=user_nation_state.nation,
        )


class DestroyOrderView(BaseMixin, generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.OrderSerializer
    queryset = models.Order.objects.all()

    def check_object_permissions(self, request, obj):
        user_nation_state = self.get_user_nation_state()
        if obj.nation != user_nation_state.nation:
            raise exceptions.PermissionDenied(
                detail='Order does not belong to this user.'
            )


class FinalizeOrdersView(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.NationStateSerializer
    queryset = models.NationState.objects.filter(
        turn__game__status=GameStatus.ACTIVE
    )

    def check_object_permissions(self, request, obj):
        if request.user != obj.user:
            raise exceptions.PermissionDenied(
                detail='Cannot finalize orders for other nation.'
            )
