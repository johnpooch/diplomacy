from core.utils.models import unique_object_slug


class AutoSlug:
    """
    Mixin class that allows you to have a slug field auto-populated from
    another field.

    This class has two properties, which you can override if you like:
    * `autoslug_field` is the name of the slug field that will be
      auto-populated.
    * `autoslug_populate_from` is the name of the field whose value will be
      slugified to produce the slug string. This field should contain strings
      (CharField or similar).

    autoslug_populate_from can also be a function, which will be given the
    current model object as its first argument, and should return a string
    or None.

    Note that the slug field on your model needs to have `blank=True` set on it
    (or an overridden form in admin), otherwise validation errors will prevent
    you from saving.

    Relies on the add_automatic_slug receiver in diplomacy.core.signals to work.
    """
    autoslug_field = 'slug'
    autoslug_populate_from = 'name'

    def hydrate_slug(self):
        """
        Set the slug field (autoslug_field) value from its set source
        (autoslug_populate_from) if the slug field has no value.
        """
        existing = getattr(self, self.autoslug_field)
        if existing and len(existing) > 0:
            return

        source = self._autoslug_source_value()
        if source:
            # Replace ampersand before slugify removes it:
            # e.g. 'Dungeons & Dragons' -> 'dungeons-and-dragons'
            source = source.replace('&', 'and')
            setattr(self, self.autoslug_field, self._slugify(source))

    def _autoslug_source_value(self):
        """
        Return the value that should be used as the source of the slug field
        value.

        Uses the autoslug_populate_from to determine a value.

        Returns:
            `str` or `None`
        """
        if callable(self.autoslug_populate_from):
            source = self.autoslug_populate_from(self)
        else:
            source = getattr(self, self.autoslug_populate_from)
        return source

    def _slugify(self, source):
        return unique_object_slug(self, source)
