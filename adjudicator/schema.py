from marshmallow import (
    fields, Schema, validate, validates_schema, ValidationError
)

from adjudicator.base import (
    OrderType, PieceType, Phase, TerritoryType, Variant
)


possible_orders = {
    Phase.ORDER: [
        OrderType.MOVE,
        OrderType.CONVOY,
        OrderType.HOLD,
        OrderType.SUPPORT
    ],
    Phase.RETREAT: [
        OrderType.RETREAT,
        OrderType.DISBAND
    ],
    Phase.BUILD: [
        OrderType.BUILD,
        OrderType.DISBAND
    ],
}


class Territory(fields.Int):
    def _serialize(self, value, attr, obj, **kwargs):
        if value:
            return value.id
        return None


class Piece(fields.Int):
    def _serialize(self, value, attr, obj, **kwargs):
        if value:
            return value.id
        return None


class NationSchema(Schema):
    id = fields.Int(required=True)
    name = fields.String(load_only=True)
    next_turn_supply_delta = fields.Int()
    next_turn_supply_center_count = fields.Int()
    next_turn_piece_count = fields.Int()


class NamedCoastSchema(Schema):
    id = fields.Int(required=True)
    parent = Territory(required=True)
    neighbours = fields.List(Territory(), required=True)
    name = fields.String(missing=None)


class PieceSchema(Schema):
    id = fields.Int(required=True)
    type = fields.String(
        required=True,
        validate=validate.OneOf(PieceType.CHOICES),
        load_only=True,
    )
    nation = fields.Int(required=True, load_only=True)
    territory = Territory(required=True, load_only=True)
    named_coast = fields.Int(missing=None, load_only=True)
    retreating = fields.Boolean(missing=False, load_only=True)
    attacker_territory = Territory(missing=None, load_only=True)
    destroyed = fields.Boolean(missing=False, dump_only=True)
    destroyed_message = fields.String(missing=None, dump_only=True)
    dislodged = fields.Boolean(missing=False, dump_only=True)
    dislodged_by = Piece(missing=None, dump_only=True)
    dislodged_from = Territory(missing=None, dump_only=True)


class OrderSchema(Schema):
    id = fields.Int(required=True)
    type = fields.String(
        required=True,
        validate=validate.OneOf(OrderType.CHOICES),
    )
    nation = fields.Int(required=True, load_only=True)
    source = Territory(required=True, load_only=True)
    target = Territory(missing=None, load_only=True)
    aux = Territory(missing=None, load_only=True)
    target_coast = fields.Int(missing=None, load_only=True)
    via_convoy = fields.Boolean(missing=False, load_only=True)
    illegal = fields.Boolean(missing=False, dump_only=True)
    illegal_code = fields.String(missing=None, dump_only=True)
    illegal_verbose = fields.String(missing=None, dump_only=True)
    outcome = fields.String(missing=None, dump_only=True)
    piece_type = fields.String(
        missing=None,
        validate=validate.OneOf(PieceType.CHOICES),
        load_only=True,
    )

    @validates_schema
    def validate_piece_type_order_type(self, data, **kwargs):
        """
        Ensure that piece type is only specified for build orders
        """
        error_message = 'Piece type should be specified for build orders.'
        if (
            data['type'] != OrderType.BUILD and data['piece_type']
        ) or (
            data['type'] == OrderType.BUILD and not data['piece_type']
        ):
            raise ValidationError({'piece_type': error_message})


class TerritorySchema(Schema):
    id = fields.Int(required=True)
    type = fields.String(
        required=True,
        validate=validate.OneOf(TerritoryType.CHOICES),
        load_only=True,
    )
    neighbours = fields.List(Territory(), required=True, load_only=True)
    shared_coasts = fields.List(Territory(), missing=[], load_only=True)
    nationality = fields.Int(missing=None, load_only=True)
    controlled_by = fields.Int(missing=None, load_only=True)
    contested = fields.Boolean(missing=False, load_only=True)
    name = fields.String(missing=None, load_only=True)
    supply_center = fields.Boolean(missing=False, load_only=True)
    bounce_occurred = fields.Boolean(missing=False, dump_only=True)
    captured_by = fields.Int(missing=None, dump_only=True)


class TurnSchema(Schema):
    id = fields.Int(required=True)
    phase = fields.String(
        required=True,
        validate=validate.OneOf(Phase.CHOICES),
        load_only=True
    )
    season = fields.String(required=True, load_only=True)
    year = fields.Int(required=True, load_only=True)
    variant = fields.Str(missing=Variant.STANDARD)
    territories = fields.Nested(TerritorySchema(many=True), required=True)
    orders = fields.Nested(OrderSchema(many=True), required=True)
    pieces = fields.Nested(PieceSchema(many=True), required=True)
    nations = fields.Nested(NationSchema(many=True), required=True)
    named_coasts = fields.Nested(
        NamedCoastSchema(many=True),
        required=True,
        load_only=True,
    )
    next_season = fields.String(dump_only=True)
    next_phase = fields.String(dump_only=True)
    next_year = fields.Int(dump_only=True)

    @validates_schema
    def validate_order_types_for_phase(self, data, **kwargs):
        """
        Ensure that order types are valid for the turn phase
        """
        errors = {}
        allowed = possible_orders[data['phase']]
        error_message = 'During {} phase valid order types are {}'
        for i, order in enumerate(data['orders']):
            if order['type'] not in allowed:
                message = error_message.format(data['phase'], ', '.join(allowed))
                errors['orders'] = {i: {'type': [message]}}
        if errors:
            raise ValidationError(errors)

    @validates_schema
    def validate_territory_ids(self, data, **kwargs):
        """
        Ensure that all territory id fields have a corresponding territory.
        """
        errors = {}
        territory_ids = [t['id'] for t in data['territories']]
        error_message = 'Territory id does not have a corresponding territory.'
        territory_fields = {
            'orders': ['source', 'target', 'aux'],
            'pieces': ['territory', 'attacker_territory'],
            'named_coasts': ['parent', 'neighbours'],
            'territories': ['neighbours', 'shared_coasts'],
        }
        for k, field_names in territory_fields.items():
            nested_serializer = data[k]
            for i, item in enumerate(nested_serializer):
                for field_name in field_names:
                    value = item[field_name]
                    # cast to list
                    value = value if isinstance(value, list) else [value]
                    if any(v and v not in territory_ids for v in value):
                        errors[k] = {i: {field_name: [error_message]}}
        if errors:
            raise ValidationError(errors)

    @validates_schema
    def validate_nation_ids(self, data, **kwargs):
        """
        Ensure that all nation id fields have a corresponding nation.
        """
        errors = {}
        nation_ids = [n['id'] for n in data['nations']]
        error_message = 'Nation id does not have a corresponding nation.'
        nation_fields = {
            'orders': ['nation'],
            'pieces': ['nation'],
            'named_coasts': ['parent', 'neighbours'],
            'territories': ['nationality', 'controlled_by'],
        }
        for k, field_names in nation_fields.items():
            nested_serializer = data[k]
            for i, item in enumerate(nested_serializer):
                for field_name in field_names:
                    value = item[field_name]
                    # cast to list
                    value = value if isinstance(value, list) else [value]
                    if any(v and v not in nation_ids for v in value):
                        errors[k] = {i: {field_name: [error_message]}}
        if errors:
            raise ValidationError(errors)
