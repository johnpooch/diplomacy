import copy

from service import models


class Convoy:
    def __init__(self, aux_territory, source_territories, target_territory):
        self.aux_territory = aux_territory
        self.source_territories = source_territories
        self.target_territory = target_territory


class Challenge:
    def __init__(self, source, target, convoy_paths=[]):
        self.source = source
        self.target = target
        self.convoy_paths = convoy_paths
        self.suport = 0
        self.successful = True


class CommandProcessor:
    """
    """
    
    def get_convoy_paths(self, source, convoy, target, previous=[]):
        """
        Determines all available paths between the source territory and the
        target using a list of connecting territories (convoy).

        Returns a list of paths. Each path is a list of territories.

        The function is recursive. The 'previous' parameter is should not be
        filled when initially calling the function.
        """
        paths = []
        for territory in [t for t in convoy if t.is_neighbour(source)]:
            if territory.is_neighbour(target):
                paths.append([territory] + previous)
                continue
            remaining = copy.deepcopy(convoy)
            remaining.remove(territory)
            if [t for t in remaining if t.is_neighbour(territory)]:
                paths.extend(self.get_convoy_paths(
                        territory,
                        remaining,
                        target,
                        previous + [territory]))
        return paths


    def get_convoying_territories(self, move_source, move_target):
        """
        Returns the territories of all fleets convoying from the move_source
        to the move_target.
        """
        commands = models.Command.current_turn_commands.filter(
                    type='C',
                    aux_territory=move_source,
                    target_territory=move_target)
        return [c.source_territory for c in commands]

    def create_challenge(self, command):
        """
        """
        if command.source_territory.get_friendly_piece(command.order.nation):
            if command.type == "M":
                challenges[command.target_territory] = [{
                        "source": command.source_territory,
                        "strength": 1,
                }]
            else:
                challenges[command.source_territory] = [{
                        "source": command.source_territory,
                        "strength": 1,
                }]


    def create_challenges(self, commands):
        """
        """
        challenges = {}
        for command in commands:
            if command.source_territory.get_friendly_piece(command.order.nation):
                if command.type == "M":
                    challenges[command.target_territory] = [{
                            "source": command.source_territory,
                            "strength": 1,
                    }]
                else:
                    challenges[command.source_territory] = [{
                            "source": command.source_territory,
                            "strength": 1,
                    }]
        return challenges

    def process_commands(self, commands):
        """
        """
        pass

        # all_territories = models.Territory.objects.all()
        # crunch = {}
        # for territory in all_territories:
        #     crunch[territory] = {
        #         "challenges": []
        #     }
        # commands = models.Command.current_turn_commands.all()
        # for hold in [c for c in commands if c.type == 'H']:
        #     
        # for move in [c for c in commands if c.type == 'M']:
        #     # check piece exists in source territory belonging to command issuer
        #     convoy_paths = []
        #     piece = move.source_territory.get_friendly_piece(move.order.nation)
        #     if not piece:
        #         command.fail("")
        #         continue
        #     # check target territory is accessible by piece type
        #     if not move.target_territory.accessible_by_piece_type(piece):
        #         command.fail("")
        #         continue
        #     # check target territory is neighbour of source
        #     if not move.source_territory.is_neighbour(move.target_territory):
        #         # if army
        #         self.attempt_convoy(move)
        #         if piece.type == 'A':
        #             convoy = self.get_convoying_territories(move.source_territory,
        #                     move.target_territory)
        #             for territory in convoy:
        #                 # check if piece exists in territory
        #             # TODO: check if the any convoying fleet is dislodged
        #             # TODO: check that the attack is valid
        #             # TODO: if it is, remove from convoy and mark that convoy as failed.
        #             convoy_paths = self.get_convoy_paths(move.source_territory,
        #                     convoy, move.target_territory)
        #             if not convoy_paths:
        #                 command.fail("")
        #                 continue
        #     # if sucessful create challenge
        #     challenge = {
        #         "source": move.source_territory,
        #         "support": [],
        #         "convoy_paths": []
        #     }
        #     crunch[move.target_territory]["challenges"].append(challenge)
        #     for t, v in crunch.items():
        #         if str(t) == "Wales":
        #             print(v)


