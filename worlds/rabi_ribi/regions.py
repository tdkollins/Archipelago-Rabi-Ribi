"""This module represents region definitions for Rabi-Ribi"""
import logging

from typing import TYPE_CHECKING, Any, Dict, List, Set
from BaseClasses import Region, MultiWorld, ItemClassification
from worlds.generic.Rules import add_rule
from . import logic_helpers as logic
from .entrance_shuffle import MapAllocation, MapGenerator
from .existing_randomizer.dataparser import RandomizerData
from .existing_randomizer.randomizer import parse_args
from .existing_randomizer.utility import GraphEdge
from .items import RabiRibiItem
from .locations import RabiRibiLocation, all_locations, setup_locations
from .logic_helpers import (
    convert_existing_rando_name_to_ap_name,
    convert_existing_rando_rule_to_ap_rule,
)
from .names import ItemName, LocationName
from .options import RabiRibiOptions

if TYPE_CHECKING:
    from . import RabiRibiWorld

logger = logging.getLogger("Rabi-Ribi")

# TODO: Move these region names
plurkwood_regions: Set[str] = {
    "Plurkwood Main",
    "Item Egg Plurk East",
    "Item Egg Plurk Cave",
    "Item Egg Plurk Cats"
}

warp_destination_regions: Set[str] = {
    "Item Egg Crespirit",
    "Item Egg Hospital Wall",
    "Item Egg Hospital Box"
}

halloween_regions: Set[str] = {
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

post_game_regions: Set[str] = {
    "Unreachable Location",
    "Item Blessed",
    "Item Auto Trigger",
    "Item Hitbox Down",
    "Item Ribbon Badge",
    "Item Erina Badge",
    "Item Carrot Shooter",
    "Item Cyber Flower",
    "Item Egg Rumi",
    "Item Egg Library",
    "Item Egg Memories Sysint",
    "Item Egg Memories Ravine",
    "Item Egg Sysint2"
}

class RegionDef:
    """
    This class provides methods associated with defining and connecting regions, locations,
    and the access rules for those regions and locations.
    """
    regions: Set[str] = set()
    location_table: Dict[str, int]
    unreachable_regions: set[str]

    def __init__(self, multiworld: MultiWorld, player: int, options: RabiRibiOptions):
        self.player = player
        self.multiworld = multiworld
        self.options = options

        self.existing_randomizer_args: Any = self._convert_options_to_existing_randomizer_args(options)
        self.randomizer_data = RandomizerData(self.existing_randomizer_args)

        self.location_table = setup_locations(self.options)

    def generate_seed(self):
        generator: MapGenerator = MapGenerator(self.randomizer_data, self.existing_randomizer_args, set(self.location_table.keys()), self.multiworld.random)
        self.allocation, _ = generator.generate_seed()
        self.map_transition_shuffle_order = [self.randomizer_data.walking_left_transitions.index(x) for x in self.allocation.walking_left_transitions]

        self.picked_templates = self.allocation.picked_templates
        self.map_transition_shuffle_order = self.map_transition_shuffle_order

    def regenerate_seed_for_universal_tracker(self, passthrough: Dict[str, Any]):
        """
        This method utilizes Universal Tracker's re_gen_passthrough data to set variables that were randomly assigned
        when generating the seed to the same values that were used during seed generation.
        """
        self.picked_templates = passthrough["picked_templates"]
        self.map_transition_shuffle_order = passthrough["map_transition_shuffle_order"]
        self.generate_set_seed()

    def generate_set_seed(self):
        self.allocation = MapAllocation(self.randomizer_data, self.existing_randomizer_args, self.multiworld.random)
        self.allocation.construct_set_seed(self.randomizer_data, self.existing_randomizer_args, self.picked_templates, self.map_transition_shuffle_order)

    def _convert_options_to_existing_randomizer_args(self, options: RabiRibiOptions):
        args = parse_args()
        args.open_mode = options.open_mode.value
        args.shuffle_gift_items = options.randomize_gift_items.value
        args.shuffle_map_transitions = options.shuffle_map_transitions.value

        if options.enable_constraint_changes.value:
            args.constraint_changes = options.number_of_constraint_changes.value

        return args
    
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
        self.unreachable_regions = {
            *warp_destination_regions,
            *halloween_regions,
            *post_game_regions
        }

        if not self.options.plurkwood_reachable:
            self.unreachable_regions.update(plurkwood_regions)

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
        self.multiworld.get_region("Menu", self.player).connect(self._get_region(LocationName.forest_start))
    
        edge_constraints: List[GraphEdge] = self.allocation.edges

        added_exits: Set[str] = set()

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
                add_rule(self.multiworld.get_entrance(entrance_name, self.player), rule, combine = "or")
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

        if not self.options.randomize_gift_items:
            speed_boost = RabiRibiLocation(self.player, ItemName.speed_boost, all_locations[LocationName.speed_boost], self._get_region(LocationName.town_shop))
            self._get_region(LocationName.town_shop).locations.append(speed_boost)

            bunny_strike = RabiRibiLocation(self.player, ItemName.bunny_strike, all_locations[LocationName.bunny_strike], self._get_region(LocationName.town_shop))
            self._get_region(LocationName.town_shop).locations.append(bunny_strike)
            add_rule(bunny_strike, lambda state: state.has(ItemName.sliding_powder, self.player))
            total_locations += 2

            if self.options.plurkwood_reachable:
                p_hairpin = RabiRibiLocation(self.player, ItemName.p_hairpin, all_locations[LocationName.p_hairpin], self._get_region(LocationName.plurkwood_main))
                self._get_region(LocationName.plurkwood_main).locations.append(p_hairpin)
                add_rule(p_hairpin, lambda state: state.has(ItemName.keke_bunny_recruit, self.player))
                total_locations += 1

        return total_locations

    def set_events(self):
        cocoa_1 = RabiRibiLocation(self.player, ItemName.cocoa_1, None, self._get_region(LocationName.forest_cocoa_room))
        cocoa_1.place_locked_item(RabiRibiItem(ItemName.cocoa_1, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.forest_cocoa_room).locations.append(cocoa_1)

        kotri_1 = RabiRibiLocation(self.player, ItemName.kotri_1, None, self._get_region(LocationName.park_kotri))
        kotri_1.place_locked_item(RabiRibiItem(ItemName.kotri_1, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.park_kotri).locations.append(kotri_1)

        kotri_2 = RabiRibiLocation(self.player, ItemName.kotri_2, None, self._get_region(LocationName.graveyard_kotri))
        kotri_2.place_locked_item(RabiRibiItem(ItemName.kotri_2, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.graveyard_kotri).locations.append(kotri_2)
        add_rule(kotri_2, lambda state: state.has(ItemName.kotri_1, self.player))

        cocoa_recruit = RabiRibiLocation(self.player, ItemName.cocoa_recruit, None, self._get_region(LocationName.cave_cocoa))
        cocoa_recruit.place_locked_item(RabiRibiItem(ItemName.cocoa_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.cave_cocoa).locations.append(cocoa_recruit)
        add_rule(cocoa_recruit, lambda state: logic.can_recruit_cocoa(state, self.player))

        ashuri_recruit = RabiRibiLocation(self.player, ItemName.ashuri_recruit, None, self._get_region(LocationName.spectral_west))
        ashuri_recruit.place_locked_item(RabiRibiItem(ItemName.ashuri_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.spectral_west).locations.append(ashuri_recruit)
        add_rule(ashuri_recruit, lambda state: logic.can_recruit_ashuri(state, self.player))

        rita_recruit = RabiRibiLocation(self.player, ItemName.rita_recruit, None, self._get_region(LocationName.snowland_rita))
        rita_recruit.place_locked_item(RabiRibiItem(ItemName.rita_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.snowland_rita).locations.append(rita_recruit)
        add_rule(rita_recruit, lambda state: logic.can_recruit_rita(state, self.player))

        cicini_recruit = RabiRibiLocation(self.player, ItemName.cicini_recruit, None, self._get_region(LocationName.spectral_cicini_room))
        cicini_recruit.place_locked_item(RabiRibiItem(ItemName.cicini_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.spectral_cicini_room).locations.append(cicini_recruit)
        add_rule(cicini_recruit, lambda state: logic.can_recruit_cicini(state, self.player))

        saya_recruit = RabiRibiLocation(self.player, ItemName.saya_recruit, None, self._get_region(LocationName.evernight_saya))
        saya_recruit.place_locked_item(RabiRibiItem(ItemName.saya_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.evernight_saya).locations.append(saya_recruit)
        add_rule(saya_recruit, lambda state: logic.can_recruit_saya(state, self.player))

        syaro_recruit = RabiRibiLocation(self.player, ItemName.syaro_recruit, None, self._get_region(LocationName.system_interior_main))
        syaro_recruit.place_locked_item(RabiRibiItem(ItemName.syaro_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.system_interior_main).locations.append(syaro_recruit)
        add_rule(syaro_recruit, lambda state: logic.can_recruit_syaro(state, self.player))

        pandora_recruit = RabiRibiLocation(self.player, ItemName.pandora_recruit, None, self._get_region(LocationName.pyramid_main))
        pandora_recruit.place_locked_item(RabiRibiItem(ItemName.pandora_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.pyramid_main).locations.append(pandora_recruit)
        add_rule(pandora_recruit, lambda state: logic.can_recruit_pandora(state, self.player))

        nieve_recruit = RabiRibiLocation(self.player, ItemName.nieve_recruit, None, self._get_region(LocationName.palace_level_5))
        nieve_recruit.place_locked_item(RabiRibiItem(ItemName.nieve_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.palace_level_5).locations.append(nieve_recruit)
        add_rule(nieve_recruit, lambda state: logic.can_recruit_nieve(state, self.player))

        nixie_recruit = RabiRibiLocation(self.player, ItemName.nixie_recruit, None, self._get_region(LocationName.icy_summit_nixie))
        nixie_recruit.place_locked_item(RabiRibiItem(ItemName.nixie_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.icy_summit_nixie).locations.append(nixie_recruit)
        add_rule(nixie_recruit, lambda state: logic.can_recruit_nixie(state, self.player))

        aruraune_recruit = RabiRibiLocation(self.player, ItemName.aruraune_recruit, None, self._get_region(LocationName.forest_night_west))
        aruraune_recruit.place_locked_item(RabiRibiItem(ItemName.aruraune_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.forest_night_west).locations.append(aruraune_recruit)
        add_rule(aruraune_recruit, lambda state: logic.can_recruit_aruraune(state, self.player))

        seana_recruit = RabiRibiLocation(self.player, ItemName.seana_recruit, None, self._get_region(LocationName.park_town_entrance))
        seana_recruit.place_locked_item(RabiRibiItem(ItemName.seana_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.park_town_entrance).locations.append(seana_recruit)
        add_rule(seana_recruit, lambda state: logic.can_recruit_seana(state, self.player))

        lilith_recruit = RabiRibiLocation(self.player, ItemName.lilith_recruit, None, self._get_region(LocationName.sky_island_main))
        lilith_recruit.place_locked_item(RabiRibiItem(ItemName.lilith_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.sky_island_main).locations.append(lilith_recruit)
        add_rule(lilith_recruit, lambda state: logic.can_recruit_lilith(state, self.player))

        vanilla_recruit = RabiRibiLocation(self.player, ItemName.vanilla_recruit, None, self._get_region(LocationName.sky_bridge_east_lower))
        vanilla_recruit.place_locked_item(RabiRibiItem(ItemName.vanilla_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.sky_bridge_east_lower).locations.append(vanilla_recruit)
        add_rule(vanilla_recruit, lambda state: logic.can_recruit_vanilla(state, self.player))

        chocolate_recruit = RabiRibiLocation(self.player, ItemName.chocolate_recruit, None, self._get_region(LocationName.ravine_chocolate))
        chocolate_recruit.place_locked_item(RabiRibiItem(ItemName.chocolate_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.ravine_chocolate).locations.append(chocolate_recruit)
        add_rule(chocolate_recruit, lambda state: logic.can_recruit_chocolate(state, self.player))

        kotri_recruit = RabiRibiLocation(self.player, ItemName.kotri_recruit, None, self._get_region(LocationName.volcanic_main))
        kotri_recruit.place_locked_item(RabiRibiItem(ItemName.kotri_recruit, ItemClassification.progression, None, self.player))
        self._get_region(LocationName.volcanic_main).locations.append(kotri_recruit)
        add_rule(kotri_recruit, lambda state: logic.can_recruit_kotri(state, self.player))

        if self.options.plurkwood_reachable:
            keke_bunny_recruit = RabiRibiLocation(self.player, ItemName.keke_bunny_recruit, None, self._get_region(LocationName.plurkwood_main))
            keke_bunny_recruit.place_locked_item(RabiRibiItem(ItemName.keke_bunny_recruit, ItemClassification.progression, None, self.player))
            self._get_region(LocationName.plurkwood_main).locations.append(keke_bunny_recruit)
            add_rule(keke_bunny_recruit, lambda state: logic.can_recruit_keke_bunny(state, self.player))

        chapter_1 = RabiRibiLocation(self.player, "Chapter 1", None, self._get_region(LocationName.town_main))
        chapter_1.place_locked_item(RabiRibiItem("Chapter 1", ItemClassification.progression, None, self.player))
        self._get_region(LocationName.town_main).locations.append(chapter_1)
        add_rule(chapter_1, lambda state: logic.can_reach_chapter_1(state, self.player))

        chapter_2 = RabiRibiLocation(self.player, "Chapter 2", None, self._get_region(LocationName.town_main))
        chapter_2.place_locked_item(RabiRibiItem("Chapter 2", ItemClassification.progression, None, self.player))
        self._get_region(LocationName.town_main).locations.append(chapter_2)
        add_rule(chapter_2,
                 lambda state: logic.can_reach_chapter_2(state, self.player) and
                    state.has("Chapter 1", self.player))

        chapter_3 = RabiRibiLocation(self.player, "Chapter 3", None, self._get_region(LocationName.town_main))
        chapter_3.place_locked_item(RabiRibiItem("Chapter 3", ItemClassification.progression, None, self.player))
        self._get_region(LocationName.town_main).locations.append(chapter_3)
        add_rule(chapter_3,
                 lambda state: logic.can_reach_chapter_3(state, self.player) and
                    state.has("Chapter 2", self.player))

        chapter_4 = RabiRibiLocation(self.player, "Chapter 4", None, self._get_region(LocationName.town_main))
        chapter_4.place_locked_item(RabiRibiItem("Chapter 4", ItemClassification.progression, None, self.player))
        self._get_region(LocationName.town_main).locations.append(chapter_4)
        add_rule(chapter_4,
                 lambda state: logic.can_reach_chapter_4(state, self.player) and
                    state.has("Chapter 3", self.player))

        chapter_5 = RabiRibiLocation(self.player, "Chapter 5", None, self._get_region(LocationName.town_main))
        chapter_5.place_locked_item(RabiRibiItem("Chapter 5", ItemClassification.progression, None, self.player))
        self._get_region(LocationName.town_main).locations.append(chapter_5)
        add_rule(chapter_5,
                 lambda state: logic.can_reach_chapter_5(state, self.player) and
                    state.has("Chapter 4", self.player))

    def configure_slot_data(self, world: "RabiRibiWorld"):
        world.picked_templates = [template.name for template in self.allocation.picked_templates]
        world.map_transition_shuffle_order = self.map_transition_shuffle_order

    def configure_region_spoiler_log_data(self, world: "RabiRibiWorld"):
        world.map_transition_shuffle_spoiler = []
        for (idx, x) in enumerate(self.map_transition_shuffle_order):
            left = self.randomizer_data.walking_left_transitions[x]
            right = self.randomizer_data.walking_right_transitions[idx]
            left_name = convert_existing_rando_name_to_ap_name(left.origin_location)
            right_name = convert_existing_rando_name_to_ap_name(right.origin_location)
            world.map_transition_shuffle_spoiler.append(f'{left_name} -> {right_name}')

    def _get_region_name_list(self):
        return [
            convert_existing_rando_name_to_ap_name(name) for \
            name in self.randomizer_data.graph_vertices
        ]