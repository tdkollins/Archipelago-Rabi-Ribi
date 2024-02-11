"""This module represents location definitions for Rabi-Ribi"""
from BaseClasses import Location, Region, MultiWorld
from worlds.generic.Rules import add_rule
from worlds.rabi_ribi.existing_randomizer.randomizer import parse_args
from worlds.rabi_ribi.existing_randomizer.dataparser import RandomizerData
from worlds.rabi_ribi.logic_helpers import (
    convert_existing_rando_name_to_ap_name,
    convert_existing_rando_rule_to_ap_rule
)

class RabiRibiLocation(Location):
    """Rabi Ribi Location Definition"""
    game: str = "Rabi-Ribi"

class RegionDef:
    """
    This class provides methods associated with defining and connecting regions, locations,
    and the access rules for those regions and locations.
    """
    def __init__(self, multiworld: MultiWorld, player: int):
        # Use default args for now.
        args = parse_args()
        self.randomizer_data = RandomizerData(args)
        self.player = player
        self.multiworld = multiworld

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
            rule = convert_existing_rando_rule_to_ap_rule(edge.prereq_expression, self.player)
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
        :returns: None
        """
        locations = self.randomizer_data.item_constraints
        regions = self.multiworld.regions.region_cache[self.player]
        for location in locations:
            entry_rule = convert_existing_rando_rule_to_ap_rule(location.entry_prereq_expr, self.player)
            exit_rule = convert_existing_rando_rule_to_ap_rule(location.exit_prereq_expr, self.player)
            location_name = convert_existing_rando_name_to_ap_name(location.item)
            region_name = convert_existing_rando_name_to_ap_name(location.from_location)
            ap_location = RabiRibiLocation(
                self.player,
                location_name,
                location_name_to_id[location_name],
                regions[region_name]
            )
            regions[region_name].locations.append(ap_location)

            # If this should be done during the set_rules function call, just comment on the PR or @phie_
            #   on the AP discord. I did it here because its easier to only go through the locations once
            #   (the existing randomizer defines the locations and location rules on the same object)
            add_rule(ap_location, entry_rule)
            add_rule(ap_location, exit_rule)

    def _get_region_name_list(self):
        return [
            convert_existing_rando_name_to_ap_name(name) for \
            name in self.randomizer_data.locations.keys()
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
