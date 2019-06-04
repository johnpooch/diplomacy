# Generated by Django 2.1.7 on 2019-05-06 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0009_auto_20190506_2042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phase',
            name='type',
            field=models.CharField(choices=[('O', 'Order'), ('R', 'Retreat and Disband'), ('B', 'Build and Disband')], max_length=1),
        ),
    ]