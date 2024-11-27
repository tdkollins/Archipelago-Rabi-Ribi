import logging

from random import Random
from typing import Any
from .existing_randomizer.analyzer import Analyzer
from .existing_randomizer.dataparser import RandomizerData
from .existing_randomizer.allocation import Allocation
from .logic_helpers import convert_existing_rando_name_to_ap_name

logger = logging.getLogger('Rabi-Ribi')

class MapAllocation(Allocation):
    """An implementation of Allocation that replaces all items in the pool with item locations to obtain."""
    def __init__(self, data: RandomizerData, settings: tuple[str, Any], random: Random):

        super().__init__(data, settings, random)

    def shuffle(self, data, settings):
        self.map_modifications = list(data.default_map_modifications)

        # Create non-conflicting items locations for the analyzer to mark as visited.
        self.item_at_item_location = { key: f'LOC_{key}' for key in data.item_slots }
        for name in data.item_slots:
            data.configured_variables[f'LOC_{name}'] = False

        # Shuffle Constraints
        self.choose_constraint_templates(data, settings)

        # Shuffle Locations
        self.construct_graph(data, settings)


class MapGenerator(object):
    """The MapAnalyzer class is an reimplementation of the Generator class with simplified validation,
    only ensuring that all locations are reachable if the player has all upgrades."""
    def __init__(self, data: RandomizerData, settings: Any, locations_to_reach: set[str], random: Random):
        self.data = data
        self.settings = settings
        self.allocation = MapAllocation(data, settings, random)
        self.locations_to_reach = locations_to_reach

    def generate_seed(self):
        MAX_ATTEMPTS = self.settings.max_attempts
        success = False

        for i in range(MAX_ATTEMPTS):
            self.shuffle()
            analyzer = MapAnalyzer(self.data, self.settings, self.allocation, self.locations_to_reach)

            if analyzer.success:
                success = True
                logger.info(f'Generated a valid seed after {i} attempts.')
                break

        if not success:
            raise RuntimeError(f'Unable to generate a valid seed after {MAX_ATTEMPTS} attempts.')

        return self.allocation, analyzer

    def shuffle(self):
        self.allocation.shuffle(self.data, self.settings)

class MapAnalyzer(Analyzer):
    """The MapAnalyzer class is an extension of the Analyzer class with simplified validation,
    only ensuring that all locations are reachable if the player has all upgrades."""
    def __init__(self, data: RandomizerData, settings: Any, allocation: MapAllocation, locations_to_reach: set[str]):
        self.data = data
        self.settings = settings
        self.allocation = allocation
        self.locations_to_reach = locations_to_reach

        # Disable the existing analyzer's visualizer
        self.visualize = False

        self.error_message = ''
        self.success = self.run_map_verifier()

    def run_map_verifier(self):
        starting_variables = self.data.generate_variables()
        result, backward_exitable = self.verify_warps_reachable(starting_variables)
        if not result:
            self.error_message = 'Not all warps reachable.'
            return False

        reachable, unreachable, levels, _ = self.verify_reachable_items(starting_variables, backward_exitable)

        # Convert item locations back to actual names
        item_location_reachable = {convert_existing_rando_name_to_ap_name(name[4:]) for name in reachable}

        if not self.locations_to_reach.issubset(item_location_reachable):
            self.error_message = 'Not all locations are reachable.'
            return False

        return True
    
    def verify_reachable_items(self, starting_variables, backward_exitable):
        # Mark all upgrades as obtained already
        for item in self.data.must_be_reachable:
            starting_variables[item] = True
        return super().verify_reachable_items(starting_variables, backward_exitable)