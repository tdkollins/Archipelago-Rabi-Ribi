"""This module represents item definitions for Rabi-Ribi"""
from typing import Dict, List, NamedTuple, Optional, Set

from BaseClasses import Item, ItemClassification
from worlds.rabi_ribi.utility import get_rabi_ribi_base_id
from .existing_randomizer.visualizer import load_item_locs
from .names import ItemName

class RabiRibiItem(Item):
    """Rabi Ribi Item Definition"""
    game: str = "Rabi-Ribi"

    def __init__(self, name, classification: ItemClassification, code: int = None, player: int = None):
        super(RabiRibiItem, self).__init__(name, classification, code, player)


class RabiRibiItemData(NamedTuple):
    code: Optional[int]
    classification: ItemClassification = ItemClassification.filler

upgrades_table: Dict[str, RabiRibiItemData] = {
    ItemName.air_dash           : RabiRibiItemData(get_rabi_ribi_base_id() + 0x01, ItemClassification.progression),
    ItemName.air_jump           : RabiRibiItemData(get_rabi_ribi_base_id() + 0x02, ItemClassification.progression),
    ItemName.auto_earrings      : RabiRibiItemData(get_rabi_ribi_base_id() + 0x03, ItemClassification.filler),
    ItemName.bunny_strike       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x04, ItemClassification.progression),
    ItemName.bunny_whirl        : RabiRibiItemData(get_rabi_ribi_base_id() + 0x05, ItemClassification.progression),
    ItemName.carrot_bomb        : RabiRibiItemData(get_rabi_ribi_base_id() + 0x06, ItemClassification.progression),
    ItemName.charge_ring        : RabiRibiItemData(get_rabi_ribi_base_id() + 0x07, ItemClassification.progression),
    ItemName.cyber_flower       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x08, ItemClassification.filler),
    ItemName.fire_orb           : RabiRibiItemData(get_rabi_ribi_base_id() + 0x09, ItemClassification.progression),
    ItemName.hammer_roll        : RabiRibiItemData(get_rabi_ribi_base_id() + 0x0A, ItemClassification.progression),
    ItemName.hammer_wave        : RabiRibiItemData(get_rabi_ribi_base_id() + 0x0B, ItemClassification.filler),
    ItemName.hourglass          : RabiRibiItemData(get_rabi_ribi_base_id() + 0x0C, ItemClassification.filler),
    ItemName.light_orb          : RabiRibiItemData(get_rabi_ribi_base_id() + 0x0D, ItemClassification.progression),
    ItemName.nature_orb         : RabiRibiItemData(get_rabi_ribi_base_id() + 0x0E, ItemClassification.filler),
    ItemName.p_hairpin          : RabiRibiItemData(get_rabi_ribi_base_id() + 0x0F, ItemClassification.filler),
    ItemName.piko_hammer        : RabiRibiItemData(get_rabi_ribi_base_id() + 0x10, ItemClassification.progression),
    ItemName.quick_barrette     : RabiRibiItemData(get_rabi_ribi_base_id() + 0x11, ItemClassification.filler),
    ItemName.plus_necklace      : RabiRibiItemData(get_rabi_ribi_base_id() + 0x12, ItemClassification.filler),
    ItemName.rabi_slippers      : RabiRibiItemData(get_rabi_ribi_base_id() + 0x13, ItemClassification.progression),
    ItemName.sliding_powder     : RabiRibiItemData(get_rabi_ribi_base_id() + 0x14, ItemClassification.progression),
    ItemName.speed_boost        : RabiRibiItemData(get_rabi_ribi_base_id() + 0x15, ItemClassification.progression),
    ItemName.spike_barrier      : RabiRibiItemData(get_rabi_ribi_base_id() + 0x16, ItemClassification.filler),
    ItemName.super_carrot       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x17, ItemClassification.filler),
    ItemName.wall_jump          : RabiRibiItemData(get_rabi_ribi_base_id() + 0x18, ItemClassification.progression),
    ItemName.water_orb          : RabiRibiItemData(get_rabi_ribi_base_id() + 0x19, ItemClassification.progression)
}

