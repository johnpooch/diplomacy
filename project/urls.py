from django.urls import include, path

from admin.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('api/v1/', include('service.urls')),
    path('api/v1/auth/', include('accounts.api.urls')),
]
