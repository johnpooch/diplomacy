# Generated by Django 3.1.7 on 2021-04-23 08:35

from django.db import migrations


def add_st_petersburg_to_norway_shared_coasts(apps, schema_editor):
    Territory = apps.get_model('core', 'Territory')
    st_petersburg = Territory.objects.get(id='standard-st-petersburg')
    norway = Territory.objects.get(id='standard-norway')
    norway.shared_coasts.add(st_petersburg)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20210422_1309'),
    ]

    operations = [
        migrations.RunPython(
            add_st_petersburg_to_norway_shared_coasts,
            reverse_code=migrations.RunPython.noop
        ),
    ]
