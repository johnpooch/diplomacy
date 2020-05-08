# Generated by Django 2.2.10 on 2020-05-07 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20200423_2149'),
    ]

    operations = [
        migrations.AddField(
            model_name='variant',
            name='starting_phase',
            field=models.CharField(choices=[('order', 'Order'), ('retreat_and_disband', 'Retreat and Disband'), ('build', 'Build')], default='order', max_length=100),
        ),
        migrations.AddField(
            model_name='variant',
            name='starting_season',
            field=models.CharField(choices=[('fall', 'Fall'), ('spring', 'Spring')], default='spring', max_length=100),
        ),
        migrations.AddField(
            model_name='variant',
            name='starting_year',
            field=models.PositiveIntegerField(default=1900),
        ),
    ]