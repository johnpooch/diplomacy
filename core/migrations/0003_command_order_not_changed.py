# Generated by Django 2.2.5 on 2019-10-26 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20191021_1756'),
    ]

    operations = [
        migrations.AddField(
            model_name='command',
            name='order_not_changed',
            field=models.BooleanField(default=False),
        ),
    ]
