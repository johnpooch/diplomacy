from django.conf import settings
from django.urls import include, path

from admin.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('api/v1/', include('service.urls')),
    path('api/v1/auth/', include('accounts.api.urls')),
]


if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
