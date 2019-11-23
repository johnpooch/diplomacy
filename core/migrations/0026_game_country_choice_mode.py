# Generated by Django 2.2.5 on 2019-11-23 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_game_process_on_finalized_orders'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='country_choice_mode',
            field=models.CharField(choices=[('random', 'Random'), ('preference', 'Preference'), ('first come', 'First come first serve')], default='random', max_length=100),
        ),
    ]
