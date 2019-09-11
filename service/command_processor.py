from service.models import Build, Convoy, Disband, Hold, Move, Support


class Challenge:

    def __init__(self, piece, territory):
        self.piece = piece
        self.territory = territory

        self.supporting_pieces = []
        self.convoying_pieces = []

    # TODO add some sort of validation to make it so that a fleet challenge
    # can't have convoying_pieces.


class CommandProcessor:

    def __init__(self):
        self.challenges = []

        # create a challenge for every hold command
        for hold in Hold.objects.all():
            challenge = Challenge(hold.piece, hold.source_territory)
            self.challenges.append(challenge)

        # create a challenge for every move command
        for move in Move.objects.all():
            challenge = Challenge(move.piece, move.target_territory)
            self.challenges.append(challenge)

        # add a supporting piece to challenge.convoy for every support command
        for support in Support.objects.all():
            challenge = Challenge(support.piece, support.source_territory)
            self.challenges.append(challenge)
            challenge = self._get_challenge(
                support.aux_piece,
                support.target_territory
            )
            if challenge:
                challenge.supporting_pieces.append(support.piece)
            else:
                # support has failed because aux piece is not attacking target
                pass

        # add a convoying piece to challenge.convoy for every convoy command
        for convoy in Convoy.objects.all():
            challenge = Challenge(convoy.piece, convoy.source_territory)
            self.challenges.append(challenge)
            challenge = self._get_challenge(
                convoy.aux_piece,
                convoy.target_territory
            )
            if challenge:
                challenge.convoying_pieces.append(convoy.piece)
            else:
                # convoy has failed because aux piece is not attacking target
                pass

        # find out if any convoying pieces have been dislodged
        # * only fleets can dislodge a convoying piece
        # * fleets can't be convoyed
        # * resolve fleet challenges to sea territories

        # resolve fleet challenges
        # [self._resolve_challenge(c) for c in self.challenges
        #  if c.piece.is_fleet()]

    def _resolve_challenges(self, challenge):
        """
        """
        pass

    def _determine_strength(self, challenge):
        """
        Determine the strength of a challenge.
        """
        return 1 + len([s for s in challenge.supporting_pieces
                        if not self._dislodged(s)])

    def _dislodged(self, piece):
        """
        Determine whether a piece has been dislodged.
        """
        challenge = self._get_challenge(piece, piece.territory)
        strength = self._determine_strength(self._determine_strength(challenge))
        opposing_challenges = [c for c in self.challenges
                               if c.territory == piece.territory]
        if not opposing_challenges:
            return False
        highest_opposing_strength = max([self._determine_strength(c)
                                         for c in opposing_challenges])
        return strength < highest_opposing_strength

    def _get_challenge(self, piece, territory):
        """
        Get a ``Challenge`` instance from ``self.challenges`` by the ``piece``
        and ``territory`` attributes of the ``Challenge``.
        """
        for c in self.challenges:
            if c.piece == piece and c.territory == territory:
                return c
        return None
