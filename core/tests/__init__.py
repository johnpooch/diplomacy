from django.contrib.auth.models import User
from django.utils import timezone

from core import models
from core.models import base


class DiplomacyTestCaseMixin:

    def create_test_user(self, save=True, **kwargs):
        kwargs.setdefault('username', timezone.now().isoformat())
        kwargs.setdefault('email', timezone.now().isoformat() + '@test.com')
        kwargs.setdefault('first_name', 'test')
        kwargs.setdefault('first_name', 'test')
        user = User(**kwargs)
        if save:
            user.save()
        return user

    def create_test_variant(self, save=True, **kwargs):
        kwargs.setdefault('name', 'Test variant')
        variant = models.Variant(**kwargs)
        if save:
            variant.save()
        return variant

    def create_test_nation(self, save=True, **kwargs):
        if 'variant' not in kwargs:
            kwargs['variant'] = self.create_test_variant()
        kwargs.setdefault('name', 'England')
        nation = models.Nation(**kwargs)
        if save:
            nation.save()
        return nation

    def create_test_game(self, save=True, **kwargs):
        if 'variant' not in kwargs:
            kwargs['variant'] = self.create_test_variant()
        if 'created_by' not in kwargs:
            kwargs['created_by'] = self.create_test_user()
        kwargs.setdefault('name', 'Test game')
        kwargs.setdefault('num_players', 7)
        game = models.Game(**kwargs)
        if save:
            game.save()
        return game

    def create_test_turn(self, save=True, **kwargs):
        if 'game' not in kwargs:
            kwargs['game'] = self.create_test_game()
        kwargs.setdefault('season', base.Season.SPRING)
        kwargs.setdefault('phase', base.Phase.ORDER)
        kwargs.setdefault('year', 1900)
        kwargs.setdefault('current_turn', True)
        turn = models.Turn(**kwargs)
        if save:
            turn.save()
        return turn

    def create_test_territory(self, save=True, **kwargs):
        if 'variant' not in kwargs:
            kwargs['variant'] = self.create_test_variant()
        kwargs.setdefault('name', 'Belgium')
        kwargs.setdefault('controlled_by_initial', None)
        kwargs.setdefault('nationality', None)
        kwargs.setdefault('type', base.TerritoryType.COASTAL)
        kwargs.setdefault('supply_center', True)
        kwargs.setdefault('initial_piece_type', None)
        territory = models.Territory(**kwargs)
        if save:
            territory.save()
        return territory

    def create_test_piece(self, save=True, **kwargs):
        if 'game' not in kwargs:
            kwargs['game'] = self.create_test_game()
        if 'nation' not in kwargs:
            kwargs['nation'] = self.create_test_nation()
        kwargs.setdefault('type', base.PieceType.ARMY)
        kwargs.setdefault('turn_created', None)
        kwargs.setdefault('turn_disbanded', None)
        piece = models.Piece(**kwargs)
        if save:
            piece.save()
        return piece

    def create_test_piece_state(self, save=True, **kwargs):
        if 'piece' not in kwargs:
            kwargs['piece'] = self.create_test_piece()
        if 'territory' not in kwargs:
            kwargs['territory'] = self.create_test_territory()
        if 'turn' not in kwargs:
            kwargs['turn'] = self.create_test_turn()
        kwargs.setdefault('named_coast', None)
        kwargs.setdefault('dislodged', False)
        kwargs.setdefault('dislodged_by', None)
        kwargs.setdefault('destroyed', False)
        kwargs.setdefault('destroyed_message', None)
        kwargs.setdefault('must_retreat', False)
        kwargs.setdefault('attacker_territory', None)
        piece_state = models.PieceState(**kwargs)
        if save:
            piece_state.save()
        return piece_state

    def create_test_nation_state(self, save=True, **kwargs):
        if 'nation' not in kwargs:
            kwargs['nation'] = self.create_test_nation()
        if 'user' not in kwargs:
            kwargs['user'] = self.create_test_user()
        if 'turn' not in kwargs:
            kwargs['turn'] = self.create_test_turn()
        kwargs.setdefault('orders_finalized', False)
        kwargs.setdefault('surrendered', False)
        nation_state = models.NationState(**kwargs)
        if save:
            nation_state.save()
        return nation_state

    def create_test_territory_state(self, save=True, **kwargs):
        if 'territory' not in kwargs:
            kwargs['territory'] = self.create_test_territory()
        if 'turn' not in kwargs:
            kwargs['turn'] = self.create_test_turn()
        kwargs.setdefault('controlled_by', None)
        kwargs.setdefault('contested', False)
        kwargs.setdefault('bounce_occurred', False)
        territory_state = models.TerritoryState(**kwargs)
        if save:
            territory_state.save()
        return territory_state
