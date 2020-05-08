from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect

from rest_framework import generics, mixins, status, views
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from core import models
from core.models.base import DeadlineFrequency, GameStatus, OrderType
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


class CreateGame(views.APIView):

    permission_classes = [IsAuthenticated]

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


# TODO refactor these into a view set
class BaseOrderView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer

    def set_up(self):
        self.game = get_object_or_404(models.Game, id=self.kwargs['game'])
        if self.request.user not in self.game.participants.all():
            raise ValidationError(
                'User is not a participant in this game.',
                status.HTTP_403_FORBIDDEN
            )
        self.turn = self.game.get_current_turn()
        self.user_nation_state = models.NationState.objects.get(
            turn=self.turn,
            user=self.request.user,
        )

    # NOTE might be cleaner to move these to the `Serializer.validate` method.
    def _validate_request(self):
        if not self.game.status == GameStatus.ACTIVE:
            raise ValidationError(
                'Game is not active.',
                status.HTTP_400_BAD_REQUEST,
            )
        if not self.user_nation_state.orders_remaining:
            raise ValidationError(
                'Nation has no more orders to submit.',
                status.HTTP_400_BAD_REQUEST,
            )
        type = self.request.data.get('type', OrderType.HOLD)
        if type not in self.turn.possible_order_types:
            raise ValidationError(
                'This order type is not possible during this turn.',
                status.HTTP_400_BAD_REQUEST,
            )


class CreateOrderView(BaseOrderView, mixins.CreateModelMixin):

    def post(self, request, *args, **kwargs):
        self.set_up()
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        self._validate_request()
        serializer.save(
            nation=self.user_nation_state.nation,
            turn=self.turn,
        )


class UpdateOrderView(BaseOrderView, mixins.UpdateModelMixin):

    def get_object(self):
        return get_object_or_404(
            models.Order,
            pk=self.kwargs['pk'],
            nation=self.user_nation_state.nation,
        )

    def put(self, request, *args, **kwargs):
        self.set_up()
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        self._validate_request()
        serializer.save(
            nation=self.user_nation_state.nation,
            turn=self.turn,
        )


class FinalizeOrdersView(views.APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
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
        user_nation_state.orders_finalized = True
        user_nation_state.save()
        if turn.ready_to_process:
            turn.process()
        return Response(status=status.HTTP_200_OK)


class UnfinalizeOrdersView(views.APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
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
        if not user_nation_state.orders_finalized:
            return Response(
                {'errors': {'data': ['Orders are not finalized.']}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_nation_state.orders_finalized = False
        user_nation_state.save()
        return Response(status=status.HTTP_200_OK)
