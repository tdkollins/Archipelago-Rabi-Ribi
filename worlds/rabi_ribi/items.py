"""This module represents item definitions for Rabi-Ribi"""
from typing import NamedTuple, Optional

from BaseClasses import Item, ItemClassification
from .constants import GAME_NAME, BASE_ID
from .existing_randomizer.dataparser import RandomizerData
from .names import ItemName
from .options import RabiRibiOptions
from .utility import convert_existing_rando_name_to_ap_name

class RabiRibiItem(Item):
    """Rabi Ribi Item Definition"""
    game: str = GAME_NAME

    def __init__(self, name, classification: ItemClassification, code: Optional[int], player: int):
        super(RabiRibiItem, self).__init__(name, classification, code, player)

class RabiRibiItemData(NamedTuple):
    code: Optional[int]
    classification: ItemClassification = ItemClassification.filler

upgrades_table: dict[str, RabiRibiItemData] = {
    ItemName.air_dash           : RabiRibiItemData(BASE_ID + 0x01, ItemClassification.progression),
    ItemName.air_jump           : RabiRibiItemData(BASE_ID + 0x02, ItemClassification.progression),
    ItemName.auto_earrings      : RabiRibiItemData(BASE_ID + 0x03, ItemClassification.filler),
    ItemName.bunny_strike       : RabiRibiItemData(BASE_ID + 0x04, ItemClassification.progression),
    ItemName.bunny_whirl        : RabiRibiItemData(BASE_ID + 0x05, ItemClassification.progression),
    ItemName.carrot_bomb        : RabiRibiItemData(BASE_ID + 0x06, ItemClassification.progression),
    ItemName.charge_ring        : RabiRibiItemData(BASE_ID + 0x07, ItemClassification.progression),
    ItemName.cyber_flower       : RabiRibiItemData(BASE_ID + 0x08, ItemClassification.filler),
    ItemName.fire_orb           : RabiRibiItemData(BASE_ID + 0x09, ItemClassification.progression),
    ItemName.hammer_roll        : RabiRibiItemData(BASE_ID + 0x0A, ItemClassification.progression),
    ItemName.hammer_wave        : RabiRibiItemData(BASE_ID + 0x0B, ItemClassification.filler),
    ItemName.hourglass          : RabiRibiItemData(BASE_ID + 0x0C, ItemClassification.filler),
    ItemName.light_orb          : RabiRibiItemData(BASE_ID + 0x0D, ItemClassification.progression),
    ItemName.nature_orb         : RabiRibiItemData(BASE_ID + 0x0E, ItemClassification.filler),
    ItemName.p_hairpin          : RabiRibiItemData(BASE_ID + 0x0F, ItemClassification.filler),
    ItemName.piko_hammer        : RabiRibiItemData(BASE_ID + 0x10, ItemClassification.progression),
    ItemName.quick_barrette     : RabiRibiItemData(BASE_ID + 0x11, ItemClassification.filler),
    ItemName.plus_necklace      : RabiRibiItemData(BASE_ID + 0x12, ItemClassification.filler),
    ItemName.rabi_slippers      : RabiRibiItemData(BASE_ID + 0x13, ItemClassification.progression),
    ItemName.sliding_powder     : RabiRibiItemData(BASE_ID + 0x14, ItemClassification.progression),
    ItemName.speed_boost        : RabiRibiItemData(BASE_ID + 0x15, ItemClassification.progression),
    ItemName.spike_barrier      : RabiRibiItemData(BASE_ID + 0x16, ItemClassification.filler),
    ItemName.super_carrot       : RabiRibiItemData(BASE_ID + 0x17, ItemClassification.filler),
    ItemName.wall_jump          : RabiRibiItemData(BASE_ID + 0x18, ItemClassification.progression),
    ItemName.water_orb          : RabiRibiItemData(BASE_ID + 0x19, ItemClassification.progression),

    ItemName.book_of_carrot     : RabiRibiItemData(BASE_ID + 0x46, ItemClassification.filler),
    ItemName.bunny_amulet       : RabiRibiItemData(BASE_ID + 0x47, ItemClassification.progression),
    ItemName.max_bracelet       : RabiRibiItemData(BASE_ID + 0x48, ItemClassification.filler),
    ItemName.soul_heart         : RabiRibiItemData(BASE_ID + 0x49, ItemClassification.filler),
    # Remove Strange Box for now, as the player starts with it
    #ItemName.strange_box        : RabiRibiItemData(rabi_ribi_base_id + 0x4A, ItemClassification.filler),
}

magic_table: dict[str, RabiRibiItemData] = {
    ItemName.sunny_beam         : RabiRibiItemData(BASE_ID + 0x1A, ItemClassification.progression_skip_balancing),
    ItemName.chaos_rod          : RabiRibiItemData(BASE_ID + 0x1B, ItemClassification.progression_skip_balancing),
    ItemName.healing_staff      : RabiRibiItemData(BASE_ID + 0x1C, ItemClassification.progression_skip_balancing),
    ItemName.explode_shot       : RabiRibiItemData(BASE_ID + 0x1D, ItemClassification.progression_skip_balancing),
    ItemName.carrot_shooter     : RabiRibiItemData(BASE_ID + 0x1E, ItemClassification.progression)
}

badges_table: dict[str, RabiRibiItemData] = {
    ItemName.arm_strength       : RabiRibiItemData(BASE_ID + 0x1F, ItemClassification.filler),
    ItemName.armored            : RabiRibiItemData(BASE_ID + 0x20, ItemClassification.filler),
    ItemName.atk_grow           : RabiRibiItemData(BASE_ID + 0x21, ItemClassification.filler),
    ItemName.atk_trade          : RabiRibiItemData(BASE_ID + 0x22, ItemClassification.filler),
    ItemName.auto_trigger       : RabiRibiItemData(BASE_ID + 0x23, ItemClassification.filler),
    ItemName.blessed            : RabiRibiItemData(BASE_ID + 0x24, ItemClassification.filler),
    ItemName.carrot_boost       : RabiRibiItemData(BASE_ID + 0x25, ItemClassification.filler),
    ItemName.cashback           : RabiRibiItemData(BASE_ID + 0x26, ItemClassification.filler),
    ItemName.crisis_boost       : RabiRibiItemData(BASE_ID + 0x27, ItemClassification.filler),
    ItemName.def_grow           : RabiRibiItemData(BASE_ID + 0x28, ItemClassification.filler),
    ItemName.def_trade          : RabiRibiItemData(BASE_ID + 0x29, ItemClassification.filler),
    ItemName.erina_badge        : RabiRibiItemData(BASE_ID + 0x2A, ItemClassification.filler),
    ItemName.frame_cancel       : RabiRibiItemData(BASE_ID + 0x2B, ItemClassification.filler),
    ItemName.health_plus        : RabiRibiItemData(BASE_ID + 0x2C, ItemClassification.filler),
    ItemName.health_surge       : RabiRibiItemData(BASE_ID + 0x2D, ItemClassification.filler),
    ItemName.health_wager       : RabiRibiItemData(BASE_ID + 0x2E, ItemClassification.filler),
    ItemName.hex_cancel         : RabiRibiItemData(BASE_ID + 0x2F, ItemClassification.filler),
    ItemName.hitbox_down        : RabiRibiItemData(BASE_ID + 0x30, ItemClassification.filler),
    ItemName.lucky_seven        : RabiRibiItemData(BASE_ID + 0x31, ItemClassification.filler),
    ItemName.mana_plus          : RabiRibiItemData(BASE_ID + 0x32, ItemClassification.filler),
    ItemName.mana_surge         : RabiRibiItemData(BASE_ID + 0x33, ItemClassification.filler),
    ItemName.mana_wager         : RabiRibiItemData(BASE_ID + 0x34, ItemClassification.filler),
    ItemName.pure_love          : RabiRibiItemData(BASE_ID + 0x35, ItemClassification.filler),
    ItemName.ribbon_badge       : RabiRibiItemData(BASE_ID + 0x36, ItemClassification.filler),
    ItemName.self_defense       : RabiRibiItemData(BASE_ID + 0x37, ItemClassification.filler),
    ItemName.stamina_plus       : RabiRibiItemData(BASE_ID + 0x38, ItemClassification.filler),
    ItemName.survival           : RabiRibiItemData(BASE_ID + 0x39, ItemClassification.filler),
    ItemName.top_form           : RabiRibiItemData(BASE_ID + 0x3A, ItemClassification.filler),
    ItemName.tough_skin         : RabiRibiItemData(BASE_ID + 0x3B, ItemClassification.filler),
    ItemName.toxic_strike       : RabiRibiItemData(BASE_ID + 0x3C, ItemClassification.filler),
    ItemName.weaken             : RabiRibiItemData(BASE_ID + 0x3D, ItemClassification.filler)
}

collectables_table: dict[str, RabiRibiItemData] = {
    ItemName.attack_up          : RabiRibiItemData(BASE_ID + 0x3E, ItemClassification.filler),
    ItemName.easter_egg         : RabiRibiItemData(BASE_ID + 0x3F, ItemClassification.progression_skip_balancing),
    # Moved Gold Carrot to consumables
    ItemName.hp_up              : RabiRibiItemData(BASE_ID + 0x41, ItemClassification.filler),
    ItemName.mp_up              : RabiRibiItemData(BASE_ID + 0x42, ItemClassification.filler),
    ItemName.nothing            : RabiRibiItemData(BASE_ID + 0x43, ItemClassification.filler),
    ItemName.pack_up            : RabiRibiItemData(BASE_ID + 0x44, ItemClassification.filler),
    ItemName.regen_up           : RabiRibiItemData(BASE_ID + 0x45, ItemClassification.filler),
}

consumable_table: dict[str, RabiRibiItemData] = {
    ItemName.gold_carrot        : RabiRibiItemData(BASE_ID + 0x40, ItemClassification.progression_skip_balancing),

    ItemName.cocoa_bomb         : RabiRibiItemData(BASE_ID + 0x4B, ItemClassification.progression_skip_balancing),
    ItemName.rumi_cake          : RabiRibiItemData(BASE_ID + 0x4C, ItemClassification.progression_skip_balancing),
    ItemName.rumi_donut         : RabiRibiItemData(BASE_ID + 0x4D, ItemClassification.progression_skip_balancing),
}

trap_table: dict[str, RabiRibiItemData] = {
    ItemName.pbpb_box           : RabiRibiItemData(BASE_ID + 0x4E, ItemClassification.trap)
}

item_data_table : dict[str, RabiRibiItemData] = {
    **upgrades_table,
    **magic_table,
    **badges_table,
    **collectables_table,
    **consumable_table,
    **trap_table
}

filler_items : dict[str, int] = {
    ItemName.hp_up: 25,
    ItemName.mp_up: 25,
    ItemName.attack_up: 20,
    ItemName.pack_up: 15,
    ItemName.regen_up: 15
}

item_table: dict[str, int] = {name: data.code for name, data in item_data_table.items() if data.code is not None }

lookup_item_id_to_name: dict[int, str] = {data.code: item_name for item_name, data in item_data_table.items() if data.code}

item_groups: dict[str, set[str]] = {
    "Upgrades": set(upgrades_table.keys()),
    "Magic": set(magic_table.keys()),
    "Badges": set(badges_table.keys()),
    "Collectables": set(collectables_table.keys()),
    "Consumables": set(consumable_table.keys())
}

# Keke Bunny does not count for Irisu fight.
recruit_table_irisu: set[str] = {
    ItemName.cocoa_recruit,
    ItemName.ashuri_recruit,
    ItemName.rita_recruit,
    ItemName.cicini_recruit,
    ItemName.saya_recruit,
    ItemName.syaro_recruit,
    ItemName.pandora_recruit,
    ItemName.nieve_recruit,
    ItemName.nixie_recruit,
    ItemName.aruraune_recruit,
    ItemName.seana_recruit,
    ItemName.lilith_recruit,
    ItemName.vanilla_recruit,
    ItemName.chocolate_recruit,
    ItemName.kotri_recruit
}

recruit_table: set[str] = {
    *recruit_table_irisu,
    ItemName.keke_bunny_recruit
}

event_table: set[str] = {
    *recruit_table,
    ItemName.ashuri_2,
    ItemName.cocoa_1,
    ItemName.kotri_1,
    ItemName.kotri_2,
    ItemName.seana_1,
    ItemName.rumi_recruit,
    ItemName.miriam_recruit,
    ItemName.irisu_recruit,
    "Chapter 1",
    "Chapter 2",
    "Chapter 3",
    "Chapter 4",
    "Chapter 5",
    "Chapter 6",
    "Chapter 7",
}

shufflable_gift_items = {
    ItemName.speed_boost,
    ItemName.bunny_strike
}

shufflable_gift_items_plurkwood = {
    ItemName.p_hairpin
}

def get_base_item_list(data: RandomizerData) -> list[str]:
    """
    Get the base list of items in the game.
    No options are configurable at the moment.

    :returns list[str]: a list of item names to be added to the AP world. 
    """
    item_list: list[str] = []

    # load list of all game items from existing randomizer.
    item_names: list[str] = data.to_shuffle
    item_names += data.included_additional_items
    item_names.sort()

    for item in item_names:
        # Remove Eggs and Potions, to be used as filler items
        if item.startswith("EGG"):
            pass
        elif item.startswith("ATK_UP"):
            pass
        elif item.startswith("HP_UP"):
            pass
        elif item.startswith("MP_UP"):
            pass
        elif item.startswith("PACK_UP"):
            pass
        elif item.startswith("REGEN_UP"):
            pass
        else:
            # Format the item string and then add to the item list
            item_list.append(convert_existing_rando_name_to_ap_name(item))

    return item_list
