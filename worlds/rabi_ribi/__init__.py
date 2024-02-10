"""
This module serves as an entrypoint into the Rabi-Ribi AP world.
"""
from typing import Dict, Set

from .items import item_table, RabiRibiItem
from .locations import location_table, RabiRibiLocation
from .options import RabiRibiOptions
from .web import RabiRibiWeb
from worlds.AutoWorld import World, WebWorld

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
        return NotImplementedError()
