from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core import factories
from core.models.base import GameStatus
from service.serializers import GameSerializer


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

        expected_data = [GameSerializer(game).data for game in games]
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

        expected_data = [GameSerializer(game).data for game in included_games]
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

        expected_data = [GameSerializer(game).data for game in included_games]
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


class TestGetJoinableGames(APITestCase):

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

        expected_data = [GameSerializer(game).data for game in included_games]
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

        expected_data = [GameSerializer(game).data for game in included_games]
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

        expected_data = [GameSerializer(game).data for game in included_games]
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
    # gets forms
    pass


class TestPostCreateGame(APITestCase):
    # returns x when form invalid (test form separately?)
    pass