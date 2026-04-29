from typing import Any, override

from BaseClasses import MultiWorld
from rule_builder.rules import Rule
from worlds.AutoWorld import World

from .existing_randomizer.dataparser import RandomizerData
from .existing_randomizer.randomizer import parse_args
from .options import RabiRibiOptions

class RabiRibiWorldBase(World):
    options_dataclass = RabiRibiOptions
    options: RabiRibiOptions # pyright: ignore[reportIncompatibleVariableOverride]
    rule_macros: dict[str, Rule.Resolved]

    start_location: str
    picked_templates: list[str]
    map_transition_shuffle_order: list[int]
    map_transition_shuffle_spoiler: list[str]

    existing_randomizer_args: Any
    randomizer_data: RandomizerData

    def __init__(self, multiworld: MultiWorld, player: int) -> None:
        super().__init__(multiworld, player)
        self.rule_macros = {}

    @override
    def generate_early(self) -> None:
        super().generate_early()
        self.existing_randomizer_args = self._convert_options_to_existing_randomizer_args()
        self.randomizer_data = RandomizerData(self.existing_randomizer_args)

    def _convert_options_to_existing_randomizer_args(self):
        args = parse_args()
        args.ap_options = self.options
        args.open_mode = True
        args.shuffle_gift_items = True
        args.shuffle_map_transitions = self.options.shuffle_map_transitions.value
        args.shuffle_start_location = self.options.shuffle_start_location.value
        args.constraint_changes = self.options.number_of_constraint_changes.value
        return args