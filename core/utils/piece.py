from core import models
from core.models.base import PieceType


def army(nation, territory, named_coast=None, save=True):
    """
    Creates an army.
    """
    piece = models.Piece(
        nation=nation,
        territory=territory,
        named_coast=named_coast,
        type=PieceType.ARMY,
    )
    if save:
        piece.save()
    return piece


def fleet(nation, territory, named_coast=None, save=True):
    """
    Creates a fleet.
    """
    piece = models.Piece(
        nation=nation,
        territory=territory,
        named_coast=named_coast,
        type=PieceType.FLEET,
    )
    if save:
        piece.save()
    return piece
