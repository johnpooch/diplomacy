# Generated by Django 3.1 on 2020-10-11 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_add_standard_game'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nationstate',
            name='nation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.nation'),
        ),
    ]
