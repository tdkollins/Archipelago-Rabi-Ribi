"""This module represents location definitions for Rabi-Ribi"""
from BaseClasses import Location, Region, MultiWorld, ItemClassification
from worlds.generic.Rules import add_rule
from worlds.rabi_ribi.items import RabiRibiItem
from worlds.rabi_ribi.existing_randomizer.dataparser import RandomizerData
from worlds.rabi_ribi.existing_randomizer.randomizer import parse_args
from worlds.rabi_ribi.logic_helpers import (
    convert_existing_rando_name_to_ap_name,
    convert_existing_rando_rule_to_ap_rule,
)
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
        regions["Menu"].connect(regions["Forest Start"])
        edge_constraints = self.randomizer_data.edge_constraints
        for edge in edge_constraints:
            rule = convert_existing_rando_rule_to_ap_rule(edge.prereq_expression, self.player, regions, self.options)
            from_location = convert_existing_rando_name_to_ap_name(edge.from_location)
            to_location = convert_existing_rando_name_to_ap_name(edge.to_location)
            if from_location == "Forest Start" and to_location == "Beach Forest Entrance":
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
        regions["Forest Start"].connect(regions["Beach Forest Entrance"])
        regions["Beach Forest Entrance"].connect(regions["Forest Start"])

        regions["Forest Upper Riverbank Exit"].connect(regions["Riverbank Main Level1"])
        regions["Riverbank Main Level1"].connect(regions["Forest Upper Riverbank Exit"])

        regions["Forest Lower Riverbank Exit"].connect(regions["Riverbank Lower Forest Entrance"])
        regions["Riverbank Lower Forest Entrance"].connect(regions["Forest Lower Riverbank Exit"])

        regions["Spectral West"].connect(regions["Volcanic Main"])
        regions["Volcanic Main"].connect(regions["Spectral West"])

        regions["Graveyard Top Of Bridge"].connect(regions["Sky Bridge East"])
        regions["Sky Bridge East"].connect(regions["Graveyard Top Of Bridge"])

        regions["Graveyard Main"].connect(regions["Sky Bridge East Lower"])
        regions["Sky Bridge East Lower"].connect(regions["Graveyard Main"])

        regions["Beach Main"].connect(regions["Ravine Beach Entrance"])
        regions["Ravine Beach Entrance"].connect(regions["Beach Main"])

        regions["Beach Volcanic Entrance"].connect(regions["Volcanic Beach Entrance"])
        regions["Volcanic Beach Entrance"].connect(regions["Beach Volcanic Entrance"])

        regions["Beach Underwater Entrance"].connect(regions["Aquarium Beach Entrance"])
        regions["Aquarium Beach Entrance"].connect(regions["Beach Underwater Entrance"])

        regions["Park Main"].connect(regions["Snowland East"])
        regions["Snowland East"].connect(regions["Park Main"])

        regions["Park Town Entrance"].connect(regions["Town Main"])
        regions["Town Main"].connect(regions["Park Town Entrance"])

        regions["Ravine Town Entrance"].connect(regions["Town Main"])
        regions["Town Main"].connect(regions["Ravine Town Entrance"])

        regions["Snowland Evernight Entrance"].connect(regions["Evernight Lower"])
        regions["Evernight Lower"].connect(regions["Snowland Evernight Entrance"])

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

        cocoa_1 = RabiRibiLocation(self.player, "Cocoa 1", None, regions["Forest Cocoa Room"])
        cocoa_1.place_locked_item(RabiRibiItem("Cocoa 1", ItemClassification.progression, None, self.player))
        regions["Forest Cocoa Room"].locations.append(cocoa_1)

        kotri_1 = RabiRibiLocation(self.player, "Kotri 1", None, regions["Park Kotri"])
        kotri_1.place_locked_item(RabiRibiItem("Kotri 1", ItemClassification.progression, None, self.player))
        regions["Park Kotri"].locations.append(kotri_1)

        kotri_2 = RabiRibiLocation(self.player, "Kotri 2", None, regions["Graveyard Kotri"])
        kotri_2.place_locked_item(RabiRibiItem("Kotri 2", ItemClassification.progression, None, self.player))
        regions["Graveyard Kotri"].locations.append(kotri_2)
        add_rule(kotri_2, lambda state: state.has("Kotri 1"), self.player)

        cocoa_recruit = RabiRibiLocation(self.player, "Cocoa Recruit", None, regions["Cave Cocoa"])
        cocoa_recruit.place_locked_item(RabiRibiItem("Cocoa Recruit", ItemClassification.progression, None, self.player))
        regions["Cave Cocoa"].locations.append(cocoa_recruit)
        add_rule(cocoa_recruit, lambda state: logic.can_recruit_cocoa(state, self.player))

        ashuri_recruit = RabiRibiLocation(self.player, "Ashuri Recruit", None, regions["Spectral West"])
        ashuri_recruit.place_locked_item(RabiRibiItem("Ashuri Recruit", ItemClassification.progression, None, self.player))
        regions["Spectral West"].locations.append(ashuri_recruit)
        add_rule(ashuri_recruit, lambda state: logic.can_recruit_ashuri(state, self.player))

        rita_recruit = RabiRibiLocation(self.player, "Rita Recruit", None, regions["Snowland Rita"])
        rita_recruit.place_locked_item(RabiRibiItem("Rita Recruit", ItemClassification.progression, None, self.player))
        regions["Spectral West"].locations.append(rita_recruit)
        add_rule(rita_recruit, lambda state: logic.can_recruit_rita(state, self.player))

        cicini_recruit = RabiRibiLocation(self.player, "Cicini Recruit", None, regions["Spectral Cicini Room"])
        cicini_recruit.place_locked_item(RabiRibiItem("Cicini Recruit", ItemClassification.progression, None, self.player))
        regions["Spectral Cicini Room"].locations.append(cicini_recruit)
        add_rule(cicini_recruit, lambda state: logic.can_recruit_cicini(state, self.player))

        saya_recruit = RabiRibiLocation(self.player, "Saya Recruit", None, regions["Evernight Saya"])
        saya_recruit.place_locked_item(RabiRibiItem("Saya Recruit", ItemClassification.progression, None, self.player))
        regions["Evernight Saya"].locations.append(saya_recruit)
        add_rule(saya_recruit, lambda state: logic.can_recruit_saya(state, self.player))

        syaro_recruit = RabiRibiLocation(self.player, "Syaro Recruit", None, regions["System Interior Main"])
        syaro_recruit.place_locked_item(RabiRibiItem("Syaro Recruit", ItemClassification.progression, None, self.player))
        regions["System Interior Main"].locations.append(syaro_recruit)
        add_rule(syaro_recruit, lambda state: logic.can_recruit_syaro(state, self.player))

        pandora_recruit = RabiRibiLocation(self.player, "Pandora Recruit", None, regions["Pyramid Main"])
        pandora_recruit.place_locked_item(RabiRibiItem("Pandora Recruit", ItemClassification.progression, None, self.player))
        regions["Pyramid Main"].locations.append(pandora_recruit)
        add_rule(pandora_recruit, lambda state: logic.can_recruit_pandora(state, self.player))

        nieve_recruit = RabiRibiLocation(self.player, "Nieve Recruit", None, regions["Palace Level 5"])
        nieve_recruit.place_locked_item(RabiRibiItem("Nieve Recruit", ItemClassification.progression, None, self.player))
        regions["Palace Level 5"].locations.append(nieve_recruit)
        add_rule(nieve_recruit, lambda state: logic.can_recruit_nieve(state, self.player))

        nixie_recruit = RabiRibiLocation(self.player, "Nixie Recruit", None, regions["Icy Summit Main"])
        nixie_recruit.place_locked_item(RabiRibiItem("Nixie Recruit", ItemClassification.progression, None, self.player))
        regions["Icy Summit Main"].locations.append(nixie_recruit)
        add_rule(nixie_recruit, lambda state: logic.can_recruit_nixie(state, self.player))

        aruraune_recruit = RabiRibiLocation(self.player, "Aruraune Recruit", None, regions["Forest Night West"])
        aruraune_recruit.place_locked_item(RabiRibiItem("Aruraune Recruit", ItemClassification.progression, None, self.player))
        regions["Forest Night West"].locations.append(aruraune_recruit)
        add_rule(aruraune_recruit, lambda state: logic.can_recruit_aruraune(state, self.player))

        seana_recruit = RabiRibiLocation(self.player, "Seana Recruit", None, regions["Park Town Entrance"])
        seana_recruit.place_locked_item(RabiRibiItem("Seana Recruit", ItemClassification.progression, None, self.player))
        regions["Park Town Entrance"].locations.append(seana_recruit)
        add_rule(seana_recruit, lambda state: logic.can_recruit_seana(state, self.player))

        lilith_recruit = RabiRibiLocation(self.player, "Lilith Recruit", None, regions["Sky Island Main"])
        lilith_recruit.place_locked_item(RabiRibiItem("Lilith Recruit", ItemClassification.progression, None, self.player))
        regions["Sky Island Main"].locations.append(lilith_recruit)
        add_rule(lilith_recruit, lambda state: logic.can_recruit_lilith(state, self.player))

        vanilla_recruit = RabiRibiLocation(self.player, "Vanilla Recruit", None, regions["Sky Bridge East Lower"])
        vanilla_recruit.place_locked_item(RabiRibiItem("Vanilla Recruit", ItemClassification.progression, None, self.player))
        regions["Sky Bridge East Lower"].locations.append(vanilla_recruit)
        add_rule(vanilla_recruit, lambda state: logic.can_recruit_chocolate(state, self.player))

        chocolate_recruit = RabiRibiLocation(self.player, "Chocolate Recruit", None, regions["Ravine Chocolate"])
        chocolate_recruit.place_locked_item(RabiRibiItem("Chocolate Recruit", ItemClassification.progression, None, self.player))
        regions["Ravine Chocolate"].locations.append(chocolate_recruit)
        add_rule(chocolate_recruit, lambda state: logic.can_recruit_chocolate(state, self.player))

        kotri_recruit = RabiRibiLocation(self.player, "Kotri Recruit", None, regions["Volcanic Main"])
        kotri_recruit.place_locked_item(RabiRibiItem("Kotri Recruit", ItemClassification.progression, None, self.player))
        regions["Volcanic Main"].locations.append(kotri_recruit)
        add_rule(kotri_recruit, lambda state: logic.can_recruit_kotri(state, self.player))

        # keke_bunny_recruit = RabiRibiLocation(self.player, "Keke Bunny Recruit", None, regions["Plurkwood Main"])
        # keke_bunny_recruit.place_locked_item(RabiRibiItem("Keke Bunny Recruit", ItemClassification.progression, None, self.player))
        # regions["Plurkwood Main"].locations.append(keke_bunny_recruit)
        # add_rule(keke_bunny_recruit, lambda state: logic.can_recruit_keke_bunny(state, self.player))

        chapter_1 = RabiRibiLocation(self.player, "Chapter 1", None, regions["Town Main"])
        chapter_1.place_locked_item(RabiRibiItem("Chapter 1", ItemClassification.progression, None, self.player))
        regions["Town Main"].locations.append(chapter_1)
        add_rule(chapter_1, lambda state: logic.can_reach_chapter_1(state, self.player))

        chapter_2 = RabiRibiLocation(self.player, "Chapter 2", None, regions["Town Main"])
        chapter_2.place_locked_item(RabiRibiItem("Chapter 2", ItemClassification.progression, None, self.player))
        regions["Town Main"].locations.append(chapter_2)
        add_rule(chapter_2,
                 lambda state: logic.can_reach_chapter_5(state, self.player) and
                    state.has("Chapter 1", self.player))

        chapter_3 = RabiRibiLocation(self.player, "Chapter 3", None, regions["Town Main"])
        chapter_3.place_locked_item(RabiRibiItem("Chapter 3", ItemClassification.progression, None, self.player))
        regions["Town Main"].locations.append(chapter_3)
        add_rule(chapter_3,
                 lambda state: logic.can_reach_chapter_5(state, self.player) and
                    state.has("Chapter 2", self.player))

        chapter_4 = RabiRibiLocation(self.player, "Chapter 4", None, regions["Town Main"])
        chapter_4.place_locked_item(RabiRibiItem("Chapter 4", ItemClassification.progression, None, self.player))
        regions["Town Main"].locations.append(chapter_4)
        add_rule(chapter_4,
                 lambda state: logic.can_reach_chapter_5(state, self.player) and
                    state.has("Chapter 3", self.player))

        chapter_5 = RabiRibiLocation(self.player, "Chapter 5", None, regions["Town Main"])
        chapter_5.place_locked_item(RabiRibiItem("Chapter 5", ItemClassification.progression, None, self.player))
        regions["Town Main"].locations.append(chapter_5)
        add_rule(chapter_5,
                 lambda state: logic.can_reach_chapter_5(state, self.player) and
                    state.has("Chapter 4", self.player))

        bunny_strike = RabiRibiLocation(self.player, "Bunny Strike", None, regions["Town Main"])
        bunny_strike.place_locked_item(RabiRibiItem("Bunny Strike", ItemClassification.progression, None, self.player))
        regions["Town Main"].locations.append(bunny_strike)

        speed_boost = RabiRibiLocation(self.player, "Speed Boost", None, regions["Town Main"])
        speed_boost.place_locked_item(RabiRibiItem("Speed Boost", ItemClassification.progression, None, self.player))
        regions["Town Main"].locations.append(speed_boost)

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
