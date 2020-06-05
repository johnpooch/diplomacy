from .piece import PieceTypes


class Check:
    pass


class SourcePieceBelongsToNation(Check):

    code = '001'
    message = 'Cannot order a piece belonging to another nation.'

    def fail_condition(self, order):
        return order.source.piece.nation != order.nation


class SourceAndTargetDistinct(Check):

    code = '002'
    message = 'Source and target cannot be the same territory.'

    def fail_condition(self, order):
        return order.target == order.source


class ArmyMovesToAdjacentTerritoryNotConvoy(Check):

    code = '003'
    message = 'Army cannot reach non-adjacent territory without convoy.'

    def fail_condition(self, order):
        piece = order.source.piece
        return piece.is_army and not order.source.adjacent_to(order.target) \
            and not order.via_convoy


class FleetMovesToAdjacentTerritory(Check):

    code = '004'
    message = 'Fleet cannot reach non-adjacent territory.'

    def fail_condition(self, order):
        piece = order.source.piece
        return piece.is_fleet and not order.source.adjacent_to(order.target)


class ArmyCanReachTarget(Check):

    code = '005'
    message = 'Army cannot enter a sea territory'

    def fail_condition(self, order):
        piece = order.source.piece
        return piece.is_army and not piece.can_reach(order.target)


class FleetCanReachTarget(Check):

    code = '006'
    message = 'Fleet cannot enter an inland territory'

    def fail_condition(self, order):
        piece = order.source.piece
        return not piece.can_reach(order.target, order.target_coast) \
            and piece.is_fleet and not order.target.is_coastal


class FleetCanReachTargetCoastal(Check):

    code = '007'
    message = (
        'Fleet cannot reach coastal territory without shared coastline.'
    )

    def fail_condition(self, order):
        piece = order.source.piece
        return piece.is_fleet \
            and not piece.can_reach(order.target, order.target_coast) \
            and order.target.is_coastal


class ConvoyeeIsArmy(Check):

    code = '008'
    message = (
        'Cannot convoy a fleet.'
    )

    def fail_condition(self, order):
        return order.aux.piece.is_fleet


class AtSea(Check):

    code = '009'
    message = (
        'Convoying fleet must be at sea.'
    )

    def fail_condition(self, order):
        return not order.source.is_sea


class CanReachTargetWithoutConvoy(Check):

    code = '010'
    message = (
        'Piece cannot reach that territory.'
    )

    def fail_condition(self, order):
        piece = order.source.piece
        return not piece.can_reach_support(order.target)


class SourceNotOccupied(Check):

    code = '011'
    message = (
        'Source is already occupied by a piece.'
    )

    def fail_condition(self, order):
        return bool(order.source.piece)


class SourceHasSupplyCenter(Check):

    code = '012'
    message = (
        'Source does not have a supply center.'
    )

    def fail_condition(self, order):
        return not order.source.supply_center


class SourceWithinNationalBorders(Check):

    code = '013'
    message = (
        'Source is outside of national borders.'
    )

    def fail_condition(self, order):
        return not order.source.nationality == order.nation


class SourceIsControlled(Check):

    code = '014'
    message = (
        'Cannot build in a supply center which is controlled by a foreign '
        'power.'
    )

    def fail_condition(self, order):
        return not order.source.controlled_by == order.nation


class PieceTypeCanExist(Check):

    code = '015'
    message = (
        'Piece type cannot exist in this type of territory.'
    )

    def fail_condition(self, order):
        return order.source.is_inland and order.piece_type == PieceTypes.FLEET


class SourceNamedCoastNotSpecified(Check):

    code = '016'
    message = (
        'Must specify a coast when building a fleet in a territory with named '
        'coasts.'
    )

    def fail_condition(self, order):
        return order.source.is_complex and order.piece_type == PieceTypes.FLEET \
            and not order.named_coast


class TargetNotAttackerTerritory(Check):

    code = '017'
    message = (
        'Piece cannot retreat to the territory from which it was attacked.'
    )

    def fail_condition(self, order):
        piece = order.source.piece
        return order.target == piece.attacker_territory


class TargetNotContested(Check):

    code = '018'
    message = (
        'Cannot retreat to a territory which was contested on the previous '
        'turn.'
    )

    def fail_condition(self, order):
        return order.target.contested
