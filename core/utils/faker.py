import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker

fake = Faker()


def choice_from_queryset(queryset):
    """
    Pick and return a random item from the given QuerySet.
    """
    count = len(queryset)
    if count == 0:
        return None
    return queryset[random.randint(0, count - 1)]


def recent_date(before=None):
    """
    Generate a random date sometime in the past 7 days.

    If `before` is not given, defaults to current timestamp.
    """
    if not before:
        before = timezone.now()
    return fake.date_time_between_dates(
        datetime_start=before - timedelta(days=7),
        datetime_end=before,
        tzinfo=before.tzinfo,
    )


def word_name():
    """
    Generate a name from random words (rather than a personal name).
    """
    return ' '.join(fake.words(2)).title()


def user():
    """
    Create a user with a unique username and email.
    """
    first_name = fake.first_name()
    last_name = fake.last_name()
    username = (first_name + last_name).lower()
    scrim = 1
    while User.objects.filter(username=username):
        username = username + str(scrim)
        scrim += 1
    return User.objects.create(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=username + '@fake.com',
        password='pass'
    )
