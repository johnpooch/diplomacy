import unittest

from core import models
from core.utils.command import convoy, move, support
from core.utils.piece import army, fleet
from core.tests.base import HelperMixin, TerritoriesMixin
from core.tests.base import InitialGameStateTestCase as TestCase


class TestCircularMovement(TestCase, HelperMixin, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'supply_centers.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.initialise_named_coasts()
        self.initialise_nations()
        self.initialise_orders()

    @unittest.skip
    def test_three_army_circular_movement(self):
        """
        Three units can change place, even in spring 1901.

        Turkey:
        F Ankara - Constantinople
        A Constantinople - Smyrna
        A Smyrna - Ankara

        All three units will move.
        """
        fleet_ankara = fleet(self.turkey, self.ankara)
        army_constantinople = army(self.turkey, self.constantinople)
        army_smyrna = army(self.turkey, self.smyrna)

        fleet_ankara_move = move(
            self.turkey_order, fleet_ankara, self.ankara, self.constantinople
        )
        army_constantinople_move = move(
            self.turkey_order, army_constantinople, self.constantinople,
            self.smyrna
        )
        army_smyrna_move = move(
            self.turkey_order, army_smyrna, self.smyrna, self.ankara
        )
        commands = [fleet_ankara_move, army_constantinople_move,
                    army_smyrna_move]
        models.Command.objects.process()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_ankara_move.succeeds)
        self.assertTrue(army_constantinople_move.succeeds)
        self.assertTrue(army_smyrna_move.succeeds)

    @unittest.skip
    def test_three_army_circular_movement_with_support(self):
        """
        Three units can change place, even when one gets support.

        Turkey:
        F Ankara - Constantinople
        A Constantinople - Smyrna
        A Smyrna - Ankara
        A Bulgaria Supports F Ankara - Constantinople

        Of course the three units will move, but knowing how programs are
        written, this can confuse the adjudicator.
        """
        fleet_ankara = fleet(self.turkey, self.ankara)
        army_bulgaria = army(self.turkey, self.bulgaria)
        army_constantinople = army(self.turkey, self.constantinople)
        army_smyrna = army(self.turkey, self.smyrna)

        fleet_ankara_move = move(
            self.turkey_order, fleet_ankara, self.ankara, self.constantinople
        )
        army_bulgaria_support = support(
            self.turkey_order, army_bulgaria, self.bulgaria, self.ankara,
            self.constantinople,
        )
        army_constantinople_move = move(
            self.turkey_order, army_constantinople, self.constantinople,
            self.smyrna
        )
        army_smyrna_move = move(
            self.turkey_order, army_smyrna, self.smyrna, self.ankara
        )
        commands = [fleet_ankara_move, army_constantinople_move,
                    army_smyrna_move, army_bulgaria_support]
        models.Command.objects.process()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(army_bulgaria_support.succeeds)
        self.assertTrue(fleet_ankara_move.succeeds)
        self.assertTrue(army_constantinople_move.succeeds)
        self.assertTrue(army_smyrna_move.succeeds)

    def test_disrupted_three_army_circular_movement(self):
        """
        When one of the units bounces, the whole circular movement will hold.

        Turkey:
        F Ankara - Constantinople
        A Constantinople - Smyrna
        A Smyrna - Ankara
        A Bulgaria - Constantinople

        Every unit will keep its place.
        """
        fleet_ankara = fleet(self.turkey, self.ankara)
        army_bulgaria = army(self.turkey, self.bulgaria)
        army_constantinople = army(self.turkey, self.constantinople)
        army_smyrna = army(self.turkey, self.smyrna)

        fleet_ankara_move = move(
            self.turkey_order, fleet_ankara, self.ankara, self.constantinople
        )
        army_bulgaria_move = move(
            self.turkey_order, army_bulgaria, self.bulgaria,
            self.constantinople,
        )
        army_constantinople_move = move(
            self.turkey_order, army_constantinople, self.constantinople,
            self.smyrna
        )
        army_smyrna_move = move(
            self.turkey_order, army_smyrna, self.smyrna, self.ankara
        )
        commands = [fleet_ankara_move, army_constantinople_move,
                    army_smyrna_move, army_bulgaria_move]
        models.Command.objects.process()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(army_bulgaria_move.fails)
        self.assertTrue(fleet_ankara_move.fails)
        self.assertTrue(army_constantinople_move.fails)
        self.assertTrue(army_smyrna_move.fails)

    @unittest.skip
    def test_circular_movement_with_attacked_convoy(self):
        """
        When the circular movement contains an attacked convoy, the circular
        movement succeeds. The adjudication algorithm should handle attack of
        convoys before calculating circular movement.

        Austria:
        A Trieste - Serbia
        A Serbia - Bulgaria

        Turkey:
        A Bulgaria - Trieste
        F Aegean Sea Convoys A Bulgaria - Trieste
        F Ionian Sea Convoys A Bulgaria - Trieste
        F Adriatic Sea Convoys A Bulgaria - Trieste

        Italy:
        F Naples - Ionian Sea

        The fleet in the Ionian Sea is attacked but not dislodged. The circular
        movement succeeds. The Austrian and Turkish armies will advance.
        """
        army_trieste = army(self.austria, self.trieste)
        army_serbia = army(self.austria, self.serbia)

        army_bulgaria = army(self.turkey, self.bulgaria)
        fleet_aegean = fleet(self.turkey, self.aegean_sea)
        fleet_ionian = fleet(self.turkey, self.ionian_sea)
        fleet_adriatic = fleet(self.turkey, self.adriatic_sea)

        fleet_naples = fleet(self.italy, self.naples)

        army_trieste_move = move(
            self.austria_order, army_trieste, self.trieste, self.serbia
        )
        army_serbia_move = move(
            self.austria_order, army_serbia, self.serbia, self.bulgaria,
        )
        army_bulgaria_move = move(
            self.turkey_order, army_bulgaria, self.bulgaria, self.trieste,
        )
        fleet_aegean_convoy = convoy(
            self.turkey_order, fleet_aegean, self.aegean_sea, self.bulgaria,
            self.trieste,
        )
        fleet_ionian_convoy = convoy(
            self.turkey_order, fleet_ionian, self.ionian_sea, self.bulgaria,
            self.trieste,
        )
        fleet_adriatic_convoy = convoy(
            self.turkey_order, fleet_adriatic, self.adriatic_sea, self.bulgaria,
            self.trieste,
        )
        fleet_naples_move = move(
            self.italy_order, fleet_naples, self.naples, self.ionian_sea,
        )
        commands = [
            army_bulgaria_move, army_trieste_move, army_serbia_move,
            fleet_aegean_convoy, fleet_ionian_convoy, fleet_adriatic_convoy,
            fleet_naples_move
        ]
        models.Command.objects.process()
        [c.refresh_from_db() for c in commands]

        failing_command = commands.pop(-1)
        self.assertTrue(failing_command.fails)
        for c in commands:
            self.assertTrue(c.succeeds)

    @unittest.skip
    def test_disrupted_circular_movement_due_to_dislodged_convoy(self):
        """
        When the circular movement contains a convoy, the circular movement is
        disrupted when the convoying fleet is dislodged. The adjudication
        algorithm should disrupt convoys before calculating circular movement.

        Austria:
        A Trieste - Serbia
        A Serbia - Bulgaria

        Turkey:
        A Bulgaria - Trieste
        F Aegean Sea Convoys A Bulgaria - Trieste
        F Ionian Sea Convoys A Bulgaria - Trieste
        F Adriatic Sea Convoys A Bulgaria - Trieste

        Italy:
        F Naples - Ionian Sea
        F Tunis Supports F Naples - Ionian Sea

        Due to the dislodged convoying fleet, all Austrian and Turkish armies
        will not move.
        """
        army_trieste = army(self.austria, self.trieste)
        army_serbia = army(self.austria, self.serbia)

        army_bulgaria = army(self.turkey, self.bulgaria)
        fleet_aegean = fleet(self.turkey, self.aegean_sea)
        fleet_ionian = fleet(self.turkey, self.ionian_sea)
        fleet_adriatic = fleet(self.turkey, self.adriatic_sea)

        fleet_naples = fleet(self.italy, self.naples)
        fleet_tunis = fleet(self.italy, self.tunis)

        army_trieste_move = move(
            self.austria_order, army_trieste, self.trieste, self.serbia
        )
        army_serbia_move = move(
            self.austria_order, army_serbia, self.serbia, self.bulgaria,
        )
        army_bulgaria_move = move(
            self.turkey_order, army_bulgaria, self.bulgaria, self.trieste,
        )
        fleet_aegean_convoy = convoy(
            self.turkey_order, fleet_aegean, self.aegean_sea, self.bulgaria,
            self.trieste,
        )
        fleet_ionian_convoy = convoy(
            self.turkey_order, fleet_ionian, self.ionian_sea, self.bulgaria,
            self.trieste,
        )
        fleet_adriatic_convoy = convoy(
            self.turkey_order, fleet_adriatic, self.adriatic_sea, self.bulgaria,
            self.trieste,
        )
        fleet_naples_move = move(
            self.italy_order, fleet_naples, self.naples, self.ionian_sea,
        )
        fleet_tunis_support = support(
            self.italy_order, fleet_tunis, self.tunis, self.naples, self.ionian_sea,
        )
        commands = [
            army_bulgaria_move, army_trieste_move, army_serbia_move,
            fleet_aegean_convoy, fleet_ionian_convoy, fleet_adriatic_convoy,
            fleet_naples_move, fleet_tunis_support,
        ]
        models.Command.objects.process()
        [c.refresh_from_db() for c in commands]

        for c in [fleet_naples_move, fleet_tunis_support]:
            self.assertTrue(c.succeeds)

        # this should fail because it does not have a path
        self.assertTrue(army_bulgaria_move.fails)
        self.assertTrue(army_serbia_move.fails)
        self.assertTrue(army_trieste_move.fails)
        for c in [army_bulgaria_move, army_trieste_move, army_serbia_move]:
            self.assertTrue(c.fails)

    def test_two_armies_with_two_convoys(self):
        """
        Two armies can swap places even when they are not adjacent.

        England:
        F North Sea Convoys A London - Belgium
        A London - Belgium

        France:
        F English Channel Convoys A Belgium - London
        A Belgium - London

        Both convoys should succeed.
        """
        fleet_north_sea = fleet(self.england, self.north_sea)
        army_london = army(self.england, self.london)

        fleet_english_channel = fleet(self.france, self.english_channel)
        army_belgium = army(self.france, self.belgium)

        fleet_north_sea_convoy = convoy(
            self.england_order, fleet_north_sea, self.north_sea, self.london,
            self.belgium,
        )
        army_london_move = move(
            self.england_order, army_london, self.london, self.belgium
        )
        fleet_english_channel_convoy = convoy(
            self.france_order, fleet_english_channel, self.english_channel, self.belgium,
            self.london,
        )
        army_belgium_move = move(
            self.france_order, army_belgium, self.belgium, self.london
        )
        commands = [
            army_belgium_move, army_london_move, fleet_north_sea_convoy,
            fleet_english_channel_convoy,
        ]
        models.Command.objects.process()
        [c.refresh_from_db() for c in commands]
        [c.succeeds for c in commands]

    def test_disrupted_unit_swap(self):
        """
        If in a swap one of the unit bounces, then the swap fails.

        England:
        F North Sea Convoys A London - Belgium
        A London - Belgium

        France:
        F English Channel Convoys A Belgium - London
        A Belgium - London
        A Burgundy - Belgium

        None of the units will succeed to move.
        """
        fleet_north_sea = fleet(self.england, self.north_sea)
        army_london = army(self.england, self.london)

        fleet_english_channel = fleet(self.france, self.english_channel)
        army_belgium = army(self.france, self.belgium)
        army_burgundy = army(self.france, self.burgundy)

        fleet_north_sea_convoy = convoy(
            self.england_order, fleet_north_sea, self.north_sea, self.london,
            self.belgium,
        )
        army_london_move = move(
            self.england_order, army_london, self.london, self.belgium
        )
        fleet_english_channel_convoy = convoy(
            self.france_order, fleet_english_channel, self.english_channel, self.belgium,
            self.london,
        )
        army_belgium_move = move(
            self.france_order, army_belgium, self.belgium, self.london
        )
        army_burgundy_move = move(
            self.france_order, army_burgundy, self.burgundy, self.belgium
        )
        commands = [
            army_belgium_move, army_london_move, fleet_north_sea_convoy,
            fleet_english_channel_convoy, army_burgundy_move
        ]
        models.Command.objects.process()
        [c.refresh_from_db() for c in commands]
        [c.fails for c in commands]
