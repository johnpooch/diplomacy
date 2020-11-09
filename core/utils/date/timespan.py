from django.utils import timezone


__all__ = [
    'get_timespan',
    'timespans',
]


class TimeSpan:
    db_string = None
    display_string = None

    def __str__(self):
        return self.display_string

    @property
    def as_choice(self):
        return (self.db_string, self.display_string)

    @property
    def timedelta(self):
        raise NotImplementedError()


class TwelveHours(TimeSpan):
    db_string = 'twelve_hours'
    display_string = '12 hours'

    @property
    def timedelta(self):
        return timezone.timedelta(hours=12)


class TwentyFourHours(TimeSpan):
    db_string = 'twenty_four_hours'
    display_string = '24 hours'

    @property
    def timedelta(self):
        return timezone.timedelta(days=1)


class TwoDays(TimeSpan):
    db_string = 'two_days'
    display_string = '2 days'

    @property
    def timedelta(self):
        return timezone.timedelta(days=2)


class ThreeDays(TimeSpan):
    db_string = 'three_days'
    display_string = '3 days'

    @property
    def timedelta(self):
        return timezone.timedelta(days=3)


class FiveDays(TimeSpan):
    db_string = 'five_days'
    display_string = '5 days'

    @property
    def timedelta(self):
        return timezone.timedelta(days=5)


class SevenDays(TimeSpan):
    db_string = 'seven_days'
    display_string = '7 days'

    @property
    def timedelta(self):
        return timezone.timedelta(days=7)


class TimeSpans:
    TWELVE_HOURS = TwelveHours()
    TWENTY_FOUR_HOURS = TwentyFourHours()
    TWO_DAYS = TwoDays()
    THREE_DAYS = ThreeDays()
    FIVE_DAYS = FiveDays()
    SEVEN_DAYS = SevenDays()

    def as_list(self):
        return [
            self.TWELVE_HOURS,
            self.TWENTY_FOUR_HOURS,
            self.TWO_DAYS,
            self.THREE_DAYS,
            self.FIVE_DAYS,
            self.SEVEN_DAYS,
        ]


timespans = TimeSpans()


def get_timespan(db_string):
    for timespan in timespans.as_list():
        if timespan.db_string == db_string:
            return timespan
    raise ValueError(
        '{} is not a recognized timezone. Must be one of the following: {}'
        .format(
            db_string,
            ', '.join([ts.db_string for ts in timespans.as_list()])
        )
    )
