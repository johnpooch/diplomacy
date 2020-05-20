from unittest import mock, skip
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core import factories, models
from core.models.base import GameStatus, OrderType, Phase, PieceType, Season
from service import serializers, views


def set_processed(self):
    self.processed = True
    self.save()


class TestGetGames(APITestCase):

    def setUp(self):
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)

    def test_get_all_games(self):
        """
        Gets all games including pending, active, and ended games.
        """
        games = [
            factories.GameFactory(status=GameStatus.PENDING),
            factories.GameFactory(status=GameStatus.ACTIVE),
            factories.GameFactory(status=GameStatus.ENDED),
        ]

        url = reverse('all-games')
        response = self.client.get(url, format='json')

        expected_data = [serializers.GameSerializer(game).data for game in games]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_get_all_games_unauthenticated(self):
        """
        Cannot get all games if not authenticated.
        """
        self.client.logout()
        url = reverse('all-games')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestJoinableGames(APITestCase):

    def test_joinable_gets_games_that_need_participants(self):
        """
        Gets all games that have fewer participants than the num players of the
        game. Excludes ended games. Excludes games where the user is already a
        participant.
        """
        credentials = {'username': 'This User', 'password': 'This Password'}
        user = factories.UserFactory(**credentials)
        self.client.force_authenticate(user=user)

        other_user = factories.UserFactory()
        included_games = [
            factories.GameFactory(),
        ]

        excluded_games = [  # noqa: F841
            factories.GameFactory.create(participants=(other_user,), num_players=1),
            factories.GameFactory.create(participants=(user,)),
            factories.GameFactory(status=GameStatus.ENDED),
        ]

        url = reverse('games-by-type', args=['joinable'])
        response = self.client.get(url, format='json')

        expected_data = [serializers.GameSerializer(game).data for game in included_games]
        not_expected_data = [serializers.GameSerializer(game).data for game in excluded_games]
        for item in expected_data:
            self.assertTrue(item in response.data)
        for item in not_expected_data:
            self.assertFalse(item in response.data)

    def test_get_joinable_games_if_unauthenticated(self):
        """
        Cannot get ended games if not authenticated.
        """
        url = reverse('games-by-type', args=['joinable'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestGetMyGames(APITestCase):

    def test_get_my_games_includes_user_participant_games(self):
        """
        Gets all games that the user is participating in, including pending,
        active, and ended games.
        """
        credentials = {'username': 'This User', 'password': 'This Password'}
        user = factories.UserFactory(**credentials)
        self.client.force_authenticate(user=user)

        included_games = [
            factories.GameFactory.create(
                participants=(user,),
                status=GameStatus.PENDING,
            ),
            factories.GameFactory.create(
                participants=(user,),
                status=GameStatus.ACTIVE,
            ),
            factories.GameFactory.create(
                participants=(user,),
                status=GameStatus.ENDED,
            ),
        ]

        excluded_games = [  # noqa: F841
            factories.GameFactory(),
        ]

        url = reverse('user-games')
        response = self.client.get(url, format='json')

        expected_data = [serializers.GameSerializer(game).data for game in included_games]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_get_my_active_games(self):
        """
        Gets all games that the user is participating in which are active.
        """
        credentials = {'username': 'This User', 'password': 'This Password'}
        user = factories.UserFactory(**credentials)
        self.client.force_authenticate(user=user)

        included_games = [
            factories.GameFactory.create(
                participants=(user,),
                status=GameStatus.ACTIVE,
            ),
        ]

        excluded_games = [  # noqa: F841
            factories.GameFactory.create(
                participants=(user,),
                status=GameStatus.PENDING,
            ),
            factories.GameFactory.create(
                participants=(user,),
                status=GameStatus.ENDED,
            ),
            factories.GameFactory(),
        ]

        url = reverse('user-games-by-type', args=[GameStatus.ACTIVE])
        response = self.client.get(url, format='json')

        expected_data = [serializers.GameSerializer(game).data for game in included_games]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_get_my_games_if_unauthenticated(self):
        """
        Cannot get my games if not authenticated.
        """
        url = reverse('user-games')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestGetCreateGame(APITestCase):

    def test_get_create_game(self):
        """
        Get create game returns a form.
        """
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)

        url = reverse('create-game')
        response = self.client.get(url, format='json')
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_get_create_game_unauthenticated(self):
        """
        Cannot get create game when unauthenticated.
        """
        url = reverse('create-game')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPostCreateGame(APITestCase):

    def test_post_invalid_game(self):
        """
        Posting invalid game data causes a 400 error.
        """
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)

        data = {}
        url = reverse('create-game')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_post_valid_game(self):
        """
        Posting valid game data creates a game instance and redirects to
        `user-games` view. The user is automatically added as a participant of
        the game.
        """
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)
        variant = factories.VariantFactory()

        data = {
            'name': 'Test Game',
        }
        url = reverse('create-game')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            models.Game.objects.get(
                name='Test Game',
                created_by=user,
                variant=variant,
                participants=user,
            )
        )

    def test_post_unauthorized(self):
        """
        Cannot post when unauthorized.
        """
        url = reverse('create-game')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestJoinGame(APITestCase):

    def test_join_game_unauthorized(self):
        """
        Cannot join a game when unauthorized.
        """
        game = factories.GameFactory()
        url = reverse('join-game', args=[game.id])
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_join_game_full(self):
        """
        Cannot join a game when the game already has enough participants.
        """
        joined_user = factories.UserFactory()
        joining_user = factories.UserFactory()
        game = factories.GameFactory(
            participants=(joined_user,),
            num_players=1,
        )

        self.client.force_authenticate(user=joining_user)

        url = reverse('join-game', args=[game.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['errors'],
            {'status': ['Cannot join game.']}
        )

    def test_join_game_ended(self):
        """
        Cannot join a game when the game already has ended.
        """
        user = factories.UserFactory()
        game = factories.GameFactory(
            status=GameStatus.ENDED,
        )
        self.client.force_authenticate(user=user)

        url = reverse('join-game', args=[game.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['errors'],
            {'status': ['Cannot join game.']}
        )

    def test_join_game_success(self):

        user = factories.UserFactory()
        game = factories.GameFactory(
            status=GameStatus.ACTIVE,
        )

        self.client.force_authenticate(user=user)

        url = reverse('join-game', args=[game.id])
        response = self.client.get(url, format='json')
        self.assertTrue(user in game.participants.all())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('core.models.Game.initialize')
    def test_join_game_initialise_game(self, mock_initialize):
        user = factories.UserFactory()
        variant = models.Variant.objects.create(name='standard')
        game = models.Game.objects.create(
            variant=variant,
            name='Test game',
            status=GameStatus.ACTIVE,
            num_players=1,
            created_by=user,
        )
        self.client.force_authenticate(user=user)

        url = reverse('join-game', args=[game.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_initialize.assert_called()


class TestGetGameState(APITestCase):

    def setUp(self):
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)

    def test_get_game_state_unauthorized(self):
        self.client.logout()
        game = factories.GameFactory(status=GameStatus.ACTIVE)

        url = reverse('game-state', args=[game.id])
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_game_state_live_game(self):
        game = factories.GameFactory(status=GameStatus.ACTIVE)
        url = reverse('game-state', args=[game.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_game_state_pending_game(self):
        game = factories.GameFactory(status=GameStatus.PENDING)
        url = reverse('game-state', args=[game.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_game_state_ended_game(self):
        game = factories.GameFactory(status=GameStatus.ENDED)
        url = reverse('game-state', args=[game.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestCreateOrder(APITestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.client.force_authenticate(user=self.user)

        self.variant = factories.VariantFactory()
        self.game = models.Game.objects.create(
            status=GameStatus.ACTIVE,
            variant=self.variant,
            name='Test Game',
            created_by=self.user,
            num_players=7
        )
        self.game.participants.add(self.user)
        self.turn = models.Turn.objects.create(
            game=self.game,
            year=1901,
            phase=Phase.ORDER,
            season=Season.SPRING,
        )
        self.nation = models.Nation.objects.create(
            variant=self.variant,
            name='Test Nation',
        )
        self.nation_state = models.NationState.objects.create(
            nation=self.nation,
            turn=self.turn,
            user=self.user,
        )
        self.territory = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
            nationality=self.nation,
            supply_center=True,
        )
        self.territory_state = models.TerritoryState.objects.create(
            territory=self.territory,
            turn=self.turn,
            controlled_by=self.nation_state.nation,
        )
        self.territory = self.territory_state.territory
        self.piece = models.Piece.objects.create(
            game=self.game,
            nation=self.nation_state.nation,
            type=PieceType.ARMY,
        )
        self.piece_state = models.PieceState.objects.create(
            turn=self.turn,
            piece=self.piece,
            territory=self.territory,
        )
        self.data = {
            'source': self.territory.id,
        }
        self.url = reverse('order', args=[self.game.id])

    def test_get(self):
        response = self.client.get(self.url, self.data, format='json')
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_create_order_unauthorized(self):
        self.client.logout()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_not_participant(self):
        self.game.participants.remove(self.user)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            'User is not a participant in this game.',
            str(response.data[0])
        )

    def test_create_order_game_pending(self):
        self.game.status = GameStatus.PENDING
        self.game.save()

        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('Game is not active.', str(response.data[0]))

    def test_create_order_game_ended(self):
        self.game.status = GameStatus.ENDED
        self.game.save()

        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @skip
    def test_create_order_no_orders_left(self):
        models.Order.objects.create(
            nation=self.nation_state.nation,
            turn=self.turn,
            source=self.territory
        )
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            'Nation has no more orders to submit.',
            str(response.data[0])
        )

    def test_create_order_no_orders_left_retreat_and_disband(self):
        models.Turn.objects.create(
            game=self.game,
            season=Season.SPRING,
            phase=Phase.RETREAT_AND_DISBAND,
            year=1900,
            current_turn=True,
        )
        nation_state = factories.NationStateFactory(
            turn=self.game.get_current_turn(),
            user=self.user,
        )
        territory_state = factories.TerritoryStateFactory(
            turn=self.game.get_current_turn(),
            controlled_by=nation_state.nation,
        )
        models.PieceState.objects.all().delete()
        territory = territory_state.territory
        self.data = {
            'source': self.territory.id,
            'target': territory.id,
            'type': OrderType.RETREAT,
        }
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_valid(self):

        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(models.Order.objects.get())  # object created

    @skip
    def test_create_order_valid_over_writes(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(models.Order.objects.get())  # object created

        territory_state = factories.TerritoryStateFactory(
            turn=self.turn,
            controlled_by=self.nation_state.nation,
        )
        territory = territory_state.territory
        self.data = {
            'source': self.territory.id,
            'target': territory.id,
            'type': OrderType.MOVE,
        }
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = models.Order.objects.get()
        self.assertEqual(order.type, OrderType.MOVE)
        self.assertEqual(order.target, territory)

    def test_create_order_hold_during_retreat(self):
        models.Turn.objects.create(
            game=self.game,
            season=Season.SPRING,
            phase=Phase.RETREAT_AND_DISBAND,
            year=1900,
            current_turn=True,
        )
        nation_state = factories.NationStateFactory(
            turn=self.game.get_current_turn(),
            user=self.user,
        )
        territory_state = factories.TerritoryStateFactory(
            turn=self.game.get_current_turn(),
            controlled_by=nation_state.nation,
        )
        self.territory = territory_state.territory
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_retreat_for_must_retreat_piece(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.SPRING,
            phase=Phase.RETREAT_AND_DISBAND,
            year=1900,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        territory_state = factories.TerritoryStateFactory(
            turn=turn,
            controlled_by=self.nation_state.nation,
        )
        self.piece_state.turn = turn
        self.piece_state.must_retreat = True
        self.piece_state.save()
        territory = territory_state.territory
        self.data = {
            'source': self.territory.id,
            'target': territory.id,
            'type': OrderType.RETREAT,
        }
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_retreat_for_non_must_retreat_piece(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.SPRING,
            phase=Phase.RETREAT_AND_DISBAND,
            year=1900,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        territory_state = factories.TerritoryStateFactory(
            turn=turn,
            controlled_by=self.nation_state.nation,
        )
        self.piece_state.turn = turn
        self.piece_state.save()
        territory = territory_state.territory
        self.data = {
            'source': self.territory.id,
            'target': territory.id,
            'type': OrderType.RETREAT,
        }
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_build_during_order(self):
        self.data['type'] = OrderType.BUILD
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_build_valid(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
            year=1901,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        self.territory_state.turn = turn
        self.territory_state.save()
        models.Piece.objects.all().delete()
        models.PieceState.objects.all().delete()
        self.data = {
            'source': self.territory.id,
            'type': OrderType.BUILD,
            'piece_type': PieceType.ARMY,
        }
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_build_no_builds(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
            year=1901,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        models.Piece.objects.all().delete()
        models.PieceState.objects.all().delete()
        self.data = {
            'source': self.territory.id,
            'type': OrderType.BUILD,
            'piece_type': PieceType.ARMY,
        }
        self.assertEqual(self.nation_state.supply_delta, 0)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_build_with_disbands(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
            year=1901,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        self.piece_state.turn = turn
        self.piece_state.save()
        self.data = {
            'source': self.territory.id,
            'type': OrderType.BUILD,
            'piece_type': PieceType.ARMY,
        }
        self.assertEqual(self.nation_state.supply_delta, -1)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_disband_valid(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
            year=1901,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        self.territory_state.turn = turn
        self.territory_state.territory.supply_center = False
        self.territory_state.territory.save()
        self.territory_state.save()
        self.piece_state.turn = turn
        self.piece_state.save()
        self.data = {
            'source': self.piece_state.territory.id,
            'type': OrderType.DISBAND,
        }
        self.assertEqual(self.nation_state.supply_delta, -1)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_disband_no_disbands(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
            year=1901,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        self.territory_state.turn = turn
        self.territory_state.territory.save()
        self.territory_state.save()
        self.piece_state.turn = turn
        self.piece_state.save()
        self.data = {
            'source': self.piece_state.territory.id,
            'type': OrderType.DISBAND,
        }
        self.assertEqual(self.nation_state.supply_delta, 0)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_too_many_disbands(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
            year=1901,
            current_turn=True,
        )
        territory = models.Territory.objects.create(
            variant=self.variant,
            nationality=self.nation,
            name='Picardy',
        )
        models.TerritoryState.objects.create(
            territory=territory,
            turn=turn,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        self.territory_state.turn = turn
        self.territory_state.territory.supply_center = False
        self.territory_state.territory.save()
        self.territory_state.save()
        self.piece_state.turn = turn
        self.piece_state.save()
        self.assertEqual(self.nation_state.supply_delta, -1)
        self.assertEqual(self.nation_state.num_orders_remaining, 1)
        data = {
            'source': self.piece_state.territory.id,
            'type': OrderType.DISBAND,
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.nation_state.num_orders_remaining, 0)
        data = {
            'source': territory.id,
            'type': OrderType.DISBAND,
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(
            'Cannot issue any more disband orders.',
            str(response.data[0])
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_build_occupied_territory(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
            year=1901,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        self.territory_state.turn = turn
        self.territory_state.save()
        models.PieceState.objects.create(
            piece=self.piece,
            turn=turn,
            territory=self.territory,
        )
        territory = models.Territory.objects.create(
            variant=self.variant,
            nationality=self.nation,
            name='Picardy',
            supply_center=True,
        )
        models.TerritoryState.objects.create(
            territory=territory,
            controlled_by=self.nation,
            turn=turn,
        )
        self.data = {
            'source': self.territory.id,
            'type': OrderType.BUILD,
            'piece_type': PieceType.ARMY,
        }
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestDeleteOrder(APITestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.client.force_authenticate(user=self.user)

        self.variant = factories.VariantFactory()
        self.game = models.Game.objects.create(
            status=GameStatus.ACTIVE,
            variant=self.variant,
            name='Test Game',
            created_by=self.user,
            num_players=7
        )
        self.game.participants.add(self.user)
        self.turn = models.Turn.objects.create(
            game=self.game,
            year=1901,
            phase=Phase.ORDER,
            season=Season.SPRING,
        )
        self.nation = models.Nation.objects.create(
            variant=self.variant,
            name='Test Nation',
        )
        self.nation_state = models.NationState.objects.create(
            nation=self.nation,
            turn=self.turn,
            user=self.user,
        )
        self.territory = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
            nationality=self.nation,
            supply_center=True,
        )
        self.territory_state = models.TerritoryState.objects.create(
            territory=self.territory,
            turn=self.turn,
            controlled_by=self.nation_state.nation,
        )
        self.territory = self.territory_state.territory
        self.piece = models.Piece.objects.create(
            game=self.game,
            nation=self.nation_state.nation,
            type=PieceType.ARMY,
        )
        self.piece_state = models.PieceState.objects.create(
            turn=self.turn,
            piece=self.piece,
            territory=self.territory,
        )

    def test_delete_order_valid(self):
        order = models.Order.objects.create(
            turn=self.turn,
            source=self.territory,
            nation=self.nation
        )
        url = reverse('order', args=[self.game.id, order.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(models.Order.DoesNotExist):
            self.assertTrue(models.Order.objects.get())

    def test_delete_order_no_order(self):
        url = reverse('order', args=[self.game.id, 1])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_other_players_order(self):
        order = models.Order.objects.create(
            turn=self.turn,
            source=self.territory,
            nation=self.nation
        )
        other_user = factories.UserFactory()
        self.game.participants.add(other_user)
        self.client.force_authenticate(user=other_user)
        nation = models.Nation.objects.create(
            variant=self.variant,
            name='Test Nation',
        )
        models.NationState.objects.create(
            nation=nation,
            turn=self.turn,
            user=other_user,
        )
        url = reverse('order', args=[self.game.id, order.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(models.Order.objects.get())


class TestFinalizeOrders(APITestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.game = factories.GameFactory(status=GameStatus.ACTIVE)
        self.game.participants.add(self.user)
        self.turn = self.game.get_current_turn()
        self.nation_state = factories.NationStateFactory(
            turn=self.turn,
            user=self.user,
        )
        territory_state = factories.TerritoryStateFactory(
            turn=self.turn,
            controlled_by=self.nation_state.nation,
        )
        self.territory = territory_state.territory
        self.url = reverse('finalize-orders', args=[self.game.id])

    def test_finalize_when_not_participant(self):
        self.game.participants.all().delete()
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_finalize_when_game_not_active(self):
        self.client.force_authenticate(user=self.user)
        self.game.status = GameStatus.PENDING
        self.game.save()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_finalize_orders_with_no_orders(self):
        self.client.force_authenticate(user=self.user)
        with mock.patch('core.models.Turn.process', set_processed):
            response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.nation_state.refresh_from_db()
        self.assertTrue(self.nation_state.orders_finalized)

    def test_can_finalize_orders_with_orders(self):
        self.client.force_authenticate(user=self.user)
        models.Order.objects.create(
            turn=self.game.get_current_turn(),
            nation=self.nation_state.nation,
            source=self.territory
        )
        with mock.patch('core.models.Turn.process', set_processed):
            response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.nation_state.refresh_from_db()
        self.assertTrue(self.nation_state.orders_finalized)

    def test_once_all_orders_finalized_turn_advances(self):
        self.client.force_authenticate(user=self.user)
        turn = self.game.get_current_turn()
        turn.nationstates.set([self.nation_state])
        with mock.patch('core.models.Turn.process', set_processed):
            response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.nation_state.refresh_from_db()
        self.assertTrue(self.nation_state.orders_finalized)


class TestUnfinalizeOrders(APITestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.game = factories.GameFactory(status=GameStatus.ACTIVE)
        self.game.participants.add(self.user)
        self.nation_state = factories.NationStateFactory(
            turn=self.game.get_current_turn(),
            user=self.user,
            orders_finalized=True,
        )
        territory_state = factories.TerritoryStateFactory(
            turn=self.game.get_current_turn(),
            controlled_by=self.nation_state.nation,
        )
        self.territory = territory_state.territory
        self.url = reverse('unfinalize-orders', args=[self.game.id])

    def test_unfinalize_when_not_participant(self):
        self.game.participants.all().delete()
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unfinalize_when_game_not_active(self):
        self.client.force_authenticate(user=self.user)
        self.game.status = GameStatus.PENDING
        self.game.save()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_unfinalize_orders_with_no_orders(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.nation_state.refresh_from_db()
        self.assertFalse(self.nation_state.orders_finalized)

    def test_can_unfinalize_orders_with_orders(self):
        self.client.force_authenticate(user=self.user)
        models.Order.objects.create(
            turn=self.game.get_current_turn(),
            nation=self.nation_state.nation,
            source=self.territory
        )
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.nation_state.refresh_from_db()
        self.assertFalse(self.nation_state.orders_finalized)

    def test_if_not_finalized_error(self):
        self.client.force_authenticate(user=self.user)
        self.nation_state.orders_finalized = False
        self.nation_state.save()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
