"""This module represents region definitions for Rabi-Ribi"""
import logging

from typing import Any, Optional
from BaseClasses import Region, ItemClassification
from rule_builder.rules import Rule
from . import logic_helpers as logic
from .bases import RabiRibiWorldBase
from .constants import GAME_NAME
from .entrance_shuffle import MapAllocation, MapGenerator
from .existing_randomizer.utility import GraphEdge
from .items import RabiRibiItem
from .locations import RabiRibiLocation, setup_locations
from .logic_helpers import convert_existing_rando_rule_to_ap_rule
from .names import ItemName, LocationName
from .options import Knowledge, TrickDifficulty
from .utility import (
    convert_existing_rando_name_to_ap_name,
    convert_ap_name_to_existing_rando_name
)

logger = logging.getLogger(GAME_NAME)

# TODO: Move these region names
plurkwood_regions: set[str] = {
    "Plurkwood Main",
    "Item P Hairpin",
    "Item Egg Plurk East",
    "Item Egg Plurk Cave",
    "Item Egg Plurk Cats"
}

warp_destination_regions: set[str] = {
    "Warp Destination Hospital",
    "Warp Destination Outside",
    "Item Egg Crespirit",
    "Item Egg Hospital Wall",
    "Item Egg Hospital Box"
}

post_game_regions: set[str] = {
    "Unreachable Location",
    "Forgotten Cave 2",
    "Hall Of Memories",
    "Library Alcove Ledge",
    "Library Bottom",
    "Library Entrance",
    "Library Irisu",
    "Library Mid Lower",
    "Library Mid Upper",
    "Sysint2 Egg Room",
    "Sysint2 End",
    "Sysint2 Start",
    "Item Blessed",
    "Item Auto Trigger",
    "Item Hitbox Down",
    "Item Carrot Shooter",
    "Item Cyber Flower",
    "Item Egg Rumi",
    "Item Egg Library",
    "Item Egg Memories Sysint",
    "Item Egg Memories Ravine",
    "Item Egg Memories Cars Room",
    "Item Egg Sysint2",
    "Item Egg Sysint2 Long Jump"
}

post_irisu_regions: set[str] = {
    "Item Ribbon Badge",
    "Item Erina Badge",
}

halloween_regions: set[str] = {
    "Halloween Central",
    "Halloween Dark Shaft",
    "Halloween Exit",
    "Halloween Flooded",
    "Halloween Past Pillars",
    "Halloween Pumpkin Hall",
    "Halloween Upper",
    "Item Egg Halloween Cicini Room",
    "Item Egg Halloween Left Pillar",
    "Item Egg Halloween Mid",
    "Item Egg Halloween Near Boss",
    "Item Egg Halloween Past Pillars1",
    "Item Egg Halloween Past Pillars2",
    "Item Egg Halloween Right Pillar",
    "Item Egg Halloween Sw Slide",
    "Item Egg Halloween Warp Zone",
    "Item Egg Halloween West"
}

# Impossible to reach without being on a high enough difficulty
# TODO: Ensure Library OOB is updated to only be reachable if Sky Island OOB is reachable.
adv_vhard_regions: set[str] = {
    "Sky Island Oob",
}

adv_vhard_post_game_regions: set[str] = {
    "Library Oob",
}

class RegionHelper:
    """
    This class provides methods associated with defining and connecting regions, locations,
    and the access rules for those regions and locations.
    """
    regions: set[str] = set()
    location_table: dict[str, int]
    unreachable_regions: set[str]

    def __init__(self, world: RabiRibiWorldBase):
        self.world = world
        self.player = self.world.player
        self.multiworld = self.world.multiworld
        self.options = self.world.options
        self.existing_randomizer_args: Any = self.world.existing_randomizer_args
        self.randomizer_data = self.world.randomizer_data

        self.location_table = setup_locations(self.options)

    def generate_seed(self):
        generator: MapGenerator = MapGenerator(self.randomizer_data, self.existing_randomizer_args, set(self.location_table.keys()), self.world)
        self.allocation, _ = generator.generate_seed()

        self.picked_templates = self.allocation.picked_templates
        self.map_transition_shuffle_order = [self.randomizer_data.walking_left_transitions.index(x) for x in self.allocation.walking_left_transitions]
        self.start_location = convert_existing_rando_name_to_ap_name(self.allocation.start_location.location)

    def generate_set_seed(self):
        existing_rando_start_location = convert_ap_name_to_existing_rando_name(self.start_location)
        self.allocation = MapAllocation(self.randomizer_data, self.existing_randomizer_args, self.world.random)
        self.allocation.construct_set_seed(self.randomizer_data, self.existing_randomizer_args, self.picked_templates, self.map_transition_shuffle_order, existing_rando_start_location)

    def _get_region(self, region_name: str):
        return self.multiworld.get_region(region_name, self.player)

    def set_regions(self):
        """
        This method defines the regions from the existing randomizer data.
        It will then add it to the AP world.

        These regions are connected in the connect_region method.

        :returns: None
        """
        menu = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu)
        self.regions.add("Menu")

        region_names = self._get_region_name_list()

        # Remove unreachable regions before adding to the graph
        self.unreachable_regions = set()

        if self.options.knowledge < Knowledge.option_advanced or \
            self.options.trick_difficulty < TrickDifficulty.option_v_hard or \
            self.world.is_ut:
            self.unreachable_regions.update(adv_vhard_regions)

        if self.options.knowledge < Knowledge.option_advanced or \
            self.options.trick_difficulty < TrickDifficulty.option_v_hard or \
            not self.options.include_post_game or \
            not self.world.is_ut:
            self.unreachable_regions.update(adv_vhard_post_game_regions)

        # Include Plurkwood with UT, as the player could recruit Keke Bunny out of logic
        if not self.options.include_plurkwood and \
            not self.world.is_ut:
            self.unreachable_regions.update(plurkwood_regions)

        if not self.options.include_warp_destination and \
            not self.options.include_post_game and \
            not self.options.include_post_irisu:
            self.unreachable_regions.update(warp_destination_regions)

        if not self.options.include_post_game and not self.options.include_post_irisu:
            self.unreachable_regions.update(post_game_regions)

        if not self.options.include_post_irisu:
            self.unreachable_regions.update(post_irisu_regions)

        if not self.options.include_halloween:
            self.unreachable_regions.update(halloween_regions)

        region_names = [r for r in region_names if r not in self.unreachable_regions]

        for name in region_names:
            region = Region(name, self.player, self.multiworld)
            self.multiworld.regions.append(region)
            self.regions.add(name)


    def connect_regions(self):
        """
        This method will connect the regions defined in the set_regions method.
        That method MUST be called first!

        :returns: None
        """
        self.multiworld.get_region("Menu", self.player).connect(self._get_region(self.start_location))
    
        edge_constraints: list[GraphEdge] = self.allocation.edges

        added_exits: set[str] = set()

        for edge in edge_constraints:
            rule = convert_existing_rando_rule_to_ap_rule(edge.satisfied_expr, self.player, self.regions, self.options)
            from_location = convert_existing_rando_name_to_ap_name(edge.from_location)
            to_location = convert_existing_rando_name_to_ap_name(edge.to_location)

            if from_location in self.unreachable_regions or to_location in self.unreachable_regions:
                continue

            if from_location == to_location:
                continue

            entrance_name = f'{from_location} -> {to_location}'

            if entrance_name in added_exits:
                self.world.set_rule(self.multiworld.get_entrance(entrance_name, self.player), rule)
            else:
                self._get_region(from_location).add_exits([to_location], {
                    to_location: rule
                })
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
            # Note that location rules are always baked into the entry / exit requirements of the region.
            # Its done this way because this is the way the original randomizer did it.
            # Items which have an access requirement specific to that region have their own region node.
            location_name = convert_existing_rando_name_to_ap_name(location.item)
            region_name = f"Item {location_name}" if f"Item {location_name}" in self.regions else \
                convert_existing_rando_name_to_ap_name(location.from_location)

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
        self.add_event("Boost Unlock", LocationName.beach_main)
        self.add_event("Shop Access", LocationName.town_shop)

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

        self.add_event(ItemName.cocoa_recruit, LocationName.cave_cocoa, logic.can_recruit_cocoa)
        self.add_event(ItemName.ashuri_recruit, LocationName.spectral_west, logic.can_recruit_ashuri)
        self.add_event(ItemName.saya_recruit, LocationName.evernight_saya, logic.can_recruit_saya)
        self.add_event(ItemName.nieve_recruit, LocationName.palace_level_5, logic.can_recruit_nieve_and_nixie)
        self.add_event(ItemName.nixie_recruit, LocationName.icy_summit_nixie, logic.can_recruit_nieve_and_nixie)
        self.add_event(ItemName.seana_recruit, LocationName.park_town_entrance, logic.can_recruit_seana)
        self.add_event(ItemName.lilith_recruit, LocationName.sky_island_main, logic.can_recruit_lilith)
        self.add_event(ItemName.chocolate_recruit, LocationName.ravine_chocolate, logic.can_recruit_chocolate)
        self.add_event(ItemName.kotri_recruit, LocationName.volcanic_main, logic.can_recruit_kotri)

        # Note: While out of logic, the player could go to Plurkwood to recruit Keke Bunny
        if self.options.include_plurkwood or self.world.is_ut:
            self.add_event(ItemName.keke_bunny_recruit, LocationName.plurkwood_main, logic.can_recruit_keke_bunny)

        self.add_event("Chapter 1", LocationName.town_main)
        self.add_event("Chapter 2", LocationName.town_main, logic.can_reach_chapter_2)
        self.add_event("Chapter 3", LocationName.town_main, logic.can_reach_chapter_3)
        self.add_event("Chapter 4", LocationName.town_main, logic.can_reach_chapter_4)
        self.add_event("Chapter 5", LocationName.town_main, logic.can_reach_chapter_5)

        if self.options.include_post_game.value or self.options.include_post_irisu.value:
            self.add_event(ItemName.miriam_recruit, LocationName.hall_of_memories)
            self.add_event(ItemName.rumi_recruit, LocationName.forgotten_cave_2)
            self.add_event(ItemName.irisu_recruit, LocationName.library_irisu, logic.can_recruit_irisu)
            self.add_event("Chapter 6", LocationName.town_main, logic.can_reach_chapter_6)
            self.add_event("Chapter 7", LocationName.town_main, logic.can_reach_chapter_7)

    def add_event(self, event_name: str, location_name: str, rule: Optional[Rule] = None):
        """Places a locked item to represent an in-game event."""
        event = RabiRibiLocation(self.player, event_name, None, self._get_region(location_name))
        event.place_locked_item(RabiRibiItem(event_name, ItemClassification.progression, None, self.player))
        self._get_region(location_name).locations.append(event)
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
            left_name = convert_existing_rando_name_to_ap_name(left.origin_location)
            right_name = convert_existing_rando_name_to_ap_name(right.origin_location)
            self.world.map_transition_shuffle_spoiler.append(f'{left_name} <=> {right_name}')

    def _get_region_name_list(self):
        return [convert_existing_rando_name_to_ap_name(name) \
            for name in self.randomizer_data.graph_vertices]
