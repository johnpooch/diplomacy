from django.shortcuts import get_object_or_404, redirect

from rest_framework import generics, mixins, status, views
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from core import models
from core.models.base import GameStatus
from service import serializers
from service import forms
from service.permissions import IsAuthenticated, IsParticipant

from rest_framework.exceptions import NotFound


def error404():
    raise NotFound(detail="Error 404, page not found", code=404)


# TODO all views need to be refactored using django rest mixins etc.

# TODO stub out all the views and urls before writing any more code. Also
# these views using TDD.

# TODO ignore permissions at first. Add them in after the basic views are done.

"""
Users
* Register
* Log in
* Log out
* User status (e.g. unread messages, pending orders)

* Finalize orders

Messages and announcements
* Create message
* Get messages
"""


class GameStateView(views.APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        """
        Returns the state of the game for each turn that has taken place as
        well as the current turn.
        """
        game_id = kwargs['game']
        states = [GameStatus.ENDED, GameStatus.ACTIVE]
        game = get_object_or_404(models.Game, id=game_id, status__in=states)

        game_state_serializer = serializers.GameStateSerializer(game)

        return Response(game_state_serializer.data)


class ListGames(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    queryset = models.Game.objects.all()
    serializer_class = serializers.GameSerializer

    def get(self, request, *args, **kwargs):
        status = kwargs.get('status')

        if status:
            if status == 'joinable':
                self.queryset = self.queryset.filter_by_joinable(request.user)
            else:
                self.queryset = self.queryset.filter(status=status)

        return self.list(request, *args, **kwargs)


class ListUserGames(ListGames):

    def get(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(participants=request.user)
        return super().get(request, *args, **kwargs)


class CreateGame(views.APIView):

    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'create_game.html'

    def get(self, request, *args, **kwargs):
        serializer = serializers.GameSerializer()
        return Response({'serializer': serializer})

    def post(self, request):
        serializer = serializers.GameSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'serializer': serializer},
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        game = kwargs['game']
        turn = game.get_current_turn()
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
