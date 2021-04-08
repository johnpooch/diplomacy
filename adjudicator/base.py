class OrderType:
    HOLD = 'hold'
    MOVE = 'move'
    SUPPORT = 'support'
    CONVOY = 'convoy'
    RETREAT = 'retreat'
    BUILD = 'build'
    DISBAND = 'disband'
    CHOICES = [HOLD, MOVE, SUPPORT, CONVOY, RETREAT, BUILD, DISBAND]


class PieceType:
    ARMY = 'army'
    FLEET = 'fleet'
    CHOICES = [ARMY, FLEET]


class Phase:
    ORDER = 'order'
    RETREAT = 'retreat'
    BUILD = 'build'
    CHOICES = [ORDER, RETREAT, BUILD]


class Season:
    FALL = 'fall'
    SPRING = 'spring'
    CHOICES = [FALL, SPRING]


class TerritoryType:
    INLAND = 'inland'
    COASTAL = 'coastal'
    SEA = 'sea'
    CHOICES = [INLAND, COASTAL, SEA]


class Variant:
    STANDARD = 'standard'
