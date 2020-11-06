from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, generics, status, views
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

    def get_game(self):
        return get_object_or_404(
            models.Game.objects,
            slug=self.kwargs['slug'],
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
    queryset = (
        models.Game.objects.all()
        .select_related('variant')
        .order_by('-created_at')
    )
    serializer_class = serializers.ListGamesSerializer
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


class ListVariants(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = models.Variant.objects.all()
    serializer_class = serializers.ListVariantsSerializer


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
    lookup_field = 'slug'


class ToggleJoinGame(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.GameSerializer
    queryset = models.Game.objects.all()
    lookup_field = 'slug'

    def check_object_permissions(self, request, obj):
        if request.user not in obj.participants.all():
            if obj.participants.count() >= obj.num_players:
                raise exceptions.PermissionDenied(
                    detail='Game is already full.'
                )
            if obj.status != GameStatus.PENDING:
                raise exceptions.PermissionDenied(
                    detail='Game is not pending.'
                )


class CreateOrderView(BaseMixin, generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.OrderSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['nation_state'] = self.get_user_nation_state()
        return context

    def delete_old_order(self, serializer):
        """
        Delete existing order before creating new order. Return existing order
        ID so client can update store correctly.
        """
        try:
            old_order = models.Order.objects.get(
                source=serializer.validated_data['source'],
                turn=serializer.validated_data['turn'],
                nation=serializer.validated_data['nation'],
            )
            old_order_id = old_order.id
            old_order.delete()
            return old_order_id
        except models.Order.DoesNotExist:
            return None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_order_id = self.delete_old_order(serializer)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_data = {**serializer.data, 'old_order': old_order_id}
        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class ListOrdersView(BaseMixin, generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.OrderSerializer

    def get_queryset(self):
        turn = get_object_or_404(
            models.Turn,
            id=self.kwargs['pk'],
        )
        user_nation_state = models.NationState.objects.filter(
            turn=turn,
            user=self.request.user.id,
        ).first()
        if not user_nation_state:
            return models.Order.objects.none()
        return models.Order.objects.filter(
            turn=turn,
            nation=user_nation_state.nation,
        )


class ToggleFinalizeOrdersView(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PublicNationStateSerializer
    queryset = models.NationState.objects.filter(
        turn__game__status=GameStatus.ACTIVE
    )

    def check_object_permissions(self, request, obj):
        if request.user != obj.user:
            raise exceptions.PermissionDenied(
                detail='Cannot finalize orders for other nation.'
            )
