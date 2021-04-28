# Generated by Django 3.1.7 on 2021-04-23 13:26

from django.db import migrations


def title_case_named_coast_names(apps, schema_editor):
    NamedCoast = apps.get_model('core', 'NamedCoast')
    for named_coast in NamedCoast.objects.all():
        named_coast.name = named_coast.name.title()
        named_coast.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20210423_0935'),
    ]

    operations = [
        migrations.RunPython(
            title_case_named_coast_names,
            reverse_code=migrations.RunPython.noop
        ),
    ]
