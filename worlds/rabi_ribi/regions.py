"""This module represents region definitions for Rabi-Ribi"""
import logging

from typing import Any, Optional
from BaseClasses import Region, ItemClassification
from rule_builder.rules import Rule
from .bases import RabiRibiWorldBase
from .constants import GAME_NAME
from .data import data, RegionData
from .entrance_shuffle import MapAllocation, MapGenerator
from .items import RabiRibiItem
from .locations import RabiRibiLocation, setup_locations
from .names import ItemName, LocationName
from .rules import *

logger = logging.getLogger(GAME_NAME)

class RegionHelper:
    """
    This class provides methods associated with defining and connecting regions, locations,
    and the access rules for those regions and locations.
    """
    regions: set[str]
    location_table: dict[str, int]
    unreachable_regions: set[str]
    picked_templates: set[str]

    def __init__(self, world: RabiRibiWorldBase):
        self.world = world
        self.player = self.world.player
        self.multiworld = self.world.multiworld
        self.options = self.world.options
        self.existing_randomizer_args: Any = self.world.existing_randomizer_args
        self.randomizer_data = self.world.randomizer_data

        self.regions = { region.name for region in data.regions if self._region_filter(region) }
        self.location_table = setup_locations(self.options)



    def generate_seed(self):
        generator: MapGenerator = MapGenerator(self.randomizer_data, self.existing_randomizer_args, set(self.location_table.keys()), self.world)
        self.allocation, _ = generator.generate_seed()

        self.picked_templates = { template.name for template in self.allocation.picked_templates }
        self.map_transition_shuffle_order = [self.randomizer_data.walking_left_transitions.index(x) for x in self.allocation.walking_left_transitions]
        self.start_location = data.get_region_ap_name(self.allocation.start_location.location)


    def generate_set_seed(self):
        self.picked_templates = set(self.world.picked_templates)
        self.map_transition_shuffle_order = self.world.map_transition_shuffle_order
        self.start_location = self.world.start_location

        existing_rando_start_location = data.get_region_by_ap_name(self.world.start_location).logic_key
        self.allocation = MapAllocation(self.randomizer_data, self.existing_randomizer_args, self.world.random)
        self.allocation.construct_set_seed(
            self.randomizer_data,
            self.existing_randomizer_args,
            self.picked_templates,
            self.map_transition_shuffle_order,
            existing_rando_start_location)


    def _get_region(self, region_name: str):
        return self.world.get_region(region_name)


    def _region_filter(self, region: RegionData) -> bool:
        if not self.world.is_ut and self.options.knowledge < region.knowledge:
            return False

        if not self.world.is_ut and self.options.trick_difficulty < region.trick_difficulty:
            return False

        # Include Plurkwood with UT, as the player could recruit Keke Bunny out of logic
        if not self.world.is_ut and not bool(self.options.include_plurkwood.value) and region.requires_plurkwood:
            return False

        if not bool(self.options.include_warp_destination.value) and region.requires_warp_destination:
            return False

        if not (bool(self.options.include_post_game.value) or bool(self.options.include_post_irisu.value)) and region.requires_post_game:
            return False

        if not bool(self.options.include_post_irisu.value) and region.requires_post_irisu:
            return False

        if not bool(self.options.include_halloween.value) and region.requires_halloween:
            return False
        return True


    def set_regions(self):
        """
        This method defines the regions from the existing randomizer data.
        It will then add it to the AP world.

        These regions are connected in the connect_region method.

        :returns: None
        """
        menu = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu)

        for name in self.regions:
            region = Region(name, self.player, self.multiworld)
            self.multiworld.regions.append(region)


    def connect_regions(self):
        """
        This method will connect the regions defined in the set_regions method.
        That method MUST be called first!

        :returns: None
        """
        self.multiworld.get_region("Menu", self.player).connect(self.world.get_region(self.start_location))
        added_exits: set[str] = set()

        # Add Map Transitions
        for (idx, x) in enumerate(self.map_transition_shuffle_order):
            left = self.randomizer_data.walking_left_transitions[x]
            right = self.randomizer_data.walking_right_transitions[idx]
            left_name = data.get_region_by_logic_key(left.origin_location).name
            right_name = data.get_region_by_logic_key(right.origin_location).name

            ltr_entrance = f'{left_name} -> {right_name}'
            if ltr_entrance not in added_exits:
                added_exits.add(ltr_entrance)
                self._get_region(left_name).add_exits([right_name])

            rtl_entrance = f'{right_name} -> {left_name}'
            if rtl_entrance not in added_exits:
                self._get_region(right_name).add_exits([left_name])
                added_exits.add(rtl_entrance)

        # Parse logic into Rule Builder rules
        parse_connections()

        changes = {
            f"{change.from_region} -> {change.to_region}": change
            for constraint in data.constraints
            for change in constraint.changes
            if constraint.logic_key in self.picked_templates
        }

        for region in [r for r in data.regions if self._region_filter(r)]:
            from_location = region.name
            if from_location not in self.regions:
                continue

            for to_location, default_rule in region.connections.items():
                if to_location not in self.regions:
                    continue

                entrance_name = f'{from_location} -> {to_location}'
                rule = changes[entrance_name].rule if entrance_name in changes else default_rule

                # Ignore entrances already added by map transitions
                if entrance_name not in added_exits:
                    self._get_region(from_location).add_exits([to_location], { to_location: rule })
                    added_exits.add(entrance_name)


    def set_locations(self):
        """
        This method creates all of the item locations within the AP world, and appends it to the
        appropriate region. It will also add the access rule for these locations, sourced from the
        existing randomizer.

        :dict[str, int] location_name_to_id: Map for location name -> id number
        :returns int: The total number of locations
        """
        total_locations = 0
        existing_randomizer_locations = self.randomizer_data.item_constraints

        found_locations = set()

        for location in existing_randomizer_locations:
            # Note that access rules are always attached to a region, not to a location.
            # If a location requires access rules, a separate region is created to contain the location.
            # This is for two reasons:
            # - The access rules are directly parsed from the existing randomizer, which handles logic this way.
            # - Some locations are treated as regions, as there are multiple ways to reach these locations.
            location_data = data.get_location_by_logic_key(location.item)
            location_name = location_data.name
            region_name = location_data.name if location_data.has_region else data.get_region_ap_name(location.from_location)

            if (location_name not in self.location_table):
                continue

            if (location_name not in found_locations):
                found_locations.add(location_name)

            region = self._get_region(region_name)
            ap_location = RabiRibiLocation(
                self.player,
                location_name,
                self.location_table[location_name],
                region
            )

            region.locations.append(ap_location)
            total_locations += 1

        return total_locations


    def set_events(self):
        self.add_event("Boost Unlocked", LocationName.beach_main)
        self.add_event("Shop Reachable", LocationName.town_shop)

        self.add_event(ItemName.ashuri_2, LocationName.riverbank_level3)
        self.add_event(ItemName.cocoa_1, LocationName.forest_cocoa_room)
        self.add_event(ItemName.kotri_1, LocationName.park_kotri)
        self.add_event(ItemName.kotri_2, LocationName.graveyard_kotri)
        self.add_event(ItemName.seana_1, LocationName.aquarium_east)
        self.add_event(ItemName.rita_recruit, LocationName.snowland_rita)
        self.add_event(ItemName.cicini_recruit, LocationName.spectral_cicini_room)
        self.add_event(ItemName.syaro_recruit, LocationName.system_interior_main)
        self.add_event(ItemName.pandora_recruit, LocationName.pyramid_main)
        self.add_event(ItemName.aruraune_recruit, LocationName.forest_night_west)
        self.add_event(ItemName.vanilla_recruit, LocationName.sky_bridge_east_lower)

        self.add_event(ItemName.cocoa_recruit, LocationName.cave_cocoa, can_recruit_cocoa)
        self.add_event(ItemName.ashuri_recruit, LocationName.spectral_west, can_recruit_ashuri)
        self.add_event(ItemName.saya_recruit, LocationName.evernight_saya, can_recruit_saya)
        self.add_event(ItemName.nieve_recruit, LocationName.palace_level_5, can_recruit_nieve_and_nixie)
        self.add_event(ItemName.nixie_recruit, LocationName.icy_summit_nixie, can_recruit_nieve_and_nixie)
        self.add_event(ItemName.seana_recruit, LocationName.park_town_entrance, can_recruit_seana)
        self.add_event(ItemName.lilith_recruit, LocationName.sky_island_main, can_recruit_lilith)
        self.add_event(ItemName.chocolate_recruit, LocationName.ravine_chocolate, can_recruit_chocolate)
        self.add_event(ItemName.kotri_recruit, LocationName.volcanic_main, can_recruit_kotri)

        # Note: While out of logic, the player could go to Plurkwood to recruit Keke Bunny
        if self.options.include_plurkwood or self.world.is_ut:
            self.add_event(ItemName.keke_bunny_recruit, LocationName.plurkwood_main, can_recruit_keke_bunny)

        self.add_event("Chapter 1", LocationName.town_main)
        self.add_event("Chapter 2", LocationName.town_main, can_reach_chapter_2)
        self.add_event("Chapter 3", LocationName.town_main, can_reach_chapter_3)
        self.add_event("Chapter 4", LocationName.town_main, can_reach_chapter_4)
        self.add_event("Chapter 5", LocationName.town_main, can_reach_chapter_5)

        if self.options.include_post_game.value or self.options.include_post_irisu.value:
            self.add_event(ItemName.miriam_recruit, LocationName.hall_of_memories)
            self.add_event(ItemName.rumi_recruit, LocationName.forgotten_cave_2)
            self.add_event(ItemName.irisu_recruit, LocationName.library_irisu, can_recruit_irisu)
            self.add_event("Chapter 6", LocationName.town_main, can_reach_chapter_6)
            self.add_event("Chapter 7", LocationName.town_main, can_reach_chapter_7)


    def add_event(self, event_name: str, region_key: str, rule: Rule| Macro = rules.True_()):
        """Places a locked item to represent an in-game event."""
        region_name = data.get_region_ap_name(region_key)
        event = RabiRibiLocation(self.player, event_name, None, self._get_region(region_name))
        event.place_locked_item(RabiRibiItem(event_name, ItemClassification.progression, None, self.player))
        self._get_region(region_name).locations.append(event)
        if rule is not None:
            self.world.set_rule(event, rule)


    def configure_slot_data(self):
        self.world.picked_templates = [template.name for template in self.allocation.picked_templates]
        self.world.map_transition_shuffle_order = self.map_transition_shuffle_order
        self.world.start_location = self.start_location


    def configure_region_spoiler_log_data(self):
        self.world.map_transition_shuffle_spoiler = []
        for (idx, x) in enumerate(self.map_transition_shuffle_order):
            left = self.randomizer_data.walking_left_transitions[x]
            right = self.randomizer_data.walking_right_transitions[idx]
            left_name = data.get_region_by_logic_key(left.origin_location).name
            right_name = data.get_region_by_logic_key(right.origin_location).name

            # Left and Right are the walking directions
            # meaning that the walking right region is left of the walking left region
            self.world.map_transition_shuffle_spoiler.append(f'{right_name} <=> {left_name}')