magic_table: Dict[str, RabiRibiItemData] = {
    ItemName.sunny_beam         : RabiRibiItemData(get_rabi_ribi_base_id() + 0x1A, ItemClassification.progression_skip_balancing),
    ItemName.chaos_rod          : RabiRibiItemData(get_rabi_ribi_base_id() + 0x1B, ItemClassification.progression_skip_balancing),
    ItemName.healing_staff      : RabiRibiItemData(get_rabi_ribi_base_id() + 0x1C, ItemClassification.progression_skip_balancing),
    ItemName.explode_shot       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x1D, ItemClassification.progression_skip_balancing),
    ItemName.carrot_shooter     : RabiRibiItemData(get_rabi_ribi_base_id() + 0x1E, ItemClassification.progression)
}

badges_table: Dict[str, RabiRibiItemData] = {
    ItemName.arm_strength       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x1F, ItemClassification.filler),
    ItemName.armored            : RabiRibiItemData(get_rabi_ribi_base_id() + 0x20, ItemClassification.filler),
    ItemName.atk_grow           : RabiRibiItemData(get_rabi_ribi_base_id() + 0x21, ItemClassification.filler),
    ItemName.atk_trade          : RabiRibiItemData(get_rabi_ribi_base_id() + 0x22, ItemClassification.filler),
    ItemName.auto_trigger       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x23, ItemClassification.filler),
    ItemName.blessed            : RabiRibiItemData(get_rabi_ribi_base_id() + 0x24, ItemClassification.filler),
    ItemName.carrot_boost       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x25, ItemClassification.filler),
    ItemName.cashback           : RabiRibiItemData(get_rabi_ribi_base_id() + 0x26, ItemClassification.filler),
    ItemName.crisis_boost       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x27, ItemClassification.filler),
    ItemName.def_grow           : RabiRibiItemData(get_rabi_ribi_base_id() + 0x28, ItemClassification.filler),
    ItemName.def_trade          : RabiRibiItemData(get_rabi_ribi_base_id() + 0x29, ItemClassification.filler),
    ItemName.erina_badge        : RabiRibiItemData(get_rabi_ribi_base_id() + 0x2A, ItemClassification.filler),
    ItemName.frame_cancel       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x2B, ItemClassification.filler),
    ItemName.health_plus        : RabiRibiItemData(get_rabi_ribi_base_id() + 0x2C, ItemClassification.filler),
    ItemName.health_surge       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x2D, ItemClassification.filler),
    ItemName.health_wager       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x2E, ItemClassification.filler),
    ItemName.hex_cancel         : RabiRibiItemData(get_rabi_ribi_base_id() + 0x2F, ItemClassification.filler),
    ItemName.hitbox_down        : RabiRibiItemData(get_rabi_ribi_base_id() + 0x30, ItemClassification.filler),
    ItemName.lucky_seven        : RabiRibiItemData(get_rabi_ribi_base_id() + 0x31, ItemClassification.filler),
    ItemName.mana_plus          : RabiRibiItemData(get_rabi_ribi_base_id() + 0x32, ItemClassification.filler),
    ItemName.mana_surge         : RabiRibiItemData(get_rabi_ribi_base_id() + 0x33, ItemClassification.filler),
    ItemName.mana_wager         : RabiRibiItemData(get_rabi_ribi_base_id() + 0x34, ItemClassification.filler),
    ItemName.pure_love          : RabiRibiItemData(get_rabi_ribi_base_id() + 0x35, ItemClassification.filler),
    ItemName.ribbon_badge       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x36, ItemClassification.filler),
    ItemName.self_defense       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x37, ItemClassification.filler),
    ItemName.stamina_plus       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x38, ItemClassification.filler),
    ItemName.survival           : RabiRibiItemData(get_rabi_ribi_base_id() + 0x39, ItemClassification.filler),
    ItemName.top_form           : RabiRibiItemData(get_rabi_ribi_base_id() + 0x3A, ItemClassification.filler),
    ItemName.tough_skin         : RabiRibiItemData(get_rabi_ribi_base_id() + 0x3B, ItemClassification.filler),
    ItemName.toxic_strike       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x3C, ItemClassification.filler),
    ItemName.weaken             : RabiRibiItemData(get_rabi_ribi_base_id() + 0x3D, ItemClassification.filler)
}

collectables_table: Dict[str, RabiRibiItemData] = {
     ItemName.attack_up         : RabiRibiItemData(get_rabi_ribi_base_id() + 0x3E, ItemClassification.filler),
     ItemName.easter_egg        : RabiRibiItemData(get_rabi_ribi_base_id() + 0x3F, ItemClassification.progression_skip_balancing),
     ItemName.gold_carrot       : RabiRibiItemData(get_rabi_ribi_base_id() + 0x40, ItemClassification.filler),
     ItemName.hp_up             : RabiRibiItemData(get_rabi_ribi_base_id() + 0x41, ItemClassification.filler),
     ItemName.mp_up             : RabiRibiItemData(get_rabi_ribi_base_id() + 0x42, ItemClassification.filler),
     ItemName.nothing           : RabiRibiItemData(get_rabi_ribi_base_id() + 0x43, ItemClassification.filler),
     ItemName.pack_up           : RabiRibiItemData(get_rabi_ribi_base_id() + 0x44, ItemClassification.filler),
     ItemName.regen_up          : RabiRibiItemData(get_rabi_ribi_base_id() + 0x45, ItemClassification.filler)
}

item_table : Dict[str, RabiRibiItemData] = {
    **upgrades_table,
    **magic_table,
    **badges_table,
    **collectables_table
}

lookup_id_to_name: Dict[int, str] = {data.code: item_name for item_name, data in item_table.items() if data.code}

item_groups: Dict[str, Set[str]] = {
    "Upgrades": set(upgrades_table.keys()),
    "Magic": set(magic_table.keys()),
    "Badges": set(badges_table.keys()),
    "Collectables": set(collectables_table.keys())
}

recruit_table: Set[str] = {
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
    ItemName.kotri_recruit,
    ItemName.keke_bunny_recruit
}

def get_base_item_list() -> List[str]:
    """
    Get the base list of items in the game.
    No options are configurable at the moment.

    :returns List[str]: a list of item names to be added to the AP world. 
    """
    item_list = []

    # load list of all game items from existing randomizer.
    item_locs = load_item_locs()

    # Use a set amount of easter eggs
    for _ in range(5):
        item_list.append("Easter Egg")

    for item in item_locs.keys():
        # If we want to include the item, convert to the AP item id.
        # Otherwise, pass and dont include it.
        if item.startswith("ITEM_EGG"):
            pass
        elif item.startswith("ITEM_ATK_UP"):
            item_list.append("Attack Up")
        elif item.startswith("ITEM_HP_UP"):
            item_list.append("HP Up")
        elif item.startswith("ITEM_MP_UP"):
            item_list.append("MP Up")
        elif item.startswith("ITEM_PACK_UP"):
            item_list.append("Pack Up")
        elif item.startswith("ITEM_REGEN_UP"):
            item_list.append("Regen Up")
        elif item in [
            "ITEM_UNKNOWN_ITEM_1",
            "ITEM_UNKNOWN_ITEM_2",
            "ITEM_UNKNOWN_ITEM_3",
            "ITEM_P_HAIRPIN",
            "ITEM_SPEED_BOOST",
            "ITEM_BUNNY_STRIKE",
        ]:
            pass
        else:
            # Format the item string and then add to the item list
            item = item.split("_")
            item = " ".join(word.capitalize() for word in item[1:])
            item_list.append(item)

    return item_list
