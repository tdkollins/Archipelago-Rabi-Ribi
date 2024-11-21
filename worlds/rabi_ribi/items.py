"""This module represents item definitions for Rabi-Ribi"""
from typing import Dict, List, NamedTuple, Optional, Set

from BaseClasses import Item, ItemClassification
from .existing_randomizer.visualizer import load_item_locs

rabi_ribi_base_id: int = 8350438193300

class RabiRibiItem(Item):
    """Rabi Ribi Item Definition"""
    game: str = "Rabi-Ribi"

    def __init__(self, name, classification: ItemClassification, code: int = None, player: int = None):
        super(RabiRibiItem, self).__init__(name, classification, code, player)


class RabiRibiItemData(NamedTuple):
    code: Optional[int]
    classification: ItemClassification = ItemClassification.filler

upgrades_table: Dict[str, RabiRibiItemData] = {
    "Air Dash"          : RabiRibiItemData(rabi_ribi_base_id + 0x01, ItemClassification.progression),
    "Air Jump"          : RabiRibiItemData(rabi_ribi_base_id + 0x02, ItemClassification.progression),
    "Auto Earrings"     : RabiRibiItemData(rabi_ribi_base_id + 0x03, ItemClassification.filler),
    "Bunny Strike"      : RabiRibiItemData(rabi_ribi_base_id + 0x04, ItemClassification.progression),
    "Bunny Whirl"       : RabiRibiItemData(rabi_ribi_base_id + 0x05, ItemClassification.progression),
    "Carrot Bomb"       : RabiRibiItemData(rabi_ribi_base_id + 0x06, ItemClassification.progression),
    "Charge Ring"       : RabiRibiItemData(rabi_ribi_base_id + 0x07, ItemClassification.progression),
    "Cyber Flower"      : RabiRibiItemData(rabi_ribi_base_id + 0x08, ItemClassification.filler),
    "Fire Orb"          : RabiRibiItemData(rabi_ribi_base_id + 0x09, ItemClassification.progression),
    "Hammer Roll"       : RabiRibiItemData(rabi_ribi_base_id + 0x0A, ItemClassification.progression),
    "Hammer Wave"       : RabiRibiItemData(rabi_ribi_base_id + 0x0B, ItemClassification.filler),
    "Hourglass"         : RabiRibiItemData(rabi_ribi_base_id + 0x0C, ItemClassification.filler),
    "Light Orb"         : RabiRibiItemData(rabi_ribi_base_id + 0x0D, ItemClassification.progression),
    "Nature Orb"        : RabiRibiItemData(rabi_ribi_base_id + 0x0E, ItemClassification.filler),
    "P Hairpin"         : RabiRibiItemData(rabi_ribi_base_id + 0x0F, ItemClassification.filler),
    "Piko Hammer"       : RabiRibiItemData(rabi_ribi_base_id + 0x10, ItemClassification.progression),
    "Quick Barrette"    : RabiRibiItemData(rabi_ribi_base_id + 0x11, ItemClassification.filler),
    "Plus Necklace"     : RabiRibiItemData(rabi_ribi_base_id + 0x12, ItemClassification.filler),
    "Rabi Slippers"     : RabiRibiItemData(rabi_ribi_base_id + 0x13, ItemClassification.progression),
    "Sliding Powder"    : RabiRibiItemData(rabi_ribi_base_id + 0x14, ItemClassification.progression),
    "Speed Boost"       : RabiRibiItemData(rabi_ribi_base_id + 0x15, ItemClassification.progression),
    "Spike Barrier"     : RabiRibiItemData(rabi_ribi_base_id + 0x16, ItemClassification.filler),
    "Super Carrot"      : RabiRibiItemData(rabi_ribi_base_id + 0x17, ItemClassification.filler),
    "Wall Jump"         : RabiRibiItemData(rabi_ribi_base_id + 0x18, ItemClassification.progression),
    "Water Orb"         : RabiRibiItemData(rabi_ribi_base_id + 0x19, ItemClassification.progression)
}

