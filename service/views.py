from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework import generics, mixins, status, views
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from core import models
from core.models.base import DeadlineFrequency, GameStatus, NationChoiceMode, \
    OrderType
from service import forms, serializers
from service.permissions import IsAuthenticated, IsParticipant
from service.utils import form_to_data


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


def filter_games(request):
    qs = models.Game.objects.all()

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

    def get_queryset(self):
        return filter_games(self.request)

    def get(self, request, *args, **kwargs):
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


class CreateGame(views.APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        form = forms.CreateGameForm()
        data = form_to_data(form)
        return Response(data)

    def post(self, request):
        request.data['variant_id'] = 1
        request.data['num_players'] = 7
        serializer = serializers.GameSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status.HTTP_400_BAD_REQUEST,
            )
        game = serializer.save(created_by=request.user)
        game.participants.add(request.user)
        return redirect('user-games')


class JoinGame(views.APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        game_id = kwargs['game']
        game = get_object_or_404(models.Game, id=game_id)
        join_game_form = forms.JoinGameForm(game, data=request.data)
        if not game.joinable:
            return Response(
                {'errors': {'status': ['Cannot join game.']}},
                status.HTTP_400_BAD_REQUEST,
            )
        if join_game_form.is_valid():
            game.participants.add(request.user)
            return redirect('user-games')
        return Response(
            {'errors': join_game_form.errors},
            status.HTTP_400_BAD_REQUEST,
        )


class OrderView(mixins.CreateModelMixin, generics.GenericAPIView):

    permission_classes = [IsAuthenticated]

    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer

    def post(self, request, *args, **kwargs):
        game_id = kwargs['game']
        game = get_object_or_404(models.Game, id=game_id)

        if request.user not in game.participants.all():
            return Response(
                {'errors': {
                    'data': ['User is not a participant in this game.']
                }},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not game.status == GameStatus.ACTIVE:
            return Response(
                {'errors': {'data': ['Game is not active.']}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        turn = game.get_current_turn()
        user_nation_state = models.NationState.objects.get(
            turn=turn,
            user=request.user,
        )
        if not user_nation_state.orders_remaining:
            return Response(
                {'errors': {'data': ['Nation has no more orders to submit.']}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        kwargs['game'] = game
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        game = kwargs['game']
        turn = game.get_current_turn()
        order_type = request.data.get('type', OrderType.HOLD)
        if order_type not in turn.possible_order_types:
            return Response(
                {'errors': {'data': 'This order type is not possible during this turn.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_nation_state = models.NationState.objects.get(
            turn=turn,
            user=request.user,
        )
        serializer.save(nation=user_nation_state.nation, turn=turn)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
