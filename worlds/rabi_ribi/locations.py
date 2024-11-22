"""This module represents location definitions for Rabi-Ribi"""
from BaseClasses import Location, Region, MultiWorld, ItemClassification
from worlds.generic.Rules import add_rule
from .names import ItemName
from .items import RabiRibiItem
from .existing_randomizer.dataparser import RandomizerData
from .existing_randomizer.randomizer import parse_args
from .logic_helpers import (
    convert_existing_rando_name_to_ap_name,
    convert_existing_rando_rule_to_ap_rule,
)
from .names import LocationName
import worlds.rabi_ribi.logic_helpers as logic

class RabiRibiLocation(Location):
    """Rabi Ribi Location Definition"""
    game: str = "Rabi-Ribi"

class RegionDef:
    """
    This class provides methods associated with defining and connecting regions, locations,
    and the access rules for those regions and locations.
    """

    def __init__(self, multiworld: MultiWorld, player: int, options):
        existing_randomizer_args = self._convert_options_to_existing_randomizer_args(options)
        self.randomizer_data = RandomizerData(existing_randomizer_args)
        self.player = player
        self.multiworld = multiworld
        self.options = options

    def _convert_options_to_existing_randomizer_args(self, options):
        args = parse_args()
        args.open_mode = options.open_mode.value
        return args

    def set_regions(self):
        """
        This method defines the regions from the existing randomizer data.
        It will then add it to the AP world.

        These regions are connected in the connect_region method.

        :returns: None
        """
        region_names = self._get_region_name_list()
        for name in region_names:
            self.multiworld.regions.append(Region(name, self.player, self.multiworld))
        self.multiworld.regions.append(Region("Menu", self.player, self.multiworld))

    def connect_regions(self):
        """
        This method will connect the regions defined in the set_regions method.
        That method MUST be called first!

        :returns: None
        """
        regions = self.multiworld.regions.region_cache[self.player]
        regions["Menu"].connect(regions[LocationName.forest_start])
        edge_constraints = self.randomizer_data.edge_constraints
        for edge in edge_constraints:
            rule = convert_existing_rando_rule_to_ap_rule(edge.prereq_expression, self.player, regions, self.options)
            from_location = convert_existing_rando_name_to_ap_name(edge.from_location)
            to_location = convert_existing_rando_name_to_ap_name(edge.to_location)
            if from_location == LocationName.forest_start and to_location == LocationName.beach_forest_entrance:
                # add this later manually, this rule is for event_warp rando which isnt implemented yet.
                continue
            regions[from_location].add_exits([to_location], {
                to_location: rule
            })
        edge_constraints_2 = self.randomizer_data.initial_edges
        for edge in edge_constraints_2:
            rule = convert_existing_rando_rule_to_ap_rule(edge.satisfied_expr, self.player, regions, self.options)
            from_location = convert_existing_rando_name_to_ap_name(edge.from_location)
            to_location = convert_existing_rando_name_to_ap_name(edge.to_location)
            regions[from_location].add_exits([to_location], {
                to_location: rule
            })

        # Set map transitions manually, since these are defined in a
        #   non-AP-translatable way in the existing randomizer.
        regions[LocationName.forest_start].connect(regions[LocationName.beach_forest_entrance])
        regions[LocationName.beach_forest_entrance].connect(regions[LocationName.forest_start])

        regions[LocationName.forest_upper_riverbank_exit].connect(regions[LocationName.riverbank_main_level1])
        regions[LocationName.riverbank_main_level1].connect(regions[LocationName.forest_upper_riverbank_exit])

        regions[LocationName.forest_lower_riverbank_exit].connect(regions[LocationName.riverbank_lower_forest_entrance])
        regions[LocationName.riverbank_lower_forest_entrance].connect(regions[LocationName.forest_lower_riverbank_exit])

        regions[LocationName.spectral_west].connect(regions[LocationName.volcanic_main])
        regions[LocationName.volcanic_main].connect(regions[LocationName.spectral_west])

        regions[LocationName.graveyard_top_of_bridge].connect(regions[LocationName.sky_bridge_east])
        regions[LocationName.sky_bridge_east].connect(regions[LocationName.graveyard_top_of_bridge])

        regions[LocationName.graveyard_main].connect(regions[LocationName.sky_bridge_east_lower])
        regions[LocationName.sky_bridge_east_lower].connect(regions[LocationName.graveyard_main])

        regions[LocationName.beach_main].connect(regions[LocationName.ravine_beach_entrance])
        regions[LocationName.ravine_beach_entrance].connect(regions[LocationName.beach_main])

        regions[LocationName.beach_volcanic_entrance].connect(regions[LocationName.volcanic_beach_entrance])
        regions[LocationName.volcanic_beach_entrance].connect(regions[LocationName.beach_volcanic_entrance])

        regions[LocationName.beach_underwater_entrance].connect(regions[LocationName.aquarium_beach_entrance])
        regions[LocationName.aquarium_beach_entrance].connect(regions[LocationName.beach_underwater_entrance])

        regions[LocationName.park_main].connect(regions[LocationName.snowland_east])
        regions[LocationName.snowland_east].connect(regions[LocationName.park_main])

        regions[LocationName.park_town_entrance].connect(regions[LocationName.town_main])
        regions[LocationName.town_main].connect(regions[LocationName.park_town_entrance])

        regions[LocationName.ravine_town_entrance].connect(regions[LocationName.town_main])
        regions[LocationName.town_main].connect(regions[LocationName.ravine_town_entrance])

        regions[LocationName.snowland_evernight_entrance].connect(regions[LocationName.evernight_lower])
        regions[LocationName.evernight_lower].connect(regions[LocationName.snowland_evernight_entrance])

    def set_locations(self, location_name_to_id):
        """
        This method creates all of the item locations within the AP world, and appends it to the
        appropriate region. It will also add the access rule for these locations, sourced from the
        existing randomizer.

        :dict[str, int] location_name_to_id: Map for location name -> id number
        :returns int: The total number of locations
        """
        total_locations = 0
        locations = self.randomizer_data.item_constraints
        regions = self.multiworld.regions.region_cache[self.player]
        for location in locations:

            # exlcude post game
            prereq_expr = str(location.entry_prereq_expr)
            if "POST_GAME_ALLOWED" in prereq_expr:
                continue
            if "POST_IRISU_ALLOWED" in prereq_expr:
                continue
            if "HALLOWEEN_REACHABLE" in prereq_expr:
                continue
            if "PLURKWOOD_REACHABLE" in prereq_expr:
                continue
            if "WARP_DESTINATION_REACHABLE" in prereq_expr:
                continue
            if "EVENT_WARPS_REQUIRED" in prereq_expr:
                continue

            # Note that location rules are always baked into the entry / exit requirements of the region.
            # Its done this way because this is the way the original randomizer did it.
            # Items which have an access requirement specific to that region have their own region node.
            location_name = convert_existing_rando_name_to_ap_name(location.item)
            region_name = f"Item {location_name}" if f"Item {location_name}" in regions else \
                convert_existing_rando_name_to_ap_name(location.from_location)
            location_name = convert_existing_rando_name_to_ap_name(location.item)
            ap_location = RabiRibiLocation(
                self.player,
                location_name,
                location_name_to_id[location_name],
                regions[region_name]
            )
            regions[region_name].locations.append(ap_location)
            total_locations += 1
        return total_locations

    def set_events(self):
        regions = self.multiworld.regions.region_cache[self.player]

        cocoa_1 = RabiRibiLocation(self.player, ItemName.cocoa_1, None, regions[LocationName.forest_cocoa_room])
        cocoa_1.place_locked_item(RabiRibiItem(ItemName.cocoa_1, ItemClassification.progression, None, self.player))
        regions[LocationName.forest_cocoa_room].locations.append(cocoa_1)

        kotri_1 = RabiRibiLocation(self.player, ItemName.kotri_1, None, regions[LocationName.park_kotri])
        kotri_1.place_locked_item(RabiRibiItem(ItemName.kotri_1, ItemClassification.progression, None, self.player))
        regions[LocationName.park_kotri].locations.append(kotri_1)

        kotri_2 = RabiRibiLocation(self.player, ItemName.kotri_2, None, regions[LocationName.graveyard_kotri])
        kotri_2.place_locked_item(RabiRibiItem(ItemName.kotri_2, ItemClassification.progression, None, self.player))
        regions[LocationName.graveyard_kotri].locations.append(kotri_2)
        add_rule(kotri_2, lambda state: state.has(ItemName.kotri_1, self.player))

        cocoa_recruit = RabiRibiLocation(self.player, ItemName.cocoa_recruit, None, regions[LocationName.cave_cocoa])
        cocoa_recruit.place_locked_item(RabiRibiItem(ItemName.cocoa_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.cave_cocoa].locations.append(cocoa_recruit)
        add_rule(cocoa_recruit, lambda state: logic.can_recruit_cocoa(state, self.player))

        ashuri_recruit = RabiRibiLocation(self.player, ItemName.ashuri_recruit, None, regions[LocationName.spectral_west])
        ashuri_recruit.place_locked_item(RabiRibiItem(ItemName.ashuri_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.spectral_west].locations.append(ashuri_recruit)
        add_rule(ashuri_recruit, lambda state: logic.can_recruit_ashuri(state, self.player))

        rita_recruit = RabiRibiLocation(self.player, ItemName.rita_recruit, None, regions[LocationName.snowland_rita])
        rita_recruit.place_locked_item(RabiRibiItem(ItemName.rita_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.snowland_rita].locations.append(rita_recruit)
        add_rule(rita_recruit, lambda state: logic.can_recruit_rita(state, self.player))

        cicini_recruit = RabiRibiLocation(self.player, ItemName.cicini_recruit, None, regions[LocationName.spectral_cicini_room])
        cicini_recruit.place_locked_item(RabiRibiItem(ItemName.cicini_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.spectral_cicini_room].locations.append(cicini_recruit)
        add_rule(cicini_recruit, lambda state: logic.can_recruit_cicini(state, self.player))

        saya_recruit = RabiRibiLocation(self.player, ItemName.saya_recruit, None, regions[LocationName.evernight_saya])
        saya_recruit.place_locked_item(RabiRibiItem(ItemName.saya_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.evernight_saya].locations.append(saya_recruit)
        add_rule(saya_recruit, lambda state: logic.can_recruit_saya(state, self.player))

        syaro_recruit = RabiRibiLocation(self.player, ItemName.syaro_recruit, None, regions[LocationName.system_interior_main])
        syaro_recruit.place_locked_item(RabiRibiItem(ItemName.syaro_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.system_interior_main].locations.append(syaro_recruit)
        add_rule(syaro_recruit, lambda state: logic.can_recruit_syaro(state, self.player))

        pandora_recruit = RabiRibiLocation(self.player, ItemName.pandora_recruit, None, regions[LocationName.pyramid_main])
        pandora_recruit.place_locked_item(RabiRibiItem(ItemName.pandora_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.pyramid_main].locations.append(pandora_recruit)
        add_rule(pandora_recruit, lambda state: logic.can_recruit_pandora(state, self.player))

        nieve_recruit = RabiRibiLocation(self.player, ItemName.nieve_recruit, None, regions[LocationName.palace_level_5])
        nieve_recruit.place_locked_item(RabiRibiItem(ItemName.nieve_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.palace_level_5].locations.append(nieve_recruit)
        add_rule(nieve_recruit, lambda state: logic.can_recruit_nieve(state, self.player))

        nixie_recruit = RabiRibiLocation(self.player, ItemName.nixie_recruit, None, regions[LocationName.icy_summit_nixie])
        nixie_recruit.place_locked_item(RabiRibiItem(ItemName.nixie_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.icy_summit_nixie].locations.append(nixie_recruit)
        add_rule(nixie_recruit, lambda state: logic.can_recruit_nixie(state, self.player))

        aruraune_recruit = RabiRibiLocation(self.player, ItemName.aruraune_recruit, None, regions[LocationName.forest_night_west])
        aruraune_recruit.place_locked_item(RabiRibiItem(ItemName.aruraune_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.forest_night_west].locations.append(aruraune_recruit)
        add_rule(aruraune_recruit, lambda state: logic.can_recruit_aruraune(state, self.player))

        seana_recruit = RabiRibiLocation(self.player, ItemName.seana_recruit, None, regions[LocationName.park_town_entrance])
        seana_recruit.place_locked_item(RabiRibiItem(ItemName.seana_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.park_town_entrance].locations.append(seana_recruit)
        add_rule(seana_recruit, lambda state: logic.can_recruit_seana(state, self.player))

        lilith_recruit = RabiRibiLocation(self.player, ItemName.lilith_recruit, None, regions[LocationName.sky_island_main])
        lilith_recruit.place_locked_item(RabiRibiItem(ItemName.lilith_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.sky_island_main].locations.append(lilith_recruit)
        add_rule(lilith_recruit, lambda state: logic.can_recruit_lilith(state, self.player))

        vanilla_recruit = RabiRibiLocation(self.player, ItemName.vanilla_recruit, None, regions[LocationName.sky_bridge_east_lower])
        vanilla_recruit.place_locked_item(RabiRibiItem(ItemName.vanilla_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.sky_bridge_east_lower].locations.append(vanilla_recruit)
        add_rule(vanilla_recruit, lambda state: logic.can_recruit_chocolate(state, self.player))

        chocolate_recruit = RabiRibiLocation(self.player, ItemName.chocolate_recruit, None, regions[LocationName.ravine_chocolate])
        chocolate_recruit.place_locked_item(RabiRibiItem(ItemName.chocolate_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.ravine_chocolate].locations.append(chocolate_recruit)
        add_rule(chocolate_recruit, lambda state: logic.can_recruit_chocolate(state, self.player))

        kotri_recruit = RabiRibiLocation(self.player, ItemName.kotri_recruit, None, regions[LocationName.volcanic_main])
        kotri_recruit.place_locked_item(RabiRibiItem(ItemName.kotri_recruit, ItemClassification.progression, None, self.player))
        regions[LocationName.volcanic_main].locations.append(kotri_recruit)
        add_rule(kotri_recruit, lambda state: logic.can_recruit_kotri(state, self.player))

        # keke_bunny_recruit = RabiRibiLocation(self.player, ItemName.keke_bunny_recruit, None, regions[LocationName.plurkwood_main])
        # keke_bunny_recruit.place_locked_item(RabiRibiItem(ItemName.keke_bunny_recruit, ItemClassification.progression, None, self.player))
        # regions[LocationName.plurkwood_main].locations.append(keke_bunny_recruit)
        # add_rule(keke_bunny_recruit, lambda state: logic.can_recruit_keke_bunny(state, self.player))

        chapter_1 = RabiRibiLocation(self.player, "Chapter 1", None, regions[LocationName.town_main])
        chapter_1.place_locked_item(RabiRibiItem("Chapter 1", ItemClassification.progression, None, self.player))
        regions[LocationName.town_main].locations.append(chapter_1)
        add_rule(chapter_1, lambda state: logic.can_reach_chapter_1(state, self.player))

        chapter_2 = RabiRibiLocation(self.player, "Chapter 2", None, regions[LocationName.town_main])
        chapter_2.place_locked_item(RabiRibiItem("Chapter 2", ItemClassification.progression, None, self.player))
        regions[LocationName.town_main].locations.append(chapter_2)
        add_rule(chapter_2,
                 lambda state: logic.can_reach_chapter_2(state, self.player) and
                    state.has("Chapter 1", self.player))

        chapter_3 = RabiRibiLocation(self.player, "Chapter 3", None, regions[LocationName.town_main])
        chapter_3.place_locked_item(RabiRibiItem("Chapter 3", ItemClassification.progression, None, self.player))
        regions[LocationName.town_main].locations.append(chapter_3)
        add_rule(chapter_3,
                 lambda state: logic.can_reach_chapter_3(state, self.player) and
                    state.has("Chapter 2", self.player))

        chapter_4 = RabiRibiLocation(self.player, "Chapter 4", None, regions[LocationName.town_main])
        chapter_4.place_locked_item(RabiRibiItem("Chapter 4", ItemClassification.progression, None, self.player))
        regions[LocationName.town_main].locations.append(chapter_4)
        add_rule(chapter_4,
                 lambda state: logic.can_reach_chapter_4(state, self.player) and
                    state.has("Chapter 3", self.player))

        chapter_5 = RabiRibiLocation(self.player, "Chapter 5", None, regions[LocationName.town_main])
        chapter_5.place_locked_item(RabiRibiItem("Chapter 5", ItemClassification.progression, None, self.player))
        regions[LocationName.town_main].locations.append(chapter_5)
        add_rule(chapter_5,
                 lambda state: logic.can_reach_chapter_5(state, self.player) and
                    state.has("Chapter 4", self.player))

        bunny_strike = RabiRibiLocation(self.player, ItemName.bunny_strike, None, regions[LocationName.town_main])
        bunny_strike.place_locked_item(RabiRibiItem(ItemName.bunny_strike, ItemClassification.progression, None, self.player))
        regions[LocationName.town_main].locations.append(bunny_strike)

        speed_boost = RabiRibiLocation(self.player, ItemName.speed_boost, None, regions[LocationName.town_main])
        speed_boost.place_locked_item(RabiRibiItem(ItemName.speed_boost, ItemClassification.progression, None, self.player))
        regions[LocationName.town_main].locations.append(speed_boost)

    def _get_region_name_list(self):
        return [
            convert_existing_rando_name_to_ap_name(name) for \
            name in self.randomizer_data.graph_vertices
        ]

def get_all_possible_locations():
    """
    This method retrieves a list of all locations in Rabi-Ribi. This is needed when instantiating the world.

    :returns: A full list of location names.
    """
    # Default args for now
    args = parse_args()

    # Grab items from existing randomizer logic
    randomizer_data = RandomizerData(args)  # Kind of hacky. I dont really want to instantiate twice but
                                            #   this needs to be done before the RabiRibiWorld __init__ runs.
                                            #   This is also instantiated in the RegionDef class above.
    location_list = randomizer_data.item_constraints

    # convert it to the ap name equivilant and return
    return [convert_existing_rando_name_to_ap_name(location.item) for location in location_list]
