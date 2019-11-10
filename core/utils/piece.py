from core import models
from core.models.base import PieceType


def army(turn, nation, territory, named_coast=None, save=True):
    """
    Creates an army.
    """
    piece = models.Piece(
        turn=turn,
        nation=nation,
        territory=territory,
        named_coast=named_coast,
        type=PieceType.ARMY,
    )
    if save:
        piece.save()
    return piece


def fleet(turn, nation, territory, named_coast=None, save=True):
    """
    Creates a fleet.
    """
    piece = models.Piece(
        turn=turn,
        nation=nation,
        territory=territory,
        named_coast=named_coast,
        type=PieceType.FLEET,
    )
    if save:
        piece.save()
    return piece
