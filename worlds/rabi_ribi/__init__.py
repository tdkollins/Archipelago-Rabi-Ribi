"""
This module serves as an entrypoint into the Rabi-Ribi AP world.
"""
from collections import defaultdict
from typing import ClassVar, Dict, Set

from BaseClasses import ItemClassification
from Fill import swap_location_item
from worlds.AutoWorld import World, WebWorld
from worlds.LauncherComponents import Component, Type, components, launch_subprocess
from .items import RabiRibiItem, RabiRibiItemData, rabi_ribi_base_id, item_table, item_groups, get_base_item_list
from .locations import RegionDef, get_all_possible_locations
from .options import RabiRibiOptions
from .settings import RabiRibiSettings
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

    base_id: int = rabi_ribi_base_id

    item_name_groups = item_groups
    location_name_groups: Dict[str, Set[str]] = {}

    item_name_to_id = {name: data.code for name, data in item_table.items()}
    location_name_to_id: Dict[str, int] = {
        name: id_num for
        id_num, name in enumerate(get_all_possible_locations(), base_id)
    }

    settings: ClassVar[RabiRibiSettings]

    def __init__(self, multiworld, player):
        super().__init__(multiworld, player)
        self.total_locations = 0

    def generate_early(self) -> None:
        """Set world specific generation properties"""

        # Will be configurable later, but for now always force eggs to be local.
        self.options.local_items.value.add("Easter Egg")

    def create_item(self, name: str) -> RabiRibiItem:
        """Create a Rabi-Ribi item for this player"""

        data: RabiRibiItemData = item_table[name]
        return RabiRibiItem(name, data.classification, data.code, self.player)

    def create_event(self, name: str) -> RabiRibiItem:
        """Create a Rabi-Ribi event to help logic"""
        return RabiRibiItem(name, ItemClassification.progression, None, self.player)

    def create_regions(self) -> None:
        """
        Define regions and locations.
        This also defines access rules for the regions and locations.
        """
        region_def = RegionDef(self.multiworld, self.player, self.options)
        region_def.set_regions()
        region_def.connect_regions()
        self.total_locations = region_def.set_locations(self.location_name_to_id)
        region_def.set_events()

    def create_items(self) -> None:
        base_item_list = get_base_item_list()

        for item in map(self.create_item, base_item_list):
            if (not self.options.randomize_hammer.value) and (item.name == "Piko Hammer"):
                continue
            self.multiworld.itempool.append(item)

        junk = self.total_locations - len(base_item_list)
        self.multiworld.itempool += [self.create_item("Nothing") for _ in range(junk)]

    def fill_slot_data(self) -> dict:
        return {
            "openMode": self.options.open_mode.value,
            "attackMode": self.options.attack_mode.value
        }

    def set_rules(self) -> None:
        """
        Set remaining rules (for now this is just the win condition). 
        """
        self.multiworld.completion_condition[self.player] = \
            lambda state: state.has("Easter Egg", self.player, 5)

    def pre_fill(self) -> None:
        if not self.options.randomize_hammer.value:
            self.multiworld.get_location("Piko Hammer", self.player).place_locked_item(self.create_item("Piko Hammer"))

    @staticmethod
    def _handle_encourage_eggs_in_late_spheres(multiworld):
        worlds_with_option_enabled = set([
            world.player for world in multiworld.get_game_worlds("Rabi-Ribi")
            if world.options.encourage_eggs_in_late_spheres.value
        ])
        rr_player_spheres = defaultdict(lambda: [])
        for sphere in multiworld.get_spheres():
            new_player_spheres = defaultdict(lambda: [])
            for location in sphere:
                if location.game == "Rabi-Ribi" and location.player in worlds_with_option_enabled:
                    new_player_spheres[location.player].append(location)
            for player, sphere in new_player_spheres.items():
                rr_player_spheres[player].append(sphere)
        for player, spheres in rr_player_spheres.items():
            first_half_of_spheres = spheres[:len(spheres)//2]
            second_half_of_spheres = spheres[len(spheres)//2:]
            egg_locations_to_swap = []
            swappable_pool = []
            for sphere in first_half_of_spheres:
                for location in sphere:
                    if location.item.name == "Easter Egg":
                        egg_locations_to_swap.append(location)
            for sphere in second_half_of_spheres:
                for location in sphere:
                    if location.item.classification == ItemClassification.filler:
                        swappable_pool.append(location)
            idx = 0
            for new_egg_location in multiworld.random.sample(swappable_pool, min(len(egg_locations_to_swap), len(swappable_pool))):
                swap_location_item(egg_locations_to_swap[idx], new_egg_location, check_locked=False)
                idx += 1

    @classmethod
    def stage_post_fill(cls, multiworld) -> None:
        cls._handle_encourage_eggs_in_late_spheres(multiworld)
