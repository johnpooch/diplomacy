class Check:
    pass


class SourcePieceBelongsToNation(Check):

    code = '001'
    message = 'Cannot order a piece belonging to another nation.'

    def condition(self, order):
        return order.source.piece.nation != order.nation


class SourceAndTargetDistinct(Check):

    code = '002'
    message = 'Source and target cannot be the same territory.'

    def condition(self, order):
        return order.target == order.source


class ArmyMovesToAdjacentTerritoryNotConvoy(Check):

    code = '003'
    message = 'Army cannot reach non-adjacent territory without convoy.'

    def condition(self, order):
        piece = order.source.piece
        return piece.is_army and not order.source.adjacent_to(order.target) \
            and not order.via_convoy


class FleetMovesToAdjacentTerritory(Check):

    code = '004'
    message = 'Fleet cannot reach non-adjacent territory.'

    def condition(self, order):
        piece = order.source.piece
        return piece.is_fleet and not order.source.adjacent_to(order.target)


class ArmyCanReachTarget(Check):

    code = '005'
    message = 'Army cannot enter a sea territory'

    def condition(self, order):
        piece = order.source.piece
        return not piece.can_reach(order.target) and piece.is_army


class FleetCanReachTarget(Check):

    code = '006'
    message = 'Fleet cannot enter an inland territory'

    def condition(self, order):
        piece = order.source.piece
        return not piece.can_reach(order.target) and piece.is_fleet \
            and not order.target.is_coastal


class FleetCanReachTargetCoastal(Check):

    code = '007'
    message = (
        'Fleet cannot reach coastal territory without shared coastline.'
    )

    def condition(self, order):
        piece = order.source.piece
        return not piece.can_reach(order.target) and piece.is_fleet \
            and order.target.is_coastal


class ConvoyeeIsArmy(Check):

    code = '008'
    message = (
        'Cannot convoy a fleet.'
    )

    def condition(self, order):
        return order.aux.piece.is_fleet


class AtSea(Check):

    code = '009'
    message = (
        'Convoying fleet must be at sea.'
    )

    def condition(self, order):
        return order.source.is_sea
