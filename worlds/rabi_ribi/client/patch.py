"""
This module is responsible for patching the game's map files per world.
This is done on the client side upon connect to allow for a smoother setup experience.
"""
import struct

from worlds.rabi_ribi import RabiRibiWorld
from worlds.rabi_ribi.options import AttackMode
from worlds.rabi_ribi.existing_randomizer.dataparser import RandomizerData
from worlds.rabi_ribi.existing_randomizer.mapfileio import (
    ItemModifier,
    grab_original_maps,
    MAP_ITEMS_OFFSET,
    MAP_TILES0_OFFSET,
    MAP_SIZE
)
from worlds.rabi_ribi.existing_randomizer.utility import to_index
from worlds.rabi_ribi.client.client import RabiRibiContext
from worlds.rabi_ribi.logic_helpers import convert_ap_name_to_existing_rando_name
from worlds.rabi_ribi.items import lookup_item_id_to_name
from worlds.rabi_ribi.locations import lookup_location_id_to_name
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
            ctx.locations_info
        )

        self.map_modifications += randomizer_data.default_map_modifications
        self.walking_left_transitions = randomizer_data.walking_left_transitions

    def set_location_info(self, slot_num, location_info):
        return {
            convert_ap_name_to_existing_rando_name(lookup_location_id_to_name[location.location]):
            convert_ap_name_to_existing_rando_name(lookup_item_id_to_name[location.item]) \
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
    settings = parse_args()
    settings.open_mode = ctx.slot_data["openMode"]
    settings.shuffle_gift_items = ctx.slot_data["randomize_gift_items"]
    attack_mode = ctx.slot_data["attackMode"]
    if attack_mode == AttackMode.option_hyper:
        settings.hyper_attack_mode = True
    elif attack_mode == AttackMode.option_super:
        settings.super_attack_mode = True
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
    embed_seed_player_into_mapdata(ctx, item_modifier)

def remove_item_from_map(ctx: RabiRibiContext, area_id: int, x: int, y: int):
    """
    This method removes a specified item from the map. This is used to delete
    items from other worlds (represented by exclamation point items) on the map
    after the player collects it. This is needed because the item being visible
    is directly linked to whether the exclamation point item is in the player's
    inventory. We always set that value to false so that the player can see all
    of the exclamation points, but we want to delete the ones the player has already
    obtained.
    """
    f = open(f"{ctx.custom_seed_subdir}/area{area_id}.map", "r+b")
    f.seek(MAP_ITEMS_OFFSET)
    tiledata_items = list(struct.unpack('%dh' % MAP_SIZE, f.read(MAP_SIZE*2)))
    index = to_index((x, y))
    tiledata_items[index] = 0
    f.seek(MAP_ITEMS_OFFSET)
    f.write(struct.pack('%dh' % MAP_SIZE, *tiledata_items))
    f.close()

def embed_seed_player_into_mapdata(ctx: RabiRibiContext, item_modifier):
    for area_id, _ in item_modifier.stored_datas.items():
        f = open(f"{ctx.custom_seed_subdir}/area{area_id}.map", "r+b")
        f.seek(MAP_TILES0_OFFSET)
        f.write(ctx.seed_player_id.encode())
        f.close()
