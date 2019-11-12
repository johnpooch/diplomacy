from django.db import models


class OrderManager(models.Manager):

    def get_queryset(self):
        """
        """
        queryset = super().get_queryset()
        # TODO prefetch commands
        return queryset

    def process_orders(self):
        """
        """
        queryset = super().get_queryset()
        for order in queryset.all():
            for command in order.commands.all():
                command.process()


class Order(models.Model):
    """
    """
    # TODO: use signals when all orders are submitted
    # TODO replace with nationstate (and one to one)
    nation_state = models.OneToOneField(
        'NationState',
        null=True,
        on_delete=models.CASCADE,
    )
    finalised = models.BooleanField(
        default=False,
    )

    objects = OrderManager()

    class Meta:
        db_table = "order"
