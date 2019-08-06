from django.contrib.auth.models import User, Group
from rest_framework import viewsets, generics
from .serializers import *
from .models import *


class NationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """
    queryset = Nation.objects.all()
    serializer_class = NationSerializer


class PieceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """
    queryset = Piece.objects.all()
    serializer_class = PieceSerializer


class SupplyCenterViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = SupplyCenter.objects.all()
    serializer_class = SupplyCenterSerializer


class TerritoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """
    queryset = Territory.objects.all()
    serializer_class = TerritorySerializer
