# Generated by Django 2.2.10 on 2020-05-09 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20200509_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='territorymapdata',
            name='abbreviation',
            field=models.CharField(max_length=100, null=True),
        ),
    ]