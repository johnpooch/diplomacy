class ResolverMixin:

    def resolve(self):
        """
        """
        if not self.unresolved:
            raise ValueError(
                'Cannot call `resolve()` on a command which is already '
                'resolved.'
            )

        # TODO make this magic
        if self.is_hold:
            self.resolve_hold()

        if self.is_move:
            self.resolve_move()

        if self.is_support:
            self.resolve_support()

        if self.is_convoy:
            self.resolve_convoy()

    def resolve_hold(self):
        """
        """
        if self.piece.sustains:
            self.set_succeeds()
        if self.piece.dislodged:
            self.set_fails()

    def resolve_move(self):
        """
        """
        # succeeds if...
        min_attack_strength = self.min_attack_strength
        max_attack_strength = self.max_attack_strength

        if self.head_to_head_exists():
            opposing_unit = self.target.piece
            if min_attack_strength > opposing_unit.command.max_defend_strength:
                if self.target.other_attacking_pieces(self.piece):
                    if min_attack_strength > max(
                            [p.command.max_prevent_strength
                             for p in self.target.other_attacking_pieces(self.piece)]
                    ):
                        return self.set_succeeds()
                else:
                    return self.set_succeeds()
        else:
            if self.target.other_attacking_pieces(self.piece):
                if min_attack_strength > self.target.max_hold_strength:
                    if min_attack_strength > max(
                        [p.command.max_prevent_strength
                         for p in self.target.other_attacking_pieces(self.piece)]
                    ):
                        return self.set_succeeds()
            else:
                if min_attack_strength > self.target.max_hold_strength:
                    return self.set_succeeds()

        # fails if...
        if self.head_to_head_exists():
            opposing_unit = self.target.piece
            if max_attack_strength <= opposing_unit.command.min_defend_strength:
                return self.set_fails()
        if max_attack_strength <= self.target.min_hold_strength:
            return self.set_fails()
        if self.target.other_attacking_pieces(self.piece):
            if max_attack_strength <= min(
                [p.command.min_prevent_strength
                 for p in self.target.other_attacking_pieces(self.piece)]
            ) and [p.command.min_prevent_strength
                   for p in self.target.other_attacking_pieces(self.piece)]:
                return self.set_fails()

    def resolve_support(self):
        """
        """
        # TODO refactor
        # succeeds if...
        if not self.source.attacking_pieces:
            self.set_succeeds()
        if self.source.piece.sustains:
            if self.target.occupied() and self.aux.occupied():
                if self.aux.piece.command.is_move and \
                        self.aux.piece.command.target == self.target:
                    if self.target.piece.command.is_convoy:
                        convoying_command = self.target.piece.command
                        if convoying_command.aux.occupied():
                            if all([p.command.max_attack_strength == 0  # aaa
                                    for p in self.source.other_attacking_pieces
                                    (convoying_command.aux.piece)]):
                                self.set_succeeds()
                    else:
                        if all([p.command.max_attack_strength == 0  # aaa
                                for p in self.source.other_attacking_pieces
                                (self.target.piece)]):
                            self.set_succeeds()
            if all([p.command.max_attack_strength == 0
                    for p in self.source.attacking_pieces]):
                self.set_succeeds()

        # fails if...
        # If aux piece is not going to target of command
        if self.aux.occupied():
            if self.aux.piece.command.is_move \
                    and self.aux.piece.command.target != self.target \
                    and not self.aux.piece.command.illegal:
                self.set_fails()
        # If aux piece holds and support target is not same as aux
        if not self.aux.piece.command.is_move and self.target != self.aux:
            self.set_fails()

        if self.source.piece.dislodged:
            self.set_fails()
        if self.target.occupied() and self.aux.occupied():
            if self.aux.piece.command.is_move and \
                    self.aux.piece.command.target == self.target:
                if self.target.piece.command.is_convoy:
                    convoying_command = self.target.piece.command
                    if convoying_command.aux.occupied():
                        if any([p.command.min_attack_strength >= 1
                                for p in self.source.other_attacking_pieces
                                (convoying_command.aux.piece)]):
                            self.set_fails()
                else:
                    if any([p.command.min_attack_strength >= 1
                            for p in self.source.other_attacking_pieces
                            (self.target.piece)]):
                        self.set_fails()
                return
        if self.source.attacking_pieces and \
                any([p.command.min_attack_strength >= 1
                     for p in self.source.attacking_pieces
                     if p.territory != self.aux.piece.command.target]):
            self.set_fails()

    def resolve_convoy(self):
        """
        """
        # if unmatched
        if not self.aux.piece.command.target == self.target:
            self.set_fails()
        # TODO somehow set fails if not part of successful convoy path
        if self.piece.dislodged:
            self.set_fails()
        if self.piece.sustains:
            self.set_succeeds()
