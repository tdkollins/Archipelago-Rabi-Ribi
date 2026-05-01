"""
This module serves as an entrypoint into the Rabi-Ribi AP world.
"""
import math
import logging
from collections import defaultdict
from itertools import chain
from typing import Any, ClassVar, Optional, TextIO, override
from BaseClasses import ItemClassification, Location, MultiWorld
from Fill import swap_location_item
from Options import OptionError
from worlds.AutoWorld import WebWorld
from .constants import GAME_NAME, BASE_ID
from .data import data
from .items import RabiRibiItem, RabiRibiItemData, item_data_table, item_groups, item_table, filler_items, get_base_item_list
from .locations import all_locations, location_groups
from .names import ItemName
from .regions import RegionHelper
from .rules import parse_connections
from .settings import RabiRibiSettings
from .tracker import RabiRibiUTWorld
from .web_world import RabiRibiWeb

logger = logging.getLogger(GAME_NAME)

class RabiRibiWorld(RabiRibiUTWorld):
    """
    Rabi-Ribi is a hybrid Bullet-Hell Metroidvania developped by CreSpirit and GameYue,
    released in 2016. It follows bunny-girl Erina and her fairy companion Ribbon in this
    cute, action-packed, and possibly pretty difficult adventure.
    """

    game: ClassVar[str] = GAME_NAME
    settings: ClassVar[RabiRibiSettings] # pyright: ignore[reportIncompatibleVariableOverride]
    web: ClassVar[WebWorld] = RabiRibiWeb()
    base_id: int = BASE_ID
    topology_present: bool = False

    item_name_groups: ClassVar[dict[str, set[str]]] = item_groups
    location_name_groups: ClassVar[dict[str, set[str]]] = location_groups
    item_name_to_id: ClassVar[dict[str, int]] = item_table
    location_name_to_id: ClassVar[dict[str, int]] = all_locations

    total_locations: int
    required_egg_count: int
    filler_items: Optional[list[str]] = None

    @override
    def generate_early(self) -> None:
        """Set world specific generation properties"""
        super().generate_early()

        if self.options.encourage_eggs_in_late_spheres.value and self.options.rainbow_shot_in_logic.value:
            raise OptionError(f"Rabi-Ribi: Rainbow Egg In Logic is not compatible with Encourage Eggs in Late Spheres. "
                              f"Player {self.player} ({self.player_name}) needs to disable one of these options.")

        # Will be configurable later, but for now always force eggs to be local
        self.options.local_items.value.add(ItemName.easter_egg)

        parse_connections()

    @override
    def create_item(self, name: str, force_classification: Optional[ItemClassification] = None) -> RabiRibiItem:
        """Create a Rabi-Ribi item for this player"""
        # Universal Tracker: Allow creation of a fake event to represent out of logic checks
        if name == ItemName.glitched_logic:
            return RabiRibiItem(name, ItemClassification.progression, None, self.player)

        data: RabiRibiItemData = item_data_table[name]
        classification = force_classification if force_classification is not None else data.classification
        return RabiRibiItem(name, classification, data.code, self.player)

    def create_event(self, name: str) -> RabiRibiItem:
        """Create a Rabi-Ribi event to help logic"""
        return RabiRibiItem(name, ItemClassification.progression, None, self.player)

    @override
    def create_regions(self) -> None:
        """
        Define regions and locations.
        This also defines access rules for the regions and locations.
        """
        self.topology_present = bool(self.options.shuffle_map_transitions.value)

        region_helper = RegionHelper(self)

        # Generate a world seed using the existing randomizer
        if self.is_ut:
            # Universal Tracker: Regenerate the seed used on the connected server
            region_helper.generate_set_seed()
        else:
            # Use standard generation
            region_helper.generate_seed()

        region_helper.set_regions()
        region_helper.connect_regions()
        self.total_locations = region_helper.set_locations()
        region_helper.set_events()

        region_helper.configure_slot_data()
        region_helper.configure_region_spoiler_log_data()

    def get_filler_item_name(self) -> str:
        """Called when the item pool needs to be filled with additional items to match location count."""
        if self.filler_items is None:
            # Create a list of lists for every potion, then flatten and shuffle
            all_potions_grouped = [([key] * value) for key, value in filler_items.items()]
            self.filler_items = list(chain(*all_potions_grouped))
            self.random.shuffle(self.filler_items)
        if len(self.filler_items) == 0:
            # All potions placed
            return ItemName.nothing
        return self.filler_items.pop(0)

    def create_items(self) -> None:
        base_item_list = get_base_item_list()
        base_items = map(self.create_item, base_item_list)
        self.multiworld.itempool.extend(base_items)

        max_egg_locations_in_pool = self.total_locations - len(base_item_list)
        total_egg_count = min(max_egg_locations_in_pool, self.options.max_number_of_easter_eggs.value)
        self.required_egg_count = max(math.floor(total_egg_count * (self.options.percentage_of_easter_eggs.value / 100.0)), 1)
        filler_egg_count = total_egg_count - self.required_egg_count

        self.multiworld.itempool.extend([self.create_item(ItemName.easter_egg) for _ in range(self.required_egg_count)])
        self.multiworld.itempool.extend([self.create_item(ItemName.easter_egg, ItemClassification.useful) for _ in range(filler_egg_count)])

        junk = self.total_locations - len(base_item_list) - total_egg_count
        self.multiworld.itempool += [self.create_item(self.get_filler_item_name()) for _ in range(junk)]

    def fill_slot_data(self) -> dict:
        return {
            "required_egg_count": self.required_egg_count,
            "attackMode": self.options.attack_mode.value,
            "apply_beginner_mod": bool(self.options.apply_beginner_mod.value),
            "include_plurkwood": bool(self.options.include_plurkwood.value),
            "include_warp_destination": bool(self.options.include_warp_destination.value),
            "include_post_game": bool(self.options.include_post_game.value),
            "include_post_irisu": bool(self.options.include_post_irisu.value),
            "include_halloween": bool(self.options.include_halloween.value),
            "picked_templates": self.picked_templates,
            "map_transition_shuffle_order": self.map_transition_shuffle_order,
            "start_location": self.start_location,
            "shuffle_music": bool(self.options.shuffle_music.value),
            "shuffle_backgrounds": bool(self.options.shuffle_backgrounds.value),
            "allow_laggy_backgrounds": bool(self.options.allow_laggy_backgrounds.value),
            "allow_difficult_backgrounds": bool(self.options.allow_difficult_backgrounds.value),
            "shuffle_backgrounds": bool(self.options.shuffle_backgrounds.value),
            "death_link": bool(self.options.death_link.value),
            "options": self.options.as_dict(
                "knowledge",
                "trick_difficulty",
                "block_clips_required",
                "semi_solid_clips_required",
                "zips_required",
                "darkness_without_light_orb",
                "underwater_without_water_orb",
                "carrot_shooter_in_logic",
                "event_warps_in_logic",
                "include_plurkwood",
                "include_warp_destination",
                "include_post_game",
                "include_post_irisu",
                "include_halloween",
                "number_of_constraint_changes",
                "shuffle_map_transitions",
                "shuffle_start_location",
                "max_number_of_easter_eggs",
                "percentage_of_easter_eggs",)
        }

    def set_rules(self) -> None:
        """
        Set remaining rules (for now this is just the win condition).
        """
        self.multiworld.completion_condition[self.player] = \
            lambda state: state.has(ItemName.easter_egg, self.player, self.required_egg_count)

    def write_spoiler_header(self, spoiler_handle: TextIO) -> None:
        if self.options.shuffle_start_location.value:
            spoiler_handle.write(f'\nStart Location ({self.player_name}): {self.start_location}')

        if self.options.shuffle_map_transitions.value:
            spoiler_handle.write(f'\n\nMap Transitions ({self.player_name}):\n')
            self.map_transition_shuffle_spoiler.sort()
            for entrance in self.map_transition_shuffle_spoiler:
                spoiler_handle.write(f'\n{entrance}')

        if self.options.number_of_constraint_changes.value > 0:
            spoiler_handle.write(f'\n\nApplied Map Constraints ({self.player_name}):\n')
            constraint_names = [
                data.get_constraint_by_logic_key(template).name
                for template
                in self.picked_templates]
            constraint_names.sort()
            for constraint in constraint_names:
                spoiler_handle.write(f'\n{constraint}')

    @staticmethod
    def _handle_encourage_eggs_in_late_spheres(multiworld: MultiWorld):
        worlds_with_option_enabled = set([
            world.player for world in multiworld.get_game_worlds(GAME_NAME)
            if isinstance(world, RabiRibiWorld) and world.options.encourage_eggs_in_late_spheres.value
        ])
        rr_player_spheres: defaultdict[int, list[list[Location]]] = defaultdict(list)
        for sphere in multiworld.get_spheres():
            # For minimal accessibility, get_spheres() returns an empty sphere
            # before returning a sphere containing unreachable locations
            if len(sphere) == 0:
                break
            new_player_spheres: defaultdict[int, list[Location]] = defaultdict(list)
            for location in sphere:
                if location.game == GAME_NAME and location.player in worlds_with_option_enabled:
                    new_player_spheres[location.player].append(location)
            for player, sphere in new_player_spheres.items():
                rr_player_spheres[player].append(sphere)
        for player, spheres in rr_player_spheres.items():
            first_half_of_spheres = spheres[:len(spheres)//2]
            second_half_of_spheres = spheres[len(spheres)//2:]
            egg_locations_to_swap: list[Location] = []
            swappable_pool: list[Location] = []
            for sphere in first_half_of_spheres:
                for location in sphere:
                    assert location.item is not None
                    if (location.item.name == ItemName.easter_egg):
                        egg_locations_to_swap.append(location)
            for sphere in second_half_of_spheres:
                for location in sphere:
                    assert location.item is not None
                    if location.item.classification == ItemClassification.filler:
                        swappable_pool.append(location)
            # As locations are found in spheres, which are unordered sets,
            # we need to sort them before shuffling and swapping
            # for deterministic behavior.
            egg_locations_to_swap.sort()
            swappable_pool.sort()
            multiworld.worlds[player].random.shuffle(swappable_pool)
            for old_position, new_position in zip(egg_locations_to_swap, swappable_pool):
                swap_location_item(old_position, new_position, check_locked=False)

    @classmethod
    def stage_post_fill(cls, multiworld) -> None:
        cls._handle_encourage_eggs_in_late_spheres(multiworld)

    # Methods for the universal tracker, not called in standard gen
    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        """
        This method exists as a hook for Universal Tracker. When this method is implemented in a world, Universal Tracker
        will perform a second world generation attempt when the player connects to the server, allowing the world access
        to slot_data to set variables that were randomly assigned during generation.
        """
        # https://github.com/FarisTheAncient/Archipelago/blob/tracker/worlds/tracker/docs/re-gen-passthrough.md
        return slot_data