# Generated by Django 3.1.7 on 2021-04-25 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20210423_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='build_deadline',
            field=models.CharField(choices=[(None, 'None'), ('twelve_hours', '12 hours'), ('twenty_four_hours', '24 hours'), ('two_days', '2 days'), ('three_days', '3 days'), ('five_days', '5 days'), ('seven_days', '7 days')], default='twelve_hours', max_length=100),
        ),
        migrations.AlterField(
            model_name='game',
            name='order_deadline',
            field=models.CharField(choices=[(None, 'None'), ('twelve_hours', '12 hours'), ('twenty_four_hours', '24 hours'), ('two_days', '2 days'), ('three_days', '3 days'), ('five_days', '5 days'), ('seven_days', '7 days')], default='twenty_four_hours', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='retreat_deadline',
            field=models.CharField(choices=[(None, 'None'), ('twelve_hours', '12 hours'), ('twenty_four_hours', '24 hours'), ('two_days', '2 days'), ('three_days', '3 days'), ('five_days', '5 days'), ('seven_days', '7 days')], default='twenty_four_hours', max_length=100),
        ),
    ]
