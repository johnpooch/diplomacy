from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core import factories
from core import models
from core.models.base import GameStatus, NationChoiceMode
from service.serializers import GameSerializer


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
