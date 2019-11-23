from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestActiveGames(APITestCase):

    def test_get_all_active_games_includes_active(self):
        """
        Includes all active games.
        """
        # url = reverse('account-list')
        # data = {'name': 'DabApps'}
        # response = self.client.post(url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(response.data, data)
        pass

    def test_get_all_active_games_excludes_pending(self):
        """
        Excludes pending games.
        """
        pass

    def test_get_all_active_games_excludes_ended(self):
        """
        Excludes ended games.
        """
        pass


class TestGetArchivedGames(APITestCase):

    def test_get_all_archived_games_includes_ended(self):
        """
        Gets all games that have ended.
        """
        pass

    def test_get_all_archived_games_excludes_pending(self):
        """
        Excludes pending games.
        """
        pass

    def test_get_all_archived_games_excludes_active(self):
        """
        Excludes active games.
        """
        pass


class TestGetJoinableGames(APITestCase):

    def test_gets_games_that_need_participants(self):
        """
        Gets all games that have fewer participants than the player capacity of
        the game variant.
        """
        pass

    def test_get_all_archived_games_excludes_pending(self):
        """
        Excludes pending games.
        """
        pass

    def test_get_all_archived_games_excludes_active(self):
        """
        Excludes active games.
        """
        pass


class TestGetMyGames(APITestCase):

    def test_get_my_games_includes_user_participant_games(self):
        """
        Gets all active games that the user is participating in.
        """
        pass

    def test_get_my_active_games_excludes_non_user_participated_games(self):
        """
        Excludes all games that the user is not a participant of.
        """
        pass
