
from django.urls import include, path

urlpatterns = [
    path('api/v1/', include('service.urls')),
    path('api/v1/auth/', include('accounts.api.urls')),
]
