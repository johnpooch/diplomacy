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
    nation = models.ForeignKey(
        'Nation',
        related_name='orders',
        on_delete=models.CASCADE,
        db_column="nation_id",
        null=False,
        db_constraint=False
    )
    turn = models.ForeignKey('Turn', on_delete=models.CASCADE, null=False)
    finalised = models.BooleanField(default=False)

    objects = OrderManager()

    class Meta:
        db_table = "order"
