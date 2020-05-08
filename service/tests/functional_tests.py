import json
import os

from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core import factories, models
from service.utils import text_to_order_data


WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
data_folder = WORKING_DIRECTORY + '/order_histories/'


class TestEndToEnd(APITestCase):

    def setUp(self):
        game_dir = 'game_1/'
        file_to_open = data_folder + game_dir + 'spring_1900.txt'
        with open(file_to_open) as f:
            text = f.read()
        jason = text_to_order_data(text)
        self.order_data = json.loads(jason)

    def test_end_to_end(self):
        pass