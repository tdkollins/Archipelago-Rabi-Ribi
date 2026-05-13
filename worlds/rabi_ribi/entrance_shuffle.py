import bisect
import logging

from random import Random
from typing import Any, override
from Options import Accessibility
from worlds.AutoWorld import World
from .constants import GAME_NAME
from .data import data as game_data
from .existing_randomizer.analyzer import Analyzer
from .existing_randomizer.dataparser import RandomizerData
from .existing_randomizer.allocation import Allocation
from .options import RabiRibiOptions

logger = logging.getLogger(GAME_NAME)
MAX_ATTEMPTS = 10000

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

        # Shuffle Map Transitions
        self.shuffle_map_transitions(settings)

        # Shuffle Locations
        self.construct_graph(data, settings)

        # Choose Starting Location
        self.choose_starting_location(data, settings)

    @override
    def choose_constraint_templates(self, data, settings):        
        self.edge_replacements = {}

        def get_template_count(settings):
            low = int(0.5 * settings.constraint_changes)
            high = int(1.5 * settings.constraint_changes + 2)
            if settings.constraint_changes <= 0:
                high = 0
            if settings.min_constraint_changes >= 0:
                low = int(settings.min_constraint_changes)
            if settings.max_constraint_changes >= 0:
                high = int(settings.max_constraint_changes + 1)
            if low == high:return low
            return self.random.randrange(low, high)

        templates = list(data.template_constraints)
        target_template_count = get_template_count(settings)

        # Force selection of required templates
        ap_options: RabiRibiOptions = settings.ap_options
        required_constraints = {
            constraint.logic_key
            for constraint in game_data.constraints
            if constraint.name in ap_options.required_constraints
        }
        picked_templates = [
            template
            for template in data.template_constraints
            if template.name in required_constraints
        ]
        update_table = False
        template_weights = data.initial_template_weights.copy()
        template_index = data.initial_template_index.copy()
        total_weight = template_weights[-1]
        removed_weight = 0

        # Remove conflicting templates from required templates
        for template in picked_templates:
            for conflict in template.conflicts_names:
                if conflict in template_index:
                    conflict_index = template_index[conflict]
                    if conflict_index < 0: continue
                    removed_weight += templates[conflict_index].weight
                    templates[conflict_index] = None
                    template_index[conflict] = -1

        # Remove excluded templates
        excluded_constraints = {
            constraint.logic_key
            for constraint in game_data.constraints
            if constraint.name in ap_options.exclude_constraints
        }
        excluded_templates = [
            template
            for template in data.template_constraints
            if template.name in excluded_constraints
        ]
        for conflict in excluded_templates:
            if conflict in template_index:
                conflict_index = template_index[conflict]
                if conflict_index < 0: continue
                removed_weight += templates[conflict_index].weight
                templates[conflict_index] = None
                template_index[conflict] = -1

        while len(templates) > 0 and len(picked_templates) < target_template_count:
            if update_table:
                update_table = False
                i = 0
                total_weight = 0
                removed_weight = 0
                template_index.clear()
                for t in templates:
                    total_weight += t.weight
                    template_weights[i] = total_weight
                    template_index[t.name] = i
                    i += 1
                template_weights = template_weights[:i]

            while True:
                index = self.random.randrange(total_weight)
                picked = bisect.bisect(template_weights, index)
                current_template = templates[picked]
                if current_template != None:
                    break

            picked_templates.append(current_template)

            # remove all conflicting templates
            for conflict in current_template.conflicts_names:
                if conflict in template_index:
                    conflict_index = template_index[conflict]
                    if conflict_index < 0: continue
                    removed_weight += templates[conflict_index].weight
                    templates[conflict_index] = None
                    template_index[conflict] = -1

            if (removed_weight / total_weight) > 0.35:
                update_table = True
                new_templates = []
                for t in templates:
                    if t == None: continue
                    new_templates.append(t)
                templates = new_templates

        self.picked_templates = picked_templates
        for template in picked_templates:
            for change in template.changes:
                self.edge_replacements[(change.from_location, change.to_location)] = change
            self.map_modifications.append(template.template_file)

    def construct_set_seed(self, data, settings, picked_templates: set[str], map_transition_shuffle_order: list[int], start_location: str):
        self.map_modifications = list(data.default_map_modifications)

        # Apply the selected templates for the graph
        template_lookup = {t.name: t for t in data.template_constraints}
        self.picked_templates = [template_lookup[n] for n in picked_templates]
        self.edge_replacements = {}

        for template in self.picked_templates:
            for change in template.changes:
                self.edge_replacements[(change.from_location, change.to_location)] = change
            self.map_modifications.append(template.template_file)

        # Apply the selected map transition shuffle for the graph
        self.walking_left_transitions = [data.walking_left_transitions[i] for i in map_transition_shuffle_order]

        self.construct_graph(data, settings)

        self.start_location = next((location for location in data.start_locations if location.location == start_location), data.start_locations[0])

class MapGenerator(object):
    """The MapAnalyzer class is an reimplementation of the Generator class with simplified validation,
    only ensuring that all locations are reachable if the player has all upgrades."""
    def __init__(self, data: RandomizerData, settings: Any, locations_to_reach: set[str], world: World):
        self.data = data
        self.settings = settings
        self.allocation = MapAllocation(data, settings, world.random)
        self.locations_to_reach = locations_to_reach
        self.world = world

    def generate_seed(self):
        success = False
        analyzer = None

        for i in range(MAX_ATTEMPTS):
            self.shuffle()
            analyzer = MapAnalyzer(self.data, self.settings, self.allocation, self.locations_to_reach)

            if analyzer.success:
                success = True
                logger.debug(f'Rabi-Ribi: Valid map transition and/or constraint set for Player {self.world.player} ({self.world.player_name}) found after {i+1} attempts.')
                break

            # Revert graph for next attempt
            self.allocation.revert_graph(self.data)

        if not success:
            raise RuntimeError(f'Rabi-Ribi: Unable to find a valid map transition and/or constraint set for Player {self.world.player} ({self.world.player_name}) after {MAX_ATTEMPTS} attempts.')

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

        if not self.verify_any_location_reachable(starting_variables, backward_exitable):
            self.error_message = 'No locations are reachable at the start.'
            return False

        # Ignore accessibility requirements when on minimal accessibility
        ap_options: RabiRibiOptions = self.settings.ap_options
        if (ap_options.accessibility == Accessibility.option_full
            and not self.verify_all_locations_reachable(starting_variables, backward_exitable)):
            self.error_message = 'Not all locations are reachable.'
            return False

        return True

    def verify_any_location_reachable(self, starting_variables, backward_exitable):
        """Verifies that at least one location is reachable without items."""
        reachable, _, _, _ = self.verify_reachable_items(starting_variables, backward_exitable)

        # Convert item locations back to actual names
        item_location_reachable = {game_data.get_location_ap_name(name[4:]) for name in reachable if name.startswith('LOC_')}
        return len(item_location_reachable) > 0

    def verify_all_locations_reachable(self, starting_variables, backward_exitable):
        """Verifies that all locations are reachable if player has all items."""
        # Mark all upgrades as obtained already
        variables = dict(starting_variables)
        for item in self.data.must_be_reachable:
            variables[item] = True

        reachable, _, _, _ = self.verify_reachable_items(variables, backward_exitable)

        # Convert item locations back to actual names
        item_location_reachable = {game_data.get_location_ap_name(name[4:]) for name in reachable if name.startswith('LOC_')}

        return self.locations_to_reach.issubset(item_location_reachable)