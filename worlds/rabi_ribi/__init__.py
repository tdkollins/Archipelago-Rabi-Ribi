"""
This module serves as an entrypoint into the Rabi-Ribi AP world.
"""
from typing import Dict, Set

from .items import item_table, RabiRibiItem, get_base_item_list
from .locations import location_table, RabiRibiLocation
from .options import RabiRibiOptions
from .web import RabiRibiWeb
from worlds.AutoWorld import World, WebWorld
from BaseClasses import ItemClassification

class RabiRibiWorld(World):
    """
    Rabi-Ribi is a hybrid Bullet-Hell Metroidvania developped by CreSpirit and GameYue,
    released in 2016. It follows bunny-girl Erina and her fairy companion Ribbon in this
    cute, action-packed, and possibly pretty difficult adventure.
    """
    game: str = "Rabi-Ribi"
    options_dataclass = RabiRibiOptions
    options: RabiRibiOptions
    topology_present: bool = False
    web: WebWorld = RabiRibiWeb()

    base_id: int = 8350438193300

    item_name_to_id: Dict[str, int] = {
        name: id_num for
        id_num, name in enumerate(item_table.keys(), base_id)
    }
    location_name_to_id: Dict[str, int] = {
        name: id_num for
        id_num, name in enumerate(location_table.keys(), base_id)
    }

    item_name_groups: Dict[str, Set[str]] = {}
    location_name_groups: Dict[str, Set[str]] = {}

    def create_item(self, name: str) -> RabiRibiItem:
        """Create a Rabi-Ribi item for this player"""
        is_progression = RabiRibiItem.is_progression_item(name)
        classification = ItemClassification.progression if is_progression else \
            ItemClassification.filler
        return RabiRibiItem(name, classification, self.item_name_to_id[name], self.player)

    def create_items(self) -> None:
        base_item_list = get_base_item_list()

        for item in map(self.create_item, base_item_list):
            self.multiworld.itempool.append(item)

        junk = 0
        self.multiworld.itempool += [self.create_item("nothing") for _ in range(junk)]

    def generate_early(self) -> None:
        """Set world specific generation properties"""

        # Will be configurable later, but for now always force eggs to be local.
        self.multiworld.local_items[self.player].value.add("Easter Egg")
