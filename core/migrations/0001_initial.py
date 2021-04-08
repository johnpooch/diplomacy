# Generated by Django 3.1.4 on 2021-03-05 17:08

import core.models.mixins
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Draw',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proposed_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('proposed', 'Proposed'), ('canceled', 'Canceled'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('expired', 'Expired')], default='proposed', max_length=20)),
                ('resolved_at', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('slug', models.CharField(blank=True, db_index=True, max_length=255, unique=True)),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('active', 'Active'), ('ended', 'Ended')], default='pending', editable=False, max_length=22)),
                ('private', models.BooleanField(default=False)),
                ('password', models.CharField(blank=True, max_length=100, null=True)),
                ('order_deadline', models.CharField(choices=[('twelve_hours', '12 hours'), ('twenty_four_hours', '24 hours'), ('two_days', '2 days'), ('three_days', '3 days'), ('five_days', '5 days'), ('seven_days', '7 days')], default='twenty_four_hours', max_length=100)),
                ('retreat_deadline', models.CharField(choices=[('twelve_hours', '12 hours'), ('twenty_four_hours', '24 hours'), ('two_days', '2 days'), ('three_days', '3 days'), ('five_days', '5 days'), ('seven_days', '7 days')], default='twenty_four_hours', max_length=100)),
                ('build_deadline', models.CharField(choices=[('twelve_hours', '12 hours'), ('twenty_four_hours', '24 hours'), ('two_days', '2 days'), ('three_days', '3 days'), ('five_days', '5 days'), ('seven_days', '7 days')], default='twelve_hours', max_length=100)),
                ('process_on_finalized_orders', models.BooleanField(default=True)),
                ('nation_choice_mode', models.CharField(choices=[('random', 'Random'), ('preference', 'Preference'), ('first_come', 'First come first serve')], default='random', max_length=100)),
                ('num_players', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('initialized_at', models.DateTimeField(null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_games', to=settings.AUTH_USER_MODEL)),
            ],
            bases=(models.Model, core.models.mixins.AutoSlug),
        ),
        migrations.CreateModel(
            name='NamedCoast',
            fields=[
                ('id', models.CharField(editable=False, max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('map_abbreviation', models.CharField(max_length=50)),
                ('piece_starts_here', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'named_coast',
            },
        ),
        migrations.CreateModel(
            name='Nation',
            fields=[
                ('id', models.CharField(editable=False, max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=15)),
                ('flag', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='NationState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orders_finalized', models.BooleanField(default=False)),
                ('nation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.nation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Piece',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('army', 'Army'), ('fleet', 'Fleet')], default='army', max_length=50)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pieces', to='core.game')),
                ('nation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pieces', to='core.nation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Territory',
            fields=[
                ('id', models.CharField(editable=False, max_length=100, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('type', models.CharField(choices=[('inland', 'Inland'), ('coastal', 'Coastal'), ('sea', 'Sea')], max_length=10)),
                ('supply_center', models.BooleanField(default=False)),
                ('initial_piece_type', models.CharField(choices=[('army', 'Army'), ('fleet', 'Fleet')], max_length=50, null=True)),
                ('controlled_by_initial', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='initially_controlled_territories', to='core.nation')),
                ('nationality', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='national_territories', to='core.nation')),
                ('neighbours', models.ManyToManyField(blank=True, related_name='_territory_neighbours_+', to='core.Territory')),
                ('shared_coasts', models.ManyToManyField(related_name='_territory_shared_coasts_+', to='core.Territory')),
            ],
            options={
                'verbose_name_plural': 'territories',
            },
        ),
        migrations.CreateModel(
            name='Turn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.CharField(choices=[('fall', 'Fall'), ('spring', 'Spring')], max_length=7)),
                ('phase', models.CharField(choices=[('order', 'Order'), ('retreat', 'Retreat'), ('build', 'Build')], max_length=20)),
                ('year', models.PositiveIntegerField()),
                ('next_season', models.CharField(choices=[('fall', 'Fall'), ('spring', 'Spring')], max_length=7, null=True)),
                ('next_phase', models.CharField(choices=[('order', 'Order'), ('retreat', 'Retreat'), ('build', 'Build')], max_length=20, null=True)),
                ('next_year', models.PositiveIntegerField(null=True)),
                ('current_turn', models.BooleanField(default=True)),
                ('processed', models.BooleanField(default=False)),
                ('processed_at', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='turns', to='core.game')),
            ],
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.CharField(editable=False, max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('max_num_players', models.PositiveIntegerField(default=7)),
                ('num_supply_centers_to_win', models.PositiveIntegerField(default=18)),
                ('max_nations_in_draw', models.PositiveIntegerField(default=4)),
                ('starting_year', models.PositiveIntegerField(default=1901)),
                ('starting_season', models.CharField(choices=[('fall', 'Fall'), ('spring', 'Spring')], default='spring', max_length=100)),
                ('starting_phase', models.CharField(choices=[('order', 'Order'), ('retreat', 'Retreat'), ('build', 'Build')], default='order', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TurnEnd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('task_id', models.CharField(max_length=255, null=True)),
                ('turn', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.turn')),
            ],
        ),
        migrations.CreateModel(
            name='TerritoryState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contested', models.BooleanField(default=False)),
                ('bounce_occurred', models.BooleanField(default=False)),
                ('captured_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='captured_territories', to='core.nation')),
                ('controlled_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='controlled_territories', to='core.nation')),
                ('territory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='territory_states', to='core.territory')),
                ('turn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='territorystates', to='core.turn')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='territory',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='territories', to='core.variant'),
        ),
        migrations.CreateModel(
            name='Surrender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('canceled', 'Canceled'), ('fulfilled', 'Fulfilled')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(null=True)),
                ('nation_state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surrenders', to='core.nationstate')),
                ('replaced_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replaced', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surrenders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PieceState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dislodged', models.BooleanField(default=False)),
                ('destroyed', models.BooleanField(default=False)),
                ('destroyed_message', models.CharField(blank=True, max_length=200, null=True)),
                ('must_retreat', models.BooleanField(default=False, help_text='Signifies that the piece was dislodged in the previous turn and now must retreat.')),
                ('attacker_territory', models.ForeignKey(blank=True, help_text="True if the piece was dislodged via a land attack in the previous turn. During this turn the piece cannot to the attacking piece's territory.", null=True, on_delete=django.db.models.deletion.CASCADE, to='core.territory')),
                ('dislodged_by', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='piece_dislodged', to='core.piecestate')),
                ('dislodged_from', models.OneToOneField(blank=True, help_text="True if the piece was dislodged via a land attack during this turn. The piece's attacker_territory field will be set to this value next turn.", null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pieces_dislodged_from_here', to='core.territory')),
                ('named_coast', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pieces', to='core.namedcoast')),
                ('piece', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='states', to='core.piece')),
                ('territory', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pieces', to='core.territory')),
                ('turn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='piecestates', to='core.turn')),
            ],
        ),
        migrations.AddField(
            model_name='piece',
            name='turn_created',
            field=models.ForeignKey(blank=True, help_text='The turn during which this piece was created. Will always be a build phase. If null, piece was created at the beginning of the game.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.turn'),
        ),
        migrations.AddField(
            model_name='piece',
            name='turn_disbanded',
            field=models.ForeignKey(blank=True, help_text='The turn during which this piece was disbanded. Will always be a retreat/disband phase or a build/disband phase.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.turn'),
        ),
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('hold', 'Hold'), ('move', 'Move'), ('support', 'Support'), ('convoy', 'Convoy'), ('retreat', 'Retreat'), ('build', 'Build'), ('disband', 'Disband')], default='hold', max_length=8)),
                ('piece_type', models.CharField(blank=True, choices=[('army', 'Army'), ('fleet', 'Fleet')], max_length=50, null=True)),
                ('via_convoy', models.BooleanField(default=False)),
                ('outcome', models.CharField(blank=True, choices=[('moves', 'Moves'), ('resolved', 'Resolved'), ('bounced', 'Bounced'), ('aux_failed', 'Aux failed'), ('aux_does_not_correspond', 'Aux does not correspond'), ('succeeds', 'Succeeds'), ('given', 'Given'), ('fails', 'Fails')], max_length=25, null=True)),
                ('outcome_verbose', models.CharField(blank=True, max_length=500, null=True)),
                ('illegal', models.BooleanField(default=False)),
                ('illegal_code', models.CharField(blank=True, max_length=50, null=True)),
                ('illegal_verbose', models.CharField(blank=True, max_length=500, null=True)),
                ('aux', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.territory')),
                ('nation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='core.nation')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_orders', to='core.territory')),
                ('target', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.territory')),
                ('target_coast', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.namedcoast')),
                ('turn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='core.turn')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='nationstate',
            name='turn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nationstates', to='core.turn'),
        ),
        migrations.AddField(
            model_name='nationstate',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='nation_states', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='nation',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nations', to='core.variant'),
        ),
        migrations.AddField(
            model_name='namedcoast',
            name='neighbours',
            field=models.ManyToManyField(blank=True, related_name='named_coast_neighbours', to='core.Territory'),
        ),
        migrations.AddField(
            model_name='namedcoast',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='named_coasts', to='core.territory'),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=1000)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='core.nation')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to='core.nation')),
            ],
            options={
                'db_table': 'message',
            },
        ),
        migrations.AddField(
            model_name='game',
            name='participants',
            field=models.ManyToManyField(through='core.Participation', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='game',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to='core.variant'),
        ),
        migrations.AddField(
            model_name='game',
            name='winners',
            field=models.ManyToManyField(to='core.Nation'),
        ),
        migrations.CreateModel(
            name='DrawResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.CharField(choices=[('accepted', 'Accepted'), ('rejected', 'Rejected')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('draw', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.draw')),
                ('nation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.nation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='draw',
            name='nations',
            field=models.ManyToManyField(related_name='draws', to='core.Nation'),
        ),
        migrations.AddField(
            model_name='draw',
            name='proposed_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proposed_draws', to='core.nation'),
        ),
        migrations.AddField(
            model_name='draw',
            name='proposed_by_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='draw',
            name='turn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='draws', to='core.turn'),
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('nation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='announcements', to='core.nation')),
            ],
            options={
                'db_table': 'announcement',
            },
        ),
        migrations.AddConstraint(
            model_name='turn',
            constraint=models.UniqueConstraint(fields=('game', 'year', 'season', 'phase'), name='unique_phase_per_game,'),
        ),
        migrations.AlterUniqueTogether(
            name='territory',
            unique_together={('name', 'variant')},
        ),
        migrations.AddConstraint(
            model_name='piecestate',
            constraint=models.UniqueConstraint(fields=('turn', 'territory', 'must_retreat'), name='unique_piece_in_territory,'),
        ),
        migrations.AlterUniqueTogether(
            name='nation',
            unique_together={('name', 'variant')},
        ),
        migrations.AddConstraint(
            model_name='namedcoast',
            constraint=models.UniqueConstraint(fields=('parent', 'map_abbreviation'), name='unique_coast_abbreviation'),
        ),
        migrations.AddConstraint(
            model_name='namedcoast',
            constraint=models.UniqueConstraint(fields=('parent', 'name'), name='unique_coast_name'),
        ),
        migrations.AlterUniqueTogether(
            name='drawresponse',
            unique_together={('draw', 'nation')},
        ),
    ]
