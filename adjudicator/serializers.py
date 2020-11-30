from rest_framework import serializers

from adjudicator import order, piece, territory
from adjudicator.named_coast import NamedCoast


class TerritoryField(serializers.IntegerField):

    def to_representation(self, value):
        return int(value.id)


class PieceField(serializers.IntegerField):

    def to_representation(self, value):
        return int(value.id)


class BaseSerializer(serializers.Serializer):

    type = serializers.CharField(allow_null=True)

    @property
    def state(self):
        return self.context['state']

    def create(self, validated_data):
        _type = validated_data.get('type')
        _class = self.type_dict[_type]
        state = self.context['state']
        instance = _class(state, **validated_data)
        return instance


class TerritorySerializer(BaseSerializer):

    type_dict = {
        'sea': territory.SeaTerritory,
        'inland': territory.InlandTerritory,
        'coastal': territory.CoastalTerritory,
    }

    bounce_occurred = serializers.BooleanField(required=False)
    contested = serializers.BooleanField(required=False)
    controlled_by = serializers.IntegerField(required=False, allow_null=True)
    id = serializers.IntegerField()
    name = serializers.CharField()
    nationality = serializers.IntegerField(required=False, allow_null=True)
    neighbours = serializers.ListField()
    shared_coasts = serializers.ListField(required=False)
    supply_center = serializers.BooleanField(required=False)


class NamedCoastSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    territory = serializers.IntegerField(source='parent')
    neighbours = serializers.ListField()

    def __init__(self, **kwargs):
        self.state = kwargs.pop('state', None)
        super().__init__(**kwargs)

    def create(self, validated_data):
        state = self.context['state']
        territory_id = validated_data.get('parent')
        if territory_id:
            validated_data['parent'] = state.get_territory_by_id(territory_id)
        instance = NamedCoast(state, **validated_data)
        return instance


class PieceSerializer(BaseSerializer):

    type_dict = {
        'army': piece.Army,
        'fleet': piece.Fleet,
    }

    attacker_territory = TerritoryField(
        required=False,
        allow_null=True
    )
    dislodged_decision = serializers.CharField(required=False)
    dislodged_by = PieceField(required=False)
    destroyed = serializers.BooleanField(required=False)
    destroyed_message = serializers.CharField(required=False)
    id = serializers.IntegerField()
    nation = serializers.IntegerField()
    retreating = serializers.BooleanField(required=False)
    territory = TerritoryField()

    def create(self, validated_data):
        territory_id = validated_data['territory']
        validated_data['territory'] = self.state.get_territory_by_id(territory_id)
        named_coast_id = validated_data.get('named_coast')
        if named_coast_id:
            validated_data['named_coast'] = self.state.get_named_coast_by_id(named_coast_id)
        return super().create(validated_data)


class OrderSerializer(BaseSerializer):

    type_dict = {
        'hold': order.Hold,
        'move': order.Move,
        'support': order.Support,
        'convoy': order.Convoy,
        'retreat': order.Retreat,
        'disband': order.Disband,
        'build': order.Build,
    }

    aux = TerritoryField(required=False, allow_null=True)
    id = serializers.IntegerField()
    illegal = serializers.BooleanField(required=False)
    illegal_code = serializers.CharField(required=False, allow_null=True)
    illegal_verbose = serializers.CharField(required=False, allow_null=True)
    outcome = serializers.CharField(required=False)
    nation = serializers.IntegerField()
    piece_type = serializers.CharField(required=False, allow_null=True)
    source = TerritoryField()
    target = TerritoryField(required=False, allow_null=True)
    target_coast = serializers.IntegerField(required=False, allow_null=True)
    via_convoy = serializers.BooleanField(required=False)

    def create(self, validated_data):
        source_id = validated_data['source']
        validated_data['source'] = self.state.get_territory_by_id(source_id)
        target_id = validated_data.get('target')
        if target_id:
            validated_data['target'] = self.state.get_territory_by_id(target_id)
        aux_id = validated_data.get('aux')
        if aux_id:
            validated_data['aux'] = self.state.get_territory_by_id(aux_id)
        target_coast_id = validated_data.get('target_coast')
        if target_coast_id:
            validated_data['target_coast'] = self.state.get_territory_by_id(target_coast_id)
        return super().create(validated_data)


class GameSerializer(serializers.Serializer):

    named_coasts = NamedCoastSerializer(many=True)
    orders = OrderSerializer(many=True)
    pieces = PieceSerializer(many=True)
    territories = TerritorySerializer(many=True)

    def create(self, validated_data):
        for name in ['territories', 'named_coasts', 'orders', 'pieces']:
            data = validated_data[name]
            self.fields[name].create(data)
        return validated_data
