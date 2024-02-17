"""
This module serves as an entrypoint into the Rabi-Ribi AP world.
"""
from typing import Dict, Set

from BaseClasses import ItemClassification
from worlds.AutoWorld import World, WebWorld
from worlds.LauncherComponents import Component, components, launch_subprocess, Type
from .items import item_set, RabiRibiItem, get_base_item_list
from .locations import RegionDef, get_all_possible_locations
from .options import RabiRibiOptions
from .web import RabiRibiWeb

def launch_client():
    """Launch a rabi ribi client instance"""
    from worlds.rabi_ribi.client.client import launch
    launch_subprocess(launch, name="RabiRibiClient")

components.append(Component(
    "Rabi-Ribi Client",
    "RabiRibiClient",
    func=launch_client,
    component_type=Type.CLIENT
))

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

    item_name_groups: Dict[str, Set[str]] = {}
    location_name_groups: Dict[str, Set[str]] = {}

    item_name_to_id: Dict[str, int] = {
        name: id_num for
        id_num, name in enumerate(item_set, base_id)
    }
    item_name_to_id["Temp"] =  + base_id + len(item_name_to_id)
    location_name_to_id: Dict[str, int] = {
        name: id_num for
        id_num, name in enumerate(get_all_possible_locations(), base_id)
    }

    def __init__(self, multiworld, player):
        super().__init__(multiworld, player)
        self.region_def = RegionDef(multiworld, player)

    def create_item(self, name: str) -> RabiRibiItem:
        """Create a Rabi-Ribi item for this player"""
        is_progression = RabiRibiItem.is_progression_item(name)
        classification = ItemClassification.progression if is_progression else \
            ItemClassification.filler
        return RabiRibiItem(name, classification, self.item_name_to_id[name], self.player)

    def create_event(self, name: str) -> RabiRibiItem:
        """Create a Rabi-Ribi event to help logic"""
        return RabiRibiItem(name, True, None, self.player)

    def create_items(self) -> None:
        base_item_list = get_base_item_list()

        for item in map(self.create_item, base_item_list):
            self.multiworld.itempool.append(item)

        junk = len(self.location_name_to_id) - len(base_item_list)
        self.multiworld.itempool += [self.create_item("Temp") for _ in range(junk)]

    def create_regions(self) -> None:
        """
        Define regions and locations. 
        This also defines access rules for the regions and locations.
        """
        self.region_def.set_regions()
        self.region_def.connect_regions()
        self.region_def.set_locations(self.location_name_to_id)

    def generate_early(self) -> None:
        """Set world specific generation properties"""

        # Will be configurable later, but for now always force eggs to be local.
        self.multiworld.local_items[self.player].value.add("Easter Egg")

    def set_rules(self) -> None:
        """
        Set remaining rules (for now this is just the win condition). 
        """
        self.multiworld.completion_condition[self.player] = \
            lambda state: state.has("Easter Egg", self.player, 5)
