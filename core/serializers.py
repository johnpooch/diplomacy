"""
Provides an interface between `core` and `adjudicator`. Interactions happen
only through the `TurnSerializer` which reads and writes to the child
serializers appropriately.

Collectively the serializers fulfill the following responsibilities:

    (1) Serialize a Turn instance into the data format that the adjudicator
        expects.

    (2) Deserialize the adjudicator response, updating the Turn instance and
        its related objects in the process.

    (3) Account for naming mismatches between core and adjudicator entities.
"""

from django.utils import timezone
from drf_writable_nested.serializers import NestedUpdateMixin
from rest_framework import serializers

from core import models


class BaseChildSerializer(serializers.ModelSerializer):

    # disable create method
    create = None


class ReadOnlyModelSerializer(serializers.ModelSerializer):

    # disable update method
    update = None

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields


class NamedCoastSerializer(ReadOnlyModelSerializer, BaseChildSerializer):

    class Meta:
        model = models.NamedCoast
        fields = (
            'name',
            'parent',
            'neighbours',
        )


class PieceSerializer(BaseChildSerializer):

    class Meta:
        model = models.Piece
        fields = (
            'type',
            'nation',
        )


class PieceStateSerializer(BaseChildSerializer):

    piece = PieceSerializer(read_only=True)
    retreating = serializers.SerializerMethodField()

    class Meta:
        model = models.PieceState
        fields = (
            'id',
            'piece',
            'retreating',
            'attacker_territory',
            'territory',
            'named_coast',
            'destroyed',
            'destroyed_message',
            'dislodged',
            'dislodged_by',
        )
        extra_kwargs = {
            'destroyed': {'write_only': True},
            'destroyed_message': {'write_only': True},
            'dislodged': {'write_only': True},
            'dislodged_by': {'write_only': True},
        }

    def get_retreating(self, obj):
        return obj.must_retreat

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        territory_representation = representation.pop('piece')
        for key in territory_representation:
            representation[key] = territory_representation[key]
        return representation


class TerritorySerializer(BaseChildSerializer):

    named_coasts = NamedCoastSerializer(many=True)

    class Meta:
        model = models.Territory
        fields = (
            'id',
            'type',
            'name',
            'named_coasts',
            'neighbours',
            'shared_coasts',
            'nationality',
            'supply_center',
        )


class TerritoryStateSerializer(BaseChildSerializer):

    territory = TerritorySerializer(read_only=True)

    class Meta:
        model = models.TerritoryState
        fields = (
            'bounce_occurred',
            'contested',
            'controlled_by',
            'territory',
        )
        read_only_fields = (
            'contested',
        )
        extra_kwargs = {
            'bounce_occurred': {'write_only': True},
        }

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        territory_representation = representation.pop('territory')
        for key in territory_representation:
            representation[key] = territory_representation[key]
        return representation


class OrderSerializer(BaseChildSerializer):

    class Meta:
        model = models.Order
        fields = (
            'id',
            'type',
            'nation',
            'source',
            'target',
            'target_coast',
            'aux',
            'piece_type',
            'via_convoy',
            'illegal',
            'illegal_code',
            'illegal_verbose',
            'outcome',
        )
        read_only_fields = (
            'source',
            'nation',
            'type',
        )
        extra_kwargs = {
            'illegal': {'write_only': True},
            'illegal_code': {'write_only': True},
            'illegal_verbose': {'write_only': True},
            'outcome': {'write_only': True},
        }


class TurnSerializer(NestedUpdateMixin, serializers.ModelSerializer):

    pieces = PieceStateSerializer(
        many=True,
        source='piecestates'
    )
    territories = TerritoryStateSerializer(
        many=True,
        source='territorystates'
    )
    orders = OrderSerializer(many=True)
    variant = serializers.SerializerMethodField()

    class Meta:
        model = models.Turn
        fields = (
            'id',
            'territories',
            'pieces',
            'orders',
            'phase',
            'variant',
        )
        read_only_fields = (
            'phase',
        )

    def __init__(self, *args, **kwargs):
        # Ensure that updates are always partial to avoid modifying other
        # fields on the model.
        kwargs['partial'] = True
        super().__init__(*args, **kwargs)

    def get_variant(self, obj):
        return obj.game.variant.name

    def to_representation(self, obj):
        # The adjudicator expects named_coasts to be un-nested from territories
        representation = super().to_representation(obj)
        territories_representation = representation.get('territories')
        named_coasts = []
        for territory in territories_representation:
            named_coasts = [*named_coasts, *territory.pop('named_coasts')]
        representation['named_coasts'] = named_coasts
        return representation

    def update(self, instance, validated_data):
        instance.processed = True
        instance.processed_at = timezone.now()
        return super().update(instance, validated_data)

    def _prefetch_related_instances(self, field, related_data):
        """
        We have to wrangle with `drf_writable_nested` to account for the
        incoming write data having the `Territory` id instead of the
        `TerritoryState` id. It isn't pretty but it seems to work.
        """
        model_class = field.Meta.model
        if model_class == models.TerritoryState:
            pk_list = self._extract_related_pks(field, related_data)
            instances = {
                str(related_instance.territory.pk): related_instance
                for related_instance in model_class.objects.filter(
                    territory__pk__in=pk_list
                )
            }
            return instances
        return super()._prefetch_related_instances(field, related_data)
