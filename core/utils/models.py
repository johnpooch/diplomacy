from django.utils.text import slugify


def unique_object_slug(obj, source, slug_field='slug', limit=10000):
    """
    Utility for generating unique slugs based on a source string. If the slug
    is already taken it will append a numeric value.
    """
    model = obj.__class__
    base_slug = slugify(source)
    current_slug = base_slug
    search = '%s__startswith' % slug_field
    objects = model.objects.filter(**{search: base_slug})

    for i in range(1, limit):
        o = objects.filter(**{slug_field: current_slug})
        if (len(o) == 0) or (o[0].id == obj.id):
            return current_slug
        current_slug = '%s-%s' % (base_slug, i)

    return False


def super_receiver(signal, base_class, **kwargs):
    """
    A decorator for connecting receivers to signals for multiple senders.
    Works like the django.db.models.signals.receiver decorator, but will
    connect itself to all classes that inherit from the given base_class.

        @super_receiver(post_save, base_class=MyAbstractClass)
        def signal_receiver(sender, **kwargs):
            ...

        @super_receiver([post_save, post_delete], base_class=MyAbstractClass)
        def signals_receiver(sender, **kwargs):
            ...
    """
    def _decorator(func):
        signals = signal if isinstance(signal, (list, tuple)) else (signal,)
        for s in signals:
            for subclass in all_subclasses(base_class):
                s.connect(func, subclass, **kwargs)
        return func

    return _decorator


def all_subclasses(cls):
    """
    Gets all subclasses of a class.
    """
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )
