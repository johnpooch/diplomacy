from django import forms
from django.core.exceptions import ValidationError

from core import models
from core.models.base import NationChoiceMode


class JoinGameForm(forms.Form):
    """
    Used in `views.JoinGame`. Validates data for joining a game.
    """
    # TODO test
    def __init__(self, game, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.game = game

        if self.game.private:
            self.fields['password'] = forms.CharField()

        if self.game.nation_choice_mode == NationChoiceMode.FIRST_COME:
            self.fields['nation_id'] = forms.IntegerField()

    def clean_password(self):
        """
        Ensure that password matches the game password
        """
        password = self.cleaned_data['password']
        if not password == self.game.password:
            raise ValidationError('Incorrect password.')
        return password

    def clean_nation_id(self):
        """
        Convert integer into `Nation` instance. Raise a validation error if
        the integer is not the ID of an available `Nation` instance.
        """
        nation_id = self.cleaned_data['nation_id']
        try:
            nation = models.Nation.objects.get(id=nation_id)
            # TODO choosing already chosen nation should cause ValidationError.
            self.cleaned_data['nation_id'] = nation
        except models.Nation.DoesNotExist:
            raise ValidationError('Invalid nation selected.')
        return nation_id
