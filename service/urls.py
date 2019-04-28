
from django.urls import path, include
from rest_framework import routers
from django.conf import settings

from . import views

router = routers.DefaultRouter()
router.register(r'nation', views.NationViewSet),
router.register(r'piece', views.PieceViewSet),
router.register(r'territory', views.TerritoryViewSet),
router.register(r'supply_center', views.SupplyCenterViewSet),

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
