"""
This module serves as an entrypoint into the Rabi-Ribi AP world.
"""
import settings
import logging
from collections import defaultdict
from typing import Any, ClassVar, Dict, List, Optional, Set, TextIO
from BaseClasses import ItemClassification, Tutorial
from Fill import swap_location_item
from worlds.AutoWorld import World, WebWorld
from worlds.LauncherComponents import Component, Type, components, launch_subprocess
from .existing_randomizer.dataparser import RandomizerData
from .existing_randomizer.randomizer import parse_args
from .items import RabiRibiItem, RabiRibiItemData, item_data_table, item_groups, shufflable_gift_items, shufflable_gift_items_plurkwood, item_table, get_base_item_list
from .locations import all_locations, location_groups
from .names import ItemName, LocationName
from .options import RabiRibiOptions
from .regions import RegionHelper
from .utility import (
    get_rabi_ribi_base_id,
    convert_existing_rando_name_to_ap_name
)

logger = logging.getLogger('Rabi-Ribi')

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

class RabiRibiSettings(settings.Group):
    class GameInstallationPath(settings.UserFolderPath):
        """
        The installation folder of the game.
        """
        description = "Rabi-Ribi Installation Path"

    game_installation_path: GameInstallationPath = GameInstallationPath("C:/Program Files (x86)/Steam/steamapps/common/Rabi-Ribi")

class RabiRibiWeb(WebWorld):
    """Web integration for Rabi-Ribi"""
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Rabi-Ribi integration for Archipelago multiworld games.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Phie", "PsyMarth"]
    )]

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
    settings: ClassVar[RabiRibiSettings]
    web: WebWorld = RabiRibiWeb()

    base_id: int = get_rabi_ribi_base_id()

    item_name_groups: Dict[str, Set[str]] = item_groups
    location_name_groups: Dict[str, Set[str]] = location_groups

    item_name_to_id = item_table
    location_name_to_id: Dict[str, int] = all_locations

    start_location: str
    picked_templates: List[str]
    total_locations: int
    map_transition_shuffle_order: List[int]
    map_transition_shuffle_spoiler: List[str]
    existing_randomizer_args: Any
    randomizer_data: RandomizerData

    def generate_early(self) -> None:
        """Set world specific generation properties"""
        self.existing_randomizer_args = self._convert_options_to_existing_randomizer_args()
        self.randomizer_data = RandomizerData(self.existing_randomizer_args)

        # Will be configurable later, but for now always force eggs to be local.
        self.options.local_items.value.add(ItemName.easter_egg)

        # Force consumable items to be local, as the player may need to pick them up multiple times.
        self.options.local_items.value.update(item_groups["Consumables"])

    def create_item(self, name: str) -> RabiRibiItem:
        """Create a Rabi-Ribi item for this player"""

        data: RabiRibiItemData = item_data_table[name]
        return RabiRibiItem(name, data.classification, data.code, self.player)

    def create_event(self, name: str) -> RabiRibiItem:
        """Create a Rabi-Ribi event to help logic"""
        return RabiRibiItem(name, ItemClassification.progression, None, self.player)

    def create_regions(self) -> None:
        """
        Define regions and locations.
        This also defines access rules for the regions and locations.
        """
        self.topology_present = bool(self.options.shuffle_map_transitions.value)

        region_helper = RegionHelper(self)

        # Generate a world seed using the existing randomizer
        if self.should_regenerate_seed_for_universal_tracker():
            # Universal Tracker: Regenerate the seed used on the connected server
            passthrough = self.multiworld.re_gen_passthrough["Rabi-Ribi"] # type: ignore
            region_helper.regenerate_seed_for_universal_tracker(passthrough)
        else:
            # Use standard generation
            region_helper.generate_seed()

        region_helper.set_regions()
        region_helper.connect_regions()
        self.total_locations = region_helper.set_locations()
        region_helper.set_events()

        region_helper.configure_slot_data()
        region_helper.configure_region_spoiler_log_data()

    def create_items(self) -> None:
        base_item_list = get_base_item_list(self.randomizer_data)

        for item in map(self.create_item, base_item_list):
            if (not self.options.randomize_hammer.value) and (item.name == ItemName.piko_hammer):
                continue
            elif (not self.options.randomize_gift_items.value) and (item.name in shufflable_gift_items):
                continue
            elif (not self.options.randomize_gift_items) and \
                self.options.include_plurkwood and \
                item.name in shufflable_gift_items_plurkwood:
                continue
            self.multiworld.itempool.append(item)

        junk = self.total_locations - len(base_item_list)
        self.multiworld.itempool += [self.create_item(ItemName.nothing) for _ in range(junk)]

    def fill_slot_data(self) -> dict:
        return {
            "openMode": bool(self.options.open_mode.value),
            "attackMode": self.options.attack_mode.value,
            "randomize_gift_items": bool(self.options.randomize_gift_items.value),
            "include_plurkwood": bool(self.options.include_plurkwood.value),
            "include_warp_destination": bool(self.options.include_warp_destination.value),
            "include_post_game": bool(self.options.include_post_game.value),
            "include_post_irisu": bool(self.options.include_post_irisu.value),
            "include_halloween": bool(self.options.include_halloween.value),
            "picked_templates": self.picked_templates,
            "map_transition_shuffle_order": self.map_transition_shuffle_order,
            "shuffle_start_location": bool(self.options.shuffle_start_location.value),
            "start_location": self.start_location,
            "shuffle_music": bool(self.options.shuffle_music.value),
            "shuffle_backgrounds": bool(self.options.shuffle_backgrounds.value),
            "death_link": bool(self.options.death_link.value)
        }

    def set_rules(self) -> None:
        """
        Set remaining rules (for now this is just the win condition).
        """
        self.multiworld.completion_condition[self.player] = \
            lambda state: state.has(ItemName.easter_egg, self.player, 5)

    def pre_fill(self) -> None:
        if not self.options.randomize_hammer.value:
            self.multiworld.get_location(LocationName.piko_hammer, self.player).place_locked_item(self.create_item(ItemName.piko_hammer))

    def write_spoiler(self, spoiler_handle: TextIO) -> None:
        spoiler_handle.write(f'\nStart Location: {self.start_location}\n')

        spoiler_handle.write(f'\nApplied Map Constraints:\n')
        for template in self.picked_templates:
            spoiler_handle.write(f'\n{convert_existing_rando_name_to_ap_name(template)}')

        spoiler_handle.write(f'\n\nMap Transitions:\n')
        for entrance in self.map_transition_shuffle_spoiler:
            spoiler_handle.write(f'\n{entrance}')

    def _convert_options_to_existing_randomizer_args(self):
        args = parse_args()
        args.ap_options = self.options
        args.open_mode = self.options.open_mode.value
        args.shuffle_gift_items = self.options.randomize_gift_items.value
        args.shuffle_map_transitions = self.options.shuffle_map_transitions.value
        args.shuffle_start_location = self.options.shuffle_start_location.value

        if self.options.enable_constraint_changes.value:
            args.constraint_changes = self.options.number_of_constraint_changes.value

        return args

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
                    if location.item.name == ItemName.easter_egg:
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

    # Methods for the universal tracker, not called in standard gen
    @staticmethod
    def interpret_slot_data(slot_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        This method exists as a hook for Universal Tracker. When this method is implemented in a world, Universal Tracker
        will perform a second world generation attempt when the player connects to the server, allowing the world access
        to slot_data to set variables that were randomly assigned during generation.
        """
        # https://github.com/FarisTheAncient/Archipelago/blob/tracker/worlds/tracker/docs/re-gen-passthrough.md
        return slot_data

    def should_regenerate_seed_for_universal_tracker(self):
        """
        If true, this world has information from Universal Tracker that should be used when generating the seed.
        This ensures that the world state matches the seed used by the connected server.
        """
        return hasattr(self.multiworld, "re_gen_passthrough") and "Rabi-Ribi" in self.multiworld.re_gen_passthrough # type: ignore
