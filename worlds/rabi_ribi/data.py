from collections import defaultdict
from dataclasses import dataclass, field
import itertools
import json
import pkgutil
import re
from typing import Any

from rule_builder import rules
from .options import Knowledge, TrickDifficulty


@dataclass
class ItemData:
    id: int
    name: str
    logic_key: str
    classification: str
    tags: list[str] = field(default_factory=list)
    exclude_from_default_pool: bool = False
    max_upgrades: int = 0
    max_count: int = 0


@dataclass
class LocationData:
    id: int
    name: str
    logic_key: str
    poptracker_name: str
    region: str
    area_id: int
    x_position: int
    y_position: int
    has_region: bool = False
    is_egg: bool = False
    requires_plurkwood: bool = False
    requires_warp_destination: bool = False
    requires_post_game: bool = False
    requires_post_irisu: bool = False
    requires_halloween: bool = False


@dataclass
class RegionData:
    name: str
    logic_key: str
    region: str
    has_warp: bool = False
    connections: dict[str, rules.Rule] = field(default_factory=dict)
    knowledge: int = Knowledge.option_basic
    trick_difficulty: int = TrickDifficulty.option_normal
    requires_plurkwood: bool = False
    requires_warp_destination: bool = False
    requires_post_game: bool = False
    requires_post_irisu: bool = False
    requires_halloween: bool = False


@dataclass
class EventData:
    name: str
    logic_key: str
    event_id: int = -1
    is_chapter: bool = False
    is_town_member: bool = False
    requires_plurkwood: bool = False
    requires_warp_destination: bool = False
    requires_post_game: bool = False
    requires_post_irisu: bool = False


@dataclass
class ConstraintChange:
    from_region: str
    to_region: str
    rule: rules.Rule


@dataclass
class ConstraintData:
    name: str
    logic_key: str
    weight: int
    requires_start_location_shuffle: bool = False
    requires_minimal_accessibility: bool = False
    changes: list[ConstraintChange] = field(default_factory=list)


class RabiRibiData:
    items: list[ItemData]
    locations: list[LocationData]
    regions: list[RegionData]
    events: list[EventData]
    constraints: list[ConstraintData]

    _ap_items: dict[str, ItemData]
    _ap_locations: dict[str, LocationData]
    _ap_regions: dict[str, RegionData]
    _ap_events: dict[str, EventData]
    _ap_constraints: dict[str, ConstraintData]

    _logic_items: dict[str, ItemData]
    _logic_locations: dict[str, LocationData]
    _logic_regions: dict[str, RegionData]
    _logic_events: dict[str, EventData]
    _logic_constraints: dict[str, ConstraintData]

    _locations_by_coordinates: dict[int, dict[tuple[int, int], LocationData]]

    def __init__(self) -> None:
        self.items = []
        self.locations = []
        self.regions = []
        self.events = []
        self.constraints = []

    def parse_data(
            self,
            item_data: list[ItemData],
            location_data: list[LocationData],
            region_data: list[RegionData],
            event_data: list[EventData],
            constraint_data: list[ConstraintData]):
        self.items = [item for item in item_data]
        self.locations = [location for location in location_data]
        self.regions = [region for region in region_data]
        self.events = [event for event in event_data]
        self.constraints = [constraint for constraint in constraint_data]

        # Add locations with logic to Regions
        location_regions = [RegionData(
            location.name,
            f"ITEM_{location.logic_key}",
            location.region,
            requires_plurkwood=location.requires_plurkwood,
            requires_warp_destination=location.requires_warp_destination,
            requires_post_game=location.requires_post_game,
            requires_post_irisu=location.requires_post_irisu,
            requires_halloween=location.requires_halloween
        ) for location in location_data if location.has_region]

        self.regions.extend(location_regions)

        self._ap_items = {item.name: item for item in self.items}
        self._ap_locations = {
            location.name: location for location in self.locations}
        self._ap_regions = {region.name: region for region in self.regions}
        self._ap_events = {event.name: event for event in self.events}
        self._ap_constraints = {
            constraint.name: constraint for constraint in self.constraints}

        self._logic_items = {item.logic_key: item for item in self.items}
        self._logic_locations = {
            location.logic_key: location for location in self.locations}
        self._logic_regions = {
            region.logic_key: region for region in self.regions}
        self._logic_events = {event.logic_key: event for event in self.events}
        self._logic_constraints = {
            constraint.logic_key: constraint for constraint in self.constraints}

        self._locations_by_coordinates = defaultdict(dict)
        for location in self.locations:
            self._locations_by_coordinates[location.area_id][(
                location.x_position, location.y_position)] = location

    def create_item_groups(self) -> dict[str, set[str]]:
        tags: set[str] = {tag for item in self.items for tag in item.tags}
        return {tag: {item.name for item in self.items if tag in item.tags} for tag in tags}

    def create_location_groups(self) -> dict[str, set[str]]:
        region_groups: itertools.groupby[str, LocationData] = itertools.groupby(
            self.locations, key=lambda l: l.region)
        return {region: {location.name for location in locations} for region, locations in region_groups}

    def get_item_by_ap_name(self, name: str) -> ItemData:
        return self._ap_items[name]

    def get_location_by_ap_name(self, name: str) -> LocationData:
        return self._ap_locations[name]

    def get_region_by_ap_name(self, name: str) -> RegionData:
        return self._ap_regions[name]

    def get_event_by_ap_name(self, name: str) -> EventData:
        return self._ap_events[name]

    def get_constraint_by_ap_name(self, name: str) -> ConstraintData:
        return self._ap_constraints[name]

    def get_item_by_logic_key(self, logic_key: str) -> ItemData:
        return self._logic_items[logic_key]

    def get_location_by_logic_key(self, logic_key: str) -> LocationData:
        return self._logic_locations[logic_key]

    def get_region_by_logic_key(self, logic_key: str) -> RegionData:
        return self._logic_regions[logic_key]

    def get_event_by_logic_key(self, logic_key: str) -> EventData:
        return self._logic_events[logic_key]

    def get_constraint_by_logic_key(self, logic_key: str) -> ConstraintData:
        return self._logic_constraints[logic_key]

    def get_item_ap_name(self, logic_key: str) -> str:
        return self._logic_items[logic_key].name

    def get_location_ap_name(self, logic_key: str) -> str:
        return self._logic_locations[logic_key].name

    def get_region_ap_name(self, logic_key: str) -> str:
        if logic_key.startswith("ITEM_"):
            logic_key = logic_key[5:]
            return self._logic_locations[logic_key].name
        return self._logic_regions[logic_key].name

    def is_region_key(self, logic_key: str) -> bool:
        return logic_key in self._logic_regions

    def is_item_key(self, logic_key: str) -> bool:
        return logic_key in self._logic_items

    def get_locations_in_area(self, area_id) -> dict[tuple[int, int], LocationData]:
        if area_id in self._locations_by_coordinates:
            return self._locations_by_coordinates[area_id]
        return {}

    def is_coordinates_location(self, area_id: int, x_position: int, y_position: int) -> bool:
        return area_id in self._locations_by_coordinates and (x_position, y_position) in self._locations_by_coordinates[area_id]

    def get_location_name_by_coordinates(self, area_id: int, x_position: int, y_position: int) -> str:
        return self._locations_by_coordinates[area_id][(x_position, y_position)].name

    def get_location_coordinates(self, name) -> tuple[int, int, int]:
        location = self._ap_locations[name]
        return (location.area_id, location.x_position, location.y_position)


def _load_json_data(data_name: str) -> list[Any]:
    file_data = pkgutil.get_data(__name__, "data/" + data_name)
    assert (isinstance(file_data, bytes))
    return json.loads(file_data.decode("utf-8-sig"))


data = RabiRibiData()


def _init() -> None:
    item_data: list[ItemData] = [
        ItemData(**item) for item in _load_json_data("items.json")]
    location_data: list[LocationData] = [LocationData(
        **item) for item in _load_json_data("locations.json")]
    region_data: list[RegionData] = [RegionData(
        **item) for item in _load_json_data("regions.json")]
    event_data: list[EventData] = [
        EventData(**item) for item in _load_json_data("events.json")]
    constraint_data: list[ConstraintData] = [ConstraintData(
        **item) for item in _load_json_data("constraints.json")]

    data.parse_data(item_data, location_data, region_data,
                    event_data, constraint_data)


_init()
