from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status, views
from rest_framework import permissions as drf_permissions
from rest_framework.response import Response

from core import models
from service import serializers
from service import permissions as custom_permissions

from rest_framework.exceptions import NotFound


def error404():
    raise NotFound(detail="Error 404, page not found", code=404)


# TODO all views need to be refactored using django rest mixins etc.
# TODO major testing pass
class GameStateView(views.APIView):
    """
    Provides the data necessary to render the game board state at the given
    turn.
    """

    def get(self, request, format=None, **kwargs):

        game_id = kwargs['game']
        turn_id = kwargs.get('turn')

        game = get_object_or_404(models.Game, id=game_id)

        if not turn_id:
            turn = game.get_current_turn()
        else:
            turn = get_object_or_404(models.Turn, id=turn_id)

        territory_states = models.TerritoryState.objects.filter(turn=turn)
        territory_states_serializer = serializers\
            .TerritoryStateSerializer(territory_states, many=True)

        nation_states = models.NationState.objects.filter(turn=turn)
        nation_states_serializer = serializers\
            .NationStateSerializer(nation_states, many=True)

        return Response(
            {
                'territory_states': territory_states_serializer.data,
                'nation_states': nation_states_serializer.data,
            }
        )


class GameList(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               generics.GenericAPIView):

    permission_classes = [drf_permissions.IsAuthenticatedOrReadOnly]

    queryset = models.Game.objects.all()
    serializer_class = serializers.GameSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Override create method to save ``created_by`` field.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class CommandView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):

    # TODO add is participant permission
    permission_classes = [drf_permissions.IsAuthenticated]

    queryset = models.Command.objects.all()
    serializer_class = serializers.CommandSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