magic_table: Dict[str, RabiRibiItemData] = {
    "Carrot Shooter"    : RabiRibiItemData(rabi_ribi_base_id + 0x1A, ItemClassification.progression),
    "Chaos Rod"         : RabiRibiItemData(rabi_ribi_base_id + 0x1B, ItemClassification.progression_skip_balancing),
    "Explode Shot"      : RabiRibiItemData(rabi_ribi_base_id + 0x1C, ItemClassification.progression_skip_balancing),
    "Sunny Beam"        : RabiRibiItemData(rabi_ribi_base_id + 0x1D, ItemClassification.progression_skip_balancing)
}

badges_table: Dict[str, RabiRibiItemData] = {
    "Arm Strength"      : RabiRibiItemData(rabi_ribi_base_id + 0x1E, ItemClassification.filler),
    "Armored"           : RabiRibiItemData(rabi_ribi_base_id + 0x1F, ItemClassification.filler),
    "Atk Grow"          : RabiRibiItemData(rabi_ribi_base_id + 0x20, ItemClassification.filler),
    "Atk Trade"         : RabiRibiItemData(rabi_ribi_base_id + 0x21, ItemClassification.filler),
    "Auto Trigger"      : RabiRibiItemData(rabi_ribi_base_id + 0x22, ItemClassification.filler),
    "Blessed"           : RabiRibiItemData(rabi_ribi_base_id + 0x23, ItemClassification.filler),
    "Carrot Boost"      : RabiRibiItemData(rabi_ribi_base_id + 0x24, ItemClassification.filler),
    "Cashback"          : RabiRibiItemData(rabi_ribi_base_id + 0x25, ItemClassification.filler),
    "Crisis Boost"      : RabiRibiItemData(rabi_ribi_base_id + 0x26, ItemClassification.filler),
    "Def Grow"          : RabiRibiItemData(rabi_ribi_base_id + 0x27, ItemClassification.filler),
    "Def Trade"         : RabiRibiItemData(rabi_ribi_base_id + 0x28, ItemClassification.filler),
    "Erina Badge"       : RabiRibiItemData(rabi_ribi_base_id + 0x29, ItemClassification.filler),
    "Frame Cancel"      : RabiRibiItemData(rabi_ribi_base_id + 0x2A, ItemClassification.filler),
    "Health Plus"       : RabiRibiItemData(rabi_ribi_base_id + 0x2B, ItemClassification.filler),
    "Health Surge"      : RabiRibiItemData(rabi_ribi_base_id + 0x2C, ItemClassification.filler),
    "Health Wager"      : RabiRibiItemData(rabi_ribi_base_id + 0x2D, ItemClassification.filler),
    "Hex Cancel"        : RabiRibiItemData(rabi_ribi_base_id + 0x2E, ItemClassification.filler),
    "Hitbox Down"       : RabiRibiItemData(rabi_ribi_base_id + 0x2F, ItemClassification.filler),
    "Lucky Seven"       : RabiRibiItemData(rabi_ribi_base_id + 0x30, ItemClassification.filler),
    "Mana Plus"         : RabiRibiItemData(rabi_ribi_base_id + 0x31, ItemClassification.filler),
    "Mana Surge"        : RabiRibiItemData(rabi_ribi_base_id + 0x32, ItemClassification.filler),
    "Mana Wager"        : RabiRibiItemData(rabi_ribi_base_id + 0x33, ItemClassification.filler),
    "Pure Love"         : RabiRibiItemData(rabi_ribi_base_id + 0x34, ItemClassification.filler),
    "Ribbon Badge"      : RabiRibiItemData(rabi_ribi_base_id + 0x35, ItemClassification.filler),
    "Self Defense"      : RabiRibiItemData(rabi_ribi_base_id + 0x36, ItemClassification.filler),
    "Stamina Plus"      : RabiRibiItemData(rabi_ribi_base_id + 0x37, ItemClassification.filler),
    "Survival"          : RabiRibiItemData(rabi_ribi_base_id + 0x38, ItemClassification.filler),
    "Top Form"          : RabiRibiItemData(rabi_ribi_base_id + 0x39, ItemClassification.filler),
    "Tough Skin"        : RabiRibiItemData(rabi_ribi_base_id + 0x3A, ItemClassification.filler),
    "Toxic Strike"      : RabiRibiItemData(rabi_ribi_base_id + 0x3B, ItemClassification.filler),
    "Weaken"            : RabiRibiItemData(rabi_ribi_base_id + 0x3C, ItemClassification.filler)
}

