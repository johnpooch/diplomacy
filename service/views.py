from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, generics, status, views
from rest_framework.response import Response

from core import models
from core.models.base import DrawStatus, GameStatus, SurrenderStatus
from service import serializers
from service.permissions import IsAuthenticated
from service.mixins import CamelCase


# NOTE this could possibly be replaced by using options
def get_game_filter_choices():
    return {
        'gameStatuses': models.base.GameStatus.CHOICES,
        'nationChoiceModes': models.base.NationChoiceMode.CHOICES,
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


class ListGames(CamelCase, generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    queryset = (
        models.Game.objects.all()
        .select_related('variant')
        .prefetch_related(
            'participants',
            'turns__nationstates__user',
            'turns__nationstates__surrenders',
            'turns__turnend',
        )
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


class ListVariants(CamelCase, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = (
        models.Variant.objects.all()
        .prefetch_related(
            'territories__named_coasts',
            'nations',
        )
    )
    serializer_class = serializers.ListVariantsSerializer


class CreateGameView(CamelCase, generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreateGameSerializer

    def create(self, request, *args, **kwargs):
        defaults = {'variant': 1, 'num_players': 7}
        request.data.update(defaults)
        return super().create(request, *args, **kwargs)


class GameStateView(CamelCase, BaseMixin, generics.RetrieveAPIView):

    previous_orders = models.Order.objects.filter(
        turn__current_turn=False,
    )
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.GameStateSerializer
    queryset = (
        models.Game.objects.all()
        .prefetch_related(
            'participants',
            'pieces',
            'turns__nationstates__user',
            'turns__nationstates__surrenders',
            'turns__piecestates',
            'turns__territorystates__territory',
            'turns__turnend',
            Prefetch(
                'turns__orders',
                queryset=previous_orders,
                to_attr='previous_orders'
            ),
        )
    )
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


class CreateOrderView(CamelCase, BaseMixin, generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.OrderSerializer
    queryset = models.Order.objects.all()

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


class DestroyOrderView(CamelCase, BaseMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.OrderSerializer

    def check_object_permissions(self, request, order):
        user_nation_state = self.get_user_nation_state()
        # TODO check if you can delete another order from a different game
        if order.nation != user_nation_state.nation:
            raise exceptions.PermissionDenied(
                detail='Order does not belong to this user.'
            )


class ListOrdersView(CamelCase, BaseMixin, generics.ListAPIView):

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


class ToggleFinalizeOrdersView(CamelCase, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ToggleFinalizeOrdersSerializer
    queryset = models.NationState.objects.filter(
        turn__game__status=GameStatus.ACTIVE
    )

    def check_object_permissions(self, request, obj):
        if request.user != obj.user:
            raise exceptions.PermissionDenied(
                detail='Cannot finalize orders for other nation.'
            )


class ToggleSurrenderView(
        CamelCase, generics.UpdateAPIView, generics.CreateAPIView
):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.SurrenderSerializer
    queryset = models.Surrender.objects.filter(
        nation_state__turn__current_turn=True,
        nation_state__turn__game__status=GameStatus.ACTIVE,
        status=SurrenderStatus.PENDING
    )

    def create(self, request, *args, **kwargs):
        turn = models.Turn.objects.get(id=kwargs['turn'])
        if not turn.current_turn:
            raise exceptions.PermissionDenied(
                'Cannot surrender on inactive turn.'
            )
        if not turn.game.status == GameStatus.ACTIVE:
            raise exceptions.PermissionDenied(
                'Cannot surrender on inactive game.'
            )
        user_nation_state = get_object_or_404(
            models.NationState,
            turn=turn,
            user=request.user.id,
        )
        defaults = {
            'user': request.user.id,
            'nation_state': user_nation_state.id
        }
        request.data.update(defaults)
        return super().create(request, *args, **kwargs)

    def check_object_permissions(self, request, surrender):
        if request.user != surrender.user:
            raise exceptions.PermissionDenied(
                detail='Cannot surrender if not controlling nation.'
            )


class ProposeDraw(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreateDrawSerializer
    queryset = models.Draw.objects.filter(
        turn__current_turn=True,
        turn__game__status=GameStatus.ACTIVE,
        status=DrawStatus.PROPOSED
    )

    def get_user_nation_state(self):
        turn = self.kwargs['turn']
        return get_object_or_404(
            models.NationState.objects,
            turn=turn,
            user=self.request.user.id,
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_nation_state'] = self.get_user_nation_state()
        return context

    def create(self, request, *args, **kwargs):
        turn = models.Turn.objects.get(id=kwargs['turn'])
        nation = models.Nation.objects.get(
            nationstate__user=request.user,
            nationstate__turn=turn,
        )
        defaults = {
            'turn': turn.id,
            'proposed_by': nation.id,
            'proposed_by_user': request.user.id,
        }
        request.data.update(defaults)
        return super().create(request, *args, **kwargs)


class CancelDraw(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CancelDrawSerializer
    queryset = models.Draw.objects.filter(
        turn__current_turn=True,
        turn__game__status=GameStatus.ACTIVE,
        status=DrawStatus.PROPOSED
    )

    def check_object_permissions(self, request, draw):
        turn = self.kwargs['turn']
        nation = models.NationState.objects.get(
            user=request.user,
            turn=turn
        ).nation
        if nation != draw.proposed_by:
            raise exceptions.PermissionDenied(
                detail='Cannot cancel another nation\'s draw proposal.'
            )


class DrawResponse(CamelCase, generics.CreateAPIView, generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.DrawResponseSerializer
    queryset = models.DrawResponse.objects.filter(
        draw__turn__current_turn=True,
        draw__turn__game__status=GameStatus.ACTIVE,
        draw__status=DrawStatus.PROPOSED,
    )

    def get_user_nation_state(self):
        draw = models.Draw.objects.get(id=self.kwargs['draw'])
        return models.NationState.objects.filter(
            turn=draw.turn,
            user=self.request.user.id,
        ).first()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_nation_state'] = self.get_user_nation_state()
        return context

    def create(self, request, *args, **kwargs):
        draw = models.Draw.objects.get(id=kwargs['draw'])
        nation = models.Nation.objects.get(
            nationstate__user=request.user,
            nationstate__turn=draw.turn,
        )
        defaults = {
            'draw': draw.id,
            'nation': nation.id,
            'user': request.user.id,
        }
        request.data.update(defaults)
        return super().create(request, *args, **kwargs)

    def check_object_permissions(self, request, draw_response):
        draw = self.kwargs['draw']
        turn = models.Turn.objects.get(draws=draw)
        nation = models.NationState.objects.get(
            user=request.user,
            turn=turn
        ).nation
        if nation != draw_response.nation:
            raise exceptions.PermissionDenied(
                detail='Cannot cancel another nation\'s draw response.'
            )
