# Generated by Django 2.1.7 on 2019-07-27 13:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0002_piece_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='piece',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='challenging', to='service.Piece'),
        ),
    ]
