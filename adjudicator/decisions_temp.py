from .decisions.attack_strength import AttackStrength


class Outcomes:
    UNRESOLVED = 'unresolved'
    PATH = 'path'
    NO_PATH = 'no path'
    SUCCEEDS = 'succeeds'
    FAILS = 'fails'
    MOVES = 'moves'
    GIVEN = 'given'
    CUT = 'cut'
    LEGAL = 'legal'
    ILLEGAL = 'illegal'
    DISLODGED = 'dislodged'
    SUSTAINS = 'sustains'
