from typing import ClassVar

from BaseClasses import MultiWorld
from rule_builder.rules import Rule
from worlds.AutoWorld import World
from worlds.rabi_ribi.settings import RabiRibiSettings

from .options import RabiRibiOptions

class RabiRibiWorldBase(World):
    options_dataclass = RabiRibiOptions
    settings: ClassVar[RabiRibiSettings]  # pyright: ignore[reportIncompatibleVariableOverride]
    options: RabiRibiOptions  # pyright: ignore[reportIncompatibleVariableOverride]
    rule_macros: dict[str, Rule.Resolved]

    start_location: str
    picked_templates: list[str]
    map_transition_shuffle_order: list[int]
    map_transition_shuffle_spoiler: list[str]

    def __init__(self, multiworld: MultiWorld, player: int) -> None:
        super().__init__(multiworld, player)
        self.starting_characters = []
        self.rule_macros = {}