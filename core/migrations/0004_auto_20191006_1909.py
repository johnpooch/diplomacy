# Generated by Django 2.1.7 on 2019-10-06 19:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20191002_1921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='command',
            name='piece',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Piece'),
        ),
        migrations.AlterField(
            model_name='command',
            name='target',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.Territory'),
        ),
    ]