# Generated by Django 2.2.5 on 2020-04-10 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20200410_1343'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='illegal_message',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='legal',
            field=models.BooleanField(default=True),
        ),
    ]