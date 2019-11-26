# Generated by Django 2.2.5 on 2019-11-23 13:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_game_country_choice_mode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='turn',
            name='current_turn',
        ),
        migrations.AlterField(
            model_name='turn',
            name='year',
            field=models.PositiveIntegerField(),
        ),
        migrations.CreateModel(
            name='TurnEnd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('task_id', models.CharField(max_length=255, null=True)),
                ('turn', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='end', to='core.Turn')),
            ],
        ),
    ]