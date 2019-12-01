from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core import factories
from core import models
from core.models.base import GameStatus, NationChoiceMode
from service.serializers import GameSerializer


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

    def test_get(self):
        url = reverse('create-order', args=[self.game.id])
        response = self.client.get(url, self.data, format='json')
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_create_order_unauthorized(self):
        self.client.logout()

        url = reverse('create-order', args=[self.game.id])
        response = self.client.post(url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_not_participant(self):
        self.game.participants.remove(self.user)

        url = reverse('create-order', args=[self.game.id])
        response = self.client.post(url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('User is not a participant in this game.' in
                        response.data['errors']['data'])

    def test_create_order_game_pending(self):
        self.game.status = GameStatus.PENDING
        self.game.save()

        url = reverse('create-order', args=[self.game.id])
        response = self.client.post(url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            'Game is not active.' in response.data['errors']['data']
        )

    def test_create_order_game_ended(self):
        self.game.status = GameStatus.ENDED
        self.game.save()

        url = reverse('create-order', args=[self.game.id])
        response = self.client.post(url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_no_orders_left(self):

        self.territory.supply_center = False
        self.territory.save()
        url = reverse('create-order', args=[self.game.id])

        response = self.client.post(url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            'Nation has no more orders to submit.' in
            response.data['errors']['data']
        )

    def test_create_order_valid(self):

        url = reverse('create-order', args=[self.game.id])
        response = self.client.post(url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(models.Order.objects.get())  # object created
