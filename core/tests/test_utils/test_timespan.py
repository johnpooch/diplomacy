from django.test import TestCase
from django.utils import timezone

from core.utils.date import get_timespan, timespans


class TestTimespan(TestCase):

    def setUp(self):
        pass

    def test_get_timespan(self):
        pairs = [
            ('twelve_hours', timespans.TWELVE_HOURS),
            ('twenty_four_hours', timespans.TWENTY_FOUR_HOURS),
            ('two_days', timespans.TWO_DAYS),
            ('three_days', timespans.THREE_DAYS),
            ('five_days', timespans.FIVE_DAYS),
            ('seven_days', timespans.SEVEN_DAYS),
        ]
        for db_string, cls in pairs:
            self.assertEqual(get_timespan(db_string), cls)

    def test_get_timespan_invalid(self):
        with self.assertRaises(ValueError):
            get_timespan('bad_string')

    def test_timedelta(self):
        delta = timespans.SEVEN_DAYS.timedelta
        self.assertTrue(isinstance(delta, timezone.timedelta))
        self.assertEqual(delta.days, 7)

    def test_as_choice(self):
        choice = timespans.SEVEN_DAYS.as_choice
        self.assertEqual(choice, ('seven_days', '7 days'))

    def test_str(self):
        self.assertEqual(str(timespans.SEVEN_DAYS), '7 days')
