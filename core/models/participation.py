from django.contrib.auth.models import User
from django.db import models


class Participation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    joined_at = models.DateTimeField(
        auto_now_add=True,
    )
