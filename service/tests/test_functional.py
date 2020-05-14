from copy import copy
import json
from unittest import mock
import os


from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from core import models
from core.models import base
from service.utils import text_to_order_data


WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
data_folder = WORKING_DIRECTORY + '/order_histories/'


def reverse_list(l):
    return l.reverse()


class TestEndToEnd(APITestCase):

    fixtures = [
        'prod/standard/variant',
        'prod/standard/nation',
        'prod/standard/territory',
        'prod/standard/named_coast',
    ]

    def setUp(self):
        game_dir = 'game_1/'
        file_to_open = data_folder + game_dir + 'spring_1900.txt'
        with open(file_to_open) as f:
            text = f.read()
        jason = text_to_order_data(text)
        self.order_data = json.loads(jason)

    def test_end_to_end(self):
        register_url = reverse('register')
        create_game_url = reverse('create-game')
        # No users
        self.assertEqual(User.objects.count(), 0)
        # Users sign up
        users = ['maria', 'john', 'sam', 'niall', 'hugh', 'oisin', 'chris']
        for user in users:
            data = {'username': user, 'email': f'{user}@{user}.com', 'password': user}
            response = self.client.post(register_url, data, format='json')
            self.assertEqual(response.status_code, 200)
            User.objects.get(username=user)  # created

        self.assertEqual(User.objects.count(), 7)

        # No games exist
        self.assertEqual(models.Game.objects.count(), 0)
        # One user creates a game
        data = {'name': 'New Game', 'description': 'Game description'}
        john = User.objects.get(username='john')
        self.client.force_authenticate(user=john)
        response = self.client.post(create_game_url, data, format='json')
        self.assertEqual(response.status_code, 200)

        game = models.Game.objects.get()
        # john automatically added as participant
        self.assertTrue(john in game.participants.all())
        self.assertEqual(game.status, base.GameStatus.PENDING)
        self.assertEqual(game.created_by, john)
        self.assertEqual(game.initialized_at, None)
        self.assertEqual(game.variant, models.Variant.objects.get(name='Standard'))

        # john tries to create order before game has started
        data = {'source': 1}
        create_order_url = reverse('create-order', args=[game.id])
        response = self.client.post(create_order_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual('Game is not active.', str(response.data[0]))

        # each player joins game
        join_game_url = reverse('join-game', args=[game.id])
        other_users = User.objects.exclude(username='john')
        for user in other_users:
            self.client.force_authenticate(user=user)
            with mock.patch('random.shuffle', reverse_list):
                response = self.client.get(join_game_url, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(user in game.participants.all())
            participation = models.Participation.objects.get(user=user, game=game)
            self.assertTrue(participation.joined_at)

        turn = game.get_current_turn()

        nation_states = \
            models.NationState.objects.filter(turn=turn)

        # game is now active and has been initialised
        game.refresh_from_db()
        self.assertEqual(game.status, base.GameStatus.ACTIVE)

        # each player has been assigned a nation
        for user in users:
            self.assertEqual(
                len([n for n in nation_states if n.user.username == user]),
                1
            )

        # eighth player signs up
        data = {'username': 'mark', 'email': f'mark@mark.com', 'password': 'mark'}
        response = self.client.post(register_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        new_user = User.objects.get(username='mark')

        # eighth player tries to join game
        self.client.force_authenticate(user=new_user)
        response = self.client.get(join_game_url, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(new_user in game.participants.all())

        # each player submits orders
        for nation_state in nation_states:
            orders = [o for o in self.order_data
                      if o['order']['nation'] == nation_state.nation.name]
            cleaned_orders = []
            for order in orders:
                order_data = copy(order['order'])
                source = order_data.get('source')
                target = order_data.get('target')
                if source:
                    order_data['source'] = models.Territory.objects.get(name=source).id
                if target:
                    order_data['target'] = models.Territory.objects.get(name=target).id
                order_data.pop('nation')
                cleaned_orders.append(order_data)

            self.client.force_authenticate(user=nation_state.user)
            for order in cleaned_orders:
                response = self.client.post(
                    create_order_url,
                    order,
                    format='json',
                )
                self.assertEqual(response.status_code, 201)

        self.assertEqual(models.Order.objects.count(), 22)
        orders = models.Order.objects.all()

        for order in orders:
            self.assertEqual(order.outcome, None)

        finalize_orders_url = reverse('finalize-orders', args=[game.id])
        # each player finalizes orders
        for user in game.participants.all():
            self.client.force_authenticate(user=user)
            response = self.client.get(finalize_orders_url)
            self.assertEqual(response.status_code, 200)

        # turn is processed
        turn.refresh_from_db()
        self.assertTrue(turn.processed)
        self.assertTrue(turn.processed_at)
        self.assertFalse(turn.current_turn)

        # orders have outcomes
        orders = turn.orders.all()
        for order in orders:
            self.assertTrue(order.outcome)

        # new turn
        new_turn = game.get_current_turn()
        self.assertEqual(new_turn.year, 1900)
        self.assertEqual(new_turn.season, base.Season.FALL)
        self.assertEqual(new_turn.phase, base.Phase.ORDER)

        # check piece positions are correct
