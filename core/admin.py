from django.contrib import admin
from . import models


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
    inlines = [TurnInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('turns')
        return queryset

    def has_add_permission(self, request, obj=None):
        return False


class TurnAdmin(ReadOnly, admin.ModelAdmin):

    inlines = [
        TerritoryStateInline,
        PieceStateInline,
    ]


admin.site.register(models.Game, GameAdmin)
admin.site.register(models.Turn, TurnAdmin)
admin.site.register(models.Variant, VariantAdmin)
