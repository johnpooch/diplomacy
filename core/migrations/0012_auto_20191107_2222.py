# Generated by Django 2.2.5 on 2019-11-07 22:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_merge_20191107_2129'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GameNation',
            new_name='NationState',
        ),
    ]