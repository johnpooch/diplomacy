from django.db import transaction
from django.db.models import Prefetch

from core import models


def debug_command(command):
    print('\n')
    print(command)
    if command.is_move:
        print(f'MAX ATTACK STRENGTH: {command.max_attack_strength}')
        print(f'MIN ATTACK STRENGTH: {command.min_attack_strength}')

        print(f'MAX DEFEND STRENGTH: {command.max_defend_strength}')
        print(f'MIN DEFEND STRENGTH: {command.min_defend_strength}')

        print(f'MAX PREVENT STRENGTH: {command.max_prevent_strength}')
        print(f'MIN PREVENT STRENGTH: {command.min_prevent_strength}')

        print(f'TERRITORY MAX HOLD STRENGTH: {command.target.max_hold_strength}')
        print(f'TERRITORY MIN HOLD STRENGTH: {command.target.min_hold_stength}')

        print(
            'SUPPORTING COMMANDS: '
            f'{command.supporting_commands}'
        )
        print(
            'OTHER ATTACKING PIECES: '
            f'{command.target.other_attacking_pieces(command.piece)}'
        )
    if command.illegal:
        print(f'COMMAND ILLEGAL MESSAGE: {command.illegal_message}')
    print(f'COMMAND OUTCOME: {command.state}')


# TODO consider where this should be
def initialize_processor(turn):

    # NOTE this should probably just happen in the judge init method
    commands = list(
        models.Command.objects.filter(
            order__turn=turn,
        ).select_related(
            'order__nation',
            'source__piece__nation',
            'aux__piece',
            'target__piece__nation',
            'target_coast',
            'piece',
        ).prefetch_related(
            'source__neighbours',
            'source__shared_coasts',
            'source__named_coasts',
            'source__attacking_pieces',
            'source__piece__named_coast__neighbours',
            'aux__neighbours',
            'aux__shared_coasts',
            'aux__named_coasts',
            'aux__attacking_pieces',
            'target__neighbours',
            'target__shared_coasts',
            'target__named_coasts',
            'target__attacking_pieces',
        )
    )
    for command in commands:
        if command.is_move:
            for other_command in commands:
                if other_command.is_support and \
                        other_command.aux == command.source and \
                        other_command.target == command.target:
                    command.supporting_commands.append(other_command)
        else:
            for other_command in commands:
                if other_command.is_support and \
                        other_command.aux == command.source and \
                        other_command.target == command.source:
                    command.supporting_commands.append(other_command)
    return Processor(commands)


class Processor:
    """
    Resolves all of the game orders and updates the game state accordingly.
    """

    # TODO sort out the num queries and architecture first. Then refactor the
    # model methods.

    # can you add an attibute to the model which is None by default and once
    # the model has been initialized, add the correct value, `piece.all_pieces
    # = all_pieces`.
    def __init__(self, commands):
        """
        Prepares all of the necessary data such that the no queries need to be
        executed during the command processing.
        """
        self.commands = commands

    def process(self):

        # determine whether any commands are illegal
        for command in self.commands:
            command.check_illegal()

        # remove illegal commands from list
        legal_commands = [c for c in self.commands if not c.illegal]

        unresolved_fleet_commands = [c for c in legal_commands if c.piece.is_fleet()]

        # determine whether any convoys are dislodged. this means resovling
        # move and support commands of all other fleets
        while True:

            # NOTE this is weird
            for command in unresolved_fleet_commands:
                if command.piece.dislodged_state.unresolved:
                    command.piece.dislodged_decision()

            # resolve all fleet commands
            for command in unresolved_fleet_commands:
                if not command.unresolved:
                    command.resolve()

            # filter out resolved commands
            unresolved_fleet_commands = [c for c in unresolved_fleet_commands
                                         if c.unresolved or c.piece.unresolved]

            # if there are no more unresolved convoy commands
            if not [c for c in unresolved_fleet_commands if c.type.is_convoy]:
                break

        commands = [c for c in legal_commands if not c.is_convoy]
        unresolved_commands = [c for c in commands if c.unresolved]

        while True:

            for command in unresolved_commands:
                if command.piece.unresolved:
                    command.piece.dislodged_decision()

            for command in unresolved_commands:
                command.resolve()
                debug_command(command)

            unresolved_commands = [c for c in unresolved_commands
                                   if c.unresolved or c.piece.unresolved]

            # if there are no more unresolved convoy commands
            if not unresolved_commands:
                break

    def update_game_state(self):
        """
        * Create new turn
        * Save all the commands of the old turn
        * Create new pieces, territories, etc for the new turn reflecting the
          new state of the game.
        """
        with transaction.atomic():
            for c in self.commands:
                c.save()
