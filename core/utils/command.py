from core import models
from core.models.base import CommandType


def hold(order, piece, source, save=True):
    """
    Creates a hold command.
    """
    hold = models.Command(
        order=order,
        piece=piece,
        source=source,
        type=CommandType.HOLD,
    )
    if save:
        hold.save()
    return hold


def move(order, piece, source, target, target_coast=None, save=True):
    """
    Creates a move command.
    """
    move = models.Command(
        order=order,
        piece=piece,
        source=source,
        target=target,
        target_coast=target_coast,
        type=CommandType.MOVE,
    )
    if save:
        move.save()
    return move


def convoy(order, piece, source, aux, target, target_coast=None, save=True):
    """
    Creates a convoy command.
    """
    convoy = models.Command(
        order=order,
        piece=piece,
        source=source,
        aux=aux,
        target=target,
        target_coast=target_coast,
        type=CommandType.CONVOY,
    )
    if save:
        convoy.save()
    return convoy


def support(order, piece, source, aux, target, target_coast=None, save=True):
    """
    Creates a support command.
    """
    support = models.Command(
        order=order,
        piece=piece,
        source=source,
        aux=aux,
        target=target,
        target_coast=target_coast,
        type=CommandType.SUPPORT,
    )
    if save:
        support.save()
    return support


def build(order, piece_type, target, target_coast=None, save=True):
    """
    Creates a build command.
    """
    build = models.Command(
        order=order,
        piece_type=piece_type,
        target=target,
        target_coast=target_coast,
        type=CommandType.BUILD,
    )
    if save:
        build.save()
    return build
