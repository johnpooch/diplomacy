from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core import factories, models
from core.models.base import GameStatus, NationChoiceMode, OrderType, Phase, Season
from service import serializers


class TestCreateOrder(APITestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.client.force_authenticate(user=self.user)

        self.game = factories.GameFactory(status=GameStatus.ACTIVE)
        self.game.participants.add(self.user)

        nation_state = factories.NationStateFactory(
            turn=self.game.get_current_turn(),
            user=self.user,
        )
        territory_state = factories.TerritoryStateFactory(
            turn=self.game.get_current_turn(),
            controlled_by=nation_state.nation,
        )
        self.territory = territory_state.territory
        self.data = {
            'source': self.territory.id,
        }
        self.url = reverse('create-order', args=[self.game.id])

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

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('User is not a participant in this game.' in
                        response.data['errors']['data'])

    def test_create_order_game_pending(self):
        self.game.status = GameStatus.PENDING
        self.game.save()

        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            'Game is not active.' in response.data['errors']['data']
        )

    def test_create_order_game_ended(self):
        self.game.status = GameStatus.ENDED
        self.game.save()

        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_no_orders_left(self):

        self.territory.supply_center = False
        self.territory.save()
        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            'Nation has no more orders to submit.' in
            response.data['errors']['data']
        )

    def test_create_order_valid(self):
        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(models.Order.objects.get())  # object created

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

    def test_create_build_during_order(self):
        self.data['type'] = OrderType.BUILD
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_active_includes_active_excludes_pending_and_ended(self):
        """
        Includes all active games. Excludes pending and ended games.
        """
        included_games = [
            factories.GameFactory(status=GameStatus.ACTIVE),
        ]

        excluded_games = [  # noqa: F841
            factories.GameFactory(status=GameStatus.PENDING),
            factories.GameFactory(status=GameStatus.ENDED),
        ]

        url = reverse('games-by-type', args=[GameStatus.ACTIVE])
        response = self.client.get(url, format='json')

        expected_data = [serializers.GameSerializer(game).data for game in included_games]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_get_active_games_if_unauthenticated(self):
        """
        Cannot get active games if not authenticated.
        """
        self.client.logout()
        url = reverse('games-by-type', args=[GameStatus.ACTIVE])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ended_includes_ended_and_excludes_pending_and_active(self):
        """
        Gets all games that have ended. Excludes active and pending games.
        """
        included_games = [
            factories.GameFactory(status=GameStatus.ENDED),
        ]

        excluded_games = [  # noqa: F841
            factories.GameFactory(status=GameStatus.PENDING),
            factories.GameFactory(status=GameStatus.ACTIVE),
        ]

        url = reverse('games-by-type', args=[GameStatus.ENDED])
        response = self.client.get(url, format='json')

        expected_data = [serializers.GameSerializer(game).data for game in included_games]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_get_ended_games_if_unauthenticated(self):
        """
        Cannot get ended games if not authenticated.
        """
        self.client.logout()
        url = reverse('games-by-type', args=[GameStatus.ENDED])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_get_joinable_games_if_unauthenticated(self):
        """
        Cannot get ended games if not authenticated.
        """
        url = reverse('games-by-type', args=['joinable'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestGetCreateGame(APITestCase):

    def test_get_create_game_form(self):
        """
        Get create game returns a form.
        """
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)

        url = reverse('create-game')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            '<form action="/api/v1/games/create" method="POST">'
        )

    def test_get_create_game_unauthenticated(self):
        """
        Cannot get create game when unauthenticated.
        """
        url = reverse('create-game')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestPostCreateGame(APITestCase):

    def test_post_invalid_game(self):
        """
        Posting invalid game data causes a 400 error and appropriate messages
        appear on invalid fields.
        """
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)

        data = {'name': 'Test Game'}
        url = reverse('create-game')
        response = self.client.post(url, data, format='json')

        self.assertContains(
            response,
            '<span class="help-block">This field is required.</span>',
            status_code=400,
        )

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
            'variant_id': variant.id,
            'num_players': 7,
        }
        url = reverse('create-game')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, '/api/v1/games/mygames')
        self.assertTrue(models.Game.objects.get(
            name='Test Game',
            created_by=user,
            variant=variant,
            participants=user,
        ))

    def test_post_unauthorized(self):
        """
        Cannot post when unauthorized.
        """
        url = reverse('create-game')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestJoinGame(APITestCase):

    def test_join_game_valid_no_password_no_country_choice(self):
        """
        To join a game with no password and no country requires no post data.
        The user is added as a participant of the game.
        """
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)
        game = factories.GameFactory()

        url = reverse('join-game', args=[game.id])
        data = {}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, '/api/v1/games/mygames')
        game.refresh_from_db()
        self.assertTrue(user in game.participants.all())

    def test_join_game_unauthorized(self):
        """
        Cannot join a game when unauthorized.
        """
        game = factories.GameFactory()
        url = reverse('join-game', args=[game.id])
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_join_game_correct_password(self):
        """
        Posting correct password adds user correctly.
        """
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)
        game = factories.GameFactory(private=True, password='testpass')

        url = reverse('join-game', args=[game.id])
        data = {'password': 'testpass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        game.refresh_from_db()
        self.assertTrue(user in game.participants.all())

    def test_join_game_wrong_password(self):
        """
        Posting incorrect password causes bad request.
        """
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)
        game = factories.GameFactory(private=True, password='testpass')

        url = reverse('join-game', args=[game.id])
        data = {'password': 'wrongpass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['errors'],
            {'password': ['Incorrect password.']}
        )

    def test_join_game_valid_nation_choice(self):
        """
        Posting valid nation choice causes the user to be added correctly
        """
        user = factories.UserFactory()
        game = factories.GameFactory(
            nation_choice_mode=NationChoiceMode.FIRST_COME
        )
        nation = factories.NationFactory()
        self.client.force_authenticate(user=user)

        url = reverse('join-game', args=[game.id])
        data = {'nation_id': nation.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        game.refresh_from_db()
        self.assertTrue(user in game.participants.all())

    def test_join_game_invalid_nation_choice(self):
        """
        Posting invalid nation choice causes bad request.
        """
        user = factories.UserFactory()
        game = factories.GameFactory(
            nation_choice_mode=NationChoiceMode.FIRST_COME
        )
        factories.NationFactory()

        self.client.force_authenticate(user=user)

        url = reverse('join-game', args=[game.id])
        data = {'nation_id': 300}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['errors'],
            {'nation_id': ['Invalid nation selected.']}
        )

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
        data = {}
        response = self.client.post(url, data, format='json')
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
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['errors'],
            {'status': ['Cannot join game.']}
        )


class TestGetGameState(APITestCase):

    def setUp(self):
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)

    def test_get_game_state_unauthorized(self):
        self.client.logout()
        game = factories.GameFactory(status=GameStatus.ACTIVE)

        url = reverse('game-state', args=[game.id])
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_game_state_live_game(self):
        game = factories.GameFactory(status=GameStatus.ACTIVE)
        url = reverse('game-state', args=[game.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_game_state_pending_game(self):
        game = factories.GameFactory(status=GameStatus.PENDING)
        url = reverse('game-state', args=[game.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_game_state_ended_game(self):
        game = factories.GameFactory(status=GameStatus.ENDED)
        url = reverse('game-state', args=[game.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

