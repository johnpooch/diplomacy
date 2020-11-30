from django.contrib import admin
from django.contrib.admin import AdminSite
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from core import models


class DiplomacyAdminSite(AdminSite):
    site_header = 'Diplomacy admin'


class ReadOnly:

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class TerritoryInline(admin.TabularInline):
    model = models.Territory
    ordering = ('name', )


class TerritoryStateInline(admin.TabularInline):
    model = models.TerritoryState
    ordering = ('territory__name', )


class PieceStateInline(admin.TabularInline):
    model = models.PieceState


class TurnInline(ReadOnly, admin.TabularInline):
    model = models.Turn
    readonly_fields = []
    can_delete = False
    show_change_link = True


class VariantAdmin(ReadOnly, admin.ModelAdmin):

    inlines = [TerritoryInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('territories')
        return queryset


class GameAdmin(admin.ModelAdmin):

    exclude = (
        'winners',
    )
    readonly_fields = (
        'created_by',
        'initialized_at',
        'variant',
    )
    list_display = ('name', 'status')
    inlines = [TurnInline]
    search_fields = ['name']
    list_filter = ['status', 'private']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('turns')
        return queryset

    def has_add_permission(self, request, obj=None):
        return False


class TurnAdmin(ReadOnly, admin.ModelAdmin):

    list_filter = (
        ('game', RelatedDropdownFilter),
    )
    inlines = [
        TerritoryStateInline,
        PieceStateInline,
    ]


admin_site = DiplomacyAdminSite(name='admin')

admin_site.register(models.Game, GameAdmin)
admin_site.register(models.Turn, TurnAdmin)
admin_site.register(models.Variant, VariantAdmin)
