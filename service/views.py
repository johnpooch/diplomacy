from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect

from rest_framework import generics, mixins, status, views
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from core import models
from core.models.base import DeadlineFrequency, GameStatus, OrderType, Phase
from service import serializers
from service.permissions import IsAuthenticated


def error404():
    raise NotFound(detail="Error 404, page not found", code=404)


def get_filter_choices(self, *args):
    return {
        'game_statuses': models.base.GameStatus.CHOICES,
        'nation_choice_modes': models.base.NationChoiceMode.CHOICES,
        'deadlines': models.base.DeadlineFrequency.CHOICES,
        'variants': [(v.id, str(v)) for v in models.Variant.objects.all()],
    }


def get_game_filter_choices():
    return {
        'game_statuses': models.base.GameStatus.CHOICES,
        'nation_choice_modes': models.base.NationChoiceMode.CHOICES,
        'deadlines': models.base.DeadlineFrequency.CHOICES,
        'variants': [(v.id, str(v)) for v in models.Variant.objects.all()],
    }


def filter_games(qs, request):
    search = request.GET.get('search')
    variant = request.GET.get('variant')
    status = request.GET.get('status')
    nation_choice_mode = request.GET.get('nation_choice_mode')
    order_deadline = request.GET.get('order_deadline')
    retreat_deadline = request.GET.get('retreat_deadline')
    build_deadline = request.GET.get('build_deadline')
    num_players = request.GET.get('num_players')
    if search:
        q1 = Q(name__icontains=search)
        q2 = Q(created_by__username__icontains=search)
        qs = qs.filter(q1 | q2).distinct()

    if variant and variant != 'Choose...':
        qs = qs.filter(variant=variant)

    if status and status != 'Choose...':
        qs = qs.filter(status=status)

    if num_players:
        qs = qs.filter(num_players=num_players)

    if nation_choice_mode and nation_choice_mode != 'Choose...':
        qs = qs.filter(nation_choice_mode=nation_choice_mode)

    if order_deadline and order_deadline != 'Choose...':
        qs = qs.filter(order_deadline=order_deadline)

    if retreat_deadline and retreat_deadline != 'Choose...':
        qs = qs.filter(retreat_deadline=retreat_deadline)

    if build_deadline and build_deadline != 'Choose...':
        qs = qs.filter(build_deadline=build_deadline)

    return qs


class GameStateView(views.APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        """
        Returns the state of the game for each turn that has taken place as
        well as the current turn.
        """
        game_id = kwargs['game']
        game = get_object_or_404(models.Game, id=game_id)
        game_state_serializer = serializers.GameStateSerializer(game)
        return Response(game_state_serializer.data)


class GameFilterChoicesView(views.APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        return Response(get_game_filter_choices())


class ListGames(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    queryset = models.Game.objects.all()
    serializer_class = serializers.GameSerializer

    def get(self, request, *args, **kwargs):
        self.queryset = filter_games(self.queryset, self.request)
        status = kwargs.get('status')
        if status:
            if status == 'joinable':
                self.queryset = self.queryset.filter_by_joinable(request.user)
            else:
                self.queryset = self.queryset.filter(status=status)
        response = self.list(request, *args, **kwargs)
        return Response(response.data)


class ListUserGames(ListGames):

    def get(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(participants=request.user)
        return super().get(request, *args, **kwargs)


class CreateGame(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreateGameSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.validate()
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class JoinGame(views.APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        game_id = kwargs['game']
        game = get_object_or_404(models.Game, id=game_id)
        if not game.joinable:
            return Response(
                {'errors': {'status': ['Cannot join game.']}},
                status.HTTP_400_BAD_REQUEST,
            )
        game.participants.add(request.user)
        if game.ready_to_initialize:
            game.initialize()
        return Response(status=status.HTTP_200_OK)


class CreateOrderView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.OrderSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        self.game = get_object_or_404(
            models.Game.objects,
            id=self.kwargs['game'],
            status=GameStatus.ACTIVE,
            participants=self.request.user,
        )
        self.turn = self.game.get_current_turn()
        self.nation_state = get_object_or_404(
            models.NationState.objects,
            turn=self.turn,
            user=self.request.user,
        )
        context['turn'] = self.turn
        context['nation_state'] = self.nation_state
        return context

    def perform_create(self, serializer):
        self._delete_existing(serializer)
        super().perform_create(serializer)

    def _delete_existing(self, serializer):
        models.Order.objects.filter(
            source=serializer.validated_data['source'],
            turn=self.game.get_current_turn(),
            nation=self.nation_state.nation,
        ).delete()


class DestroyOrderView(generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.OrderSerializer

    def get_object(self):
        game_id = self.kwargs['game']
        game = get_object_or_404(
            models.Game,
            id=game_id,
            status=GameStatus.ACTIVE,
            participants=self.request.user,
        )
        user_nation_state = models.NationState.objects.get(
            turn=game.get_current_turn(),
            user=self.request.user,
        )
        return get_object_or_404(
            models.Order,
            pk=self.kwargs['pk'],
            nation=user_nation_state.nation
        )


class FinalizeOrdersView(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.NationStateSerializer

    def get_object(self):
        game_id = self.kwargs['game']
        game = get_object_or_404(
            models.Game,
            id=game_id,
            status=GameStatus.ACTIVE,
            participants=self.request.user,
        )
        return get_object_or_404(
            models.NationState,
            turn=game.get_current_turn(),
            user=self.request.user,
            orders_finalized=(not self.request.data['orders_finalized'])
        )