collectables_table: Dict[str, RabiRibiItemData] = {
    "Attack Up"         : RabiRibiItemData(rabi_ribi_base_id + 0x3D, ItemClassification.filler),
    "Easter Egg"        : RabiRibiItemData(rabi_ribi_base_id + 0x3E, ItemClassification.progression_skip_balancing),
    "Gold Carrot"       : RabiRibiItemData(rabi_ribi_base_id + 0x3F, ItemClassification.filler),
    "HP Up"             : RabiRibiItemData(rabi_ribi_base_id + 0x40, ItemClassification.filler),
    "MP Up"             : RabiRibiItemData(rabi_ribi_base_id + 0x41, ItemClassification.filler),
    "Nothing"           : RabiRibiItemData(rabi_ribi_base_id + 0x42, ItemClassification.filler),
    "Pack Up"           : RabiRibiItemData(rabi_ribi_base_id + 0x43, ItemClassification.filler),
    "Regen Up"          : RabiRibiItemData(rabi_ribi_base_id + 0x44, ItemClassification.filler)
}

recruit_table: Dict[str, RabiRibiItemData] = {
    "Cocoa Recruit"         : RabiRibiItemData(None, ItemClassification.progression),
    "Ashuri Recruit"        : RabiRibiItemData(None, ItemClassification.progression),
    "Rita Recruit"          : RabiRibiItemData(None, ItemClassification.progression),
    "Cicini Recruit"        : RabiRibiItemData(None, ItemClassification.progression),
    "Saya Recruit"          : RabiRibiItemData(None, ItemClassification.progression),
    "Syaro Recruit"         : RabiRibiItemData(None, ItemClassification.progression),
    "Pandora Recruit"       : RabiRibiItemData(None, ItemClassification.progression),
    "Nieve Recruit"         : RabiRibiItemData(None, ItemClassification.progression),
    "Nixie Recruit"         : RabiRibiItemData(None, ItemClassification.progression),
    "Aruraune Recruit"      : RabiRibiItemData(None, ItemClassification.progression),
    "Seana Recruit"         : RabiRibiItemData(None, ItemClassification.progression),
    "Lilith Recruit"        : RabiRibiItemData(None, ItemClassification.progression),
    "Vanilla Recruit"       : RabiRibiItemData(None, ItemClassification.progression),
    "Chocolate Recruit"     : RabiRibiItemData(None, ItemClassification.progression),
    "Kotri Recruit"         : RabiRibiItemData(None, ItemClassification.progression),
    "Keke Bunny Recruit"    : RabiRibiItemData(None, ItemClassification.progression)
}

item_table : Dict[str, RabiRibiItemData] = {
    **upgrades_table,
    **magic_table,
    **badges_table,
    **collectables_table,
    **recruit_table
}

lookup_id_to_name: Dict[int, str] = {data.code: item_name for item_name, data in item_table.items() if data.code}

item_groups: Dict[str, Set[str]] = {
    "Upgrades": set(upgrades_table.keys()),
    "Magic": set(magic_table.keys()),
    "Badges": set(badges_table.keys()),
    "Collectables": set(collectables_table.keys()),
    "Town Members": set(recruit_table.keys())
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
