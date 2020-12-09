# Generated by Django 3.1.3 on 2020-12-06 17:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20201203_2231'),
    ]

    operations = [
        migrations.AddField(
            model_name='piecestate',
            name='dislodged_from',
            field=models.OneToOneField(blank=True, help_text="True if the piece was dislodged via a land attack during this turn. The piece's attacker_territory field will be set to this value next turn.", null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pieces_dislodged_from_here', to='core.territory'),
        ),
        migrations.AlterField(
            model_name='piecestate',
            name='attacker_territory',
            field=models.ForeignKey(blank=True, help_text="True if the piece was dislodged via a land attack in the previous turn. During this turn the piece cannot to the attacking piece's territory.", null=True, on_delete=django.db.models.deletion.CASCADE, to='core.territory'),
        ),
    ]
