"""
This module is responsible for patching the game's map files per world.
This is done on the client side upon connect to allow for a smoother setup experience.
"""
from worlds.rabi_ribi import RabiRibiWorld
from worlds.rabi_ribi.existing_randomizer.dataparser import RandomizerData
from worlds.rabi_ribi.existing_randomizer.mapfileio import ItemModifier, grab_original_maps
from worlds.rabi_ribi.client.client import RabiRibiContext
from worlds.rabi_ribi.logic_helpers import convert_ap_name_to_existing_rando_name
from worlds.rabi_ribi.existing_randomizer.randomizer import (
    get_default_areaids,
    pre_modify_map_data,
    parse_args,
    apply_item_specific_fixes,
    apply_map_transition_shuffle,
    insert_items_into_map
)

class Allocation():
    """
    This class mimics the existing randomizer's Allocation class.
    It sets the appropriate fields such that we can call the existing randomizer's
    data manipulation and file write functions.
    """

    def __init__(self, ctx: RabiRibiContext, randomizer_data: RandomizerData):
        self.map_modifications = []
        self.item_at_item_location = self.set_location_info(
            ctx.slot,
            ctx.locations_info,
            ctx.location_ap_id_to_name,
            ctx.item_ap_id_to_name,
        )
        self.walking_left_transitions = randomizer_data.walking_left_transitions

    def set_location_info(self, slot_num, location_info, location_ap_id_to_name, item_ap_id_to_name):
        return {
            convert_ap_name_to_existing_rando_name(location_ap_id_to_name[location.location]):
            convert_ap_name_to_existing_rando_name(item_ap_id_to_name[location.item]) \
                if location.player == slot_num else "ANOTHER_PLAYERS_ITEM"
            for location in location_info.values()
        }

def patch_map_files(ctx: RabiRibiContext):
    """
    Patch the map files to make map modifications (item changes / room changes, etc).

    :RabiRibiContext ctx: The Rabi Ribi Context instance.
    """
    map_source_dir = f"{RabiRibiWorld.settings.game_installation_path}/data/area"
    grab_original_maps(map_source_dir, ctx.custom_seed_subdir)
    settings = parse_args() # this should be done through slot data later
    area_ids = get_default_areaids()
    randomizer_data = RandomizerData(settings)
    item_modifier = ItemModifier(
        area_ids,
        map_source_dir,
        no_load=True
    )
    allocation = Allocation(ctx, randomizer_data)
    pre_modify_map_data(item_modifier, settings, allocation.map_modifications)
    apply_item_specific_fixes(item_modifier, allocation)
    apply_map_transition_shuffle(item_modifier, randomizer_data, settings, allocation)
    insert_items_into_map(item_modifier, randomizer_data, settings, allocation)
    item_modifier.save(ctx.custom_seed_subdir)
