"""This module represents item definitions for Rabi-Ribi"""
from typing import NamedTuple, Optional

from BaseClasses import Item, ItemClassification
from .constants import GAME_NAME, BASE_ID
from .data import data
from .names import ItemName

class RabiRibiItem(Item):
    """Rabi Ribi Item Definition"""
    game: str = GAME_NAME

    def __init__(self, name, classification: ItemClassification, code: Optional[int], player: int):
        super(RabiRibiItem, self).__init__(name, classification, code, player)

class RabiRibiItemData(NamedTuple):
    code: Optional[int]
    classification: ItemClassification = ItemClassification.filler

item_data_table : dict[str, RabiRibiItemData] = {
    item.name: RabiRibiItemData(BASE_ID + item.id, ItemClassification[item.classification])
    for item in data.items
}

item_table: dict[str, int] = {name: data.code for name, data in item_data_table.items() if data.code is not None }

lookup_item_id_to_name: dict[int, str] = {data.code: item_name for item_name, data in item_data_table.items() if data.code}

item_groups: dict[str, set[str]] = data.create_item_groups()

filler_items : dict[str, int] = {
    ItemName.hp_up: 25,
    ItemName.mp_up: 25,
    ItemName.attack_up: 20,
    ItemName.pack_up: 15,
    ItemName.regen_up: 15
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

def get_base_item_list() -> list[str]:
    return [item.name for item in data.items if not item.exclude_from_default_pool]
