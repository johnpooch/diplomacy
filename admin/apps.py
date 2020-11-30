from django.contrib.admin.apps import AdminConfig


class DiplomacyAdminConfig(AdminConfig):
    label = 'admin'
    default_site = 'admin.admin.DiplomacyAdminSite'
