import logging
from typing import Any, override

from BaseClasses import MultiWorld
from Options import OptionError
from rule_builder.rules import Rule
from worlds.AutoWorld import World

from .constants import GAME_NAME
from .data import data
from .existing_randomizer.dataparser import RandomizerData
from .existing_randomizer.randomizer import parse_args
from .options import RabiRibiOptions

logger = logging.getLogger(GAME_NAME)


class RabiRibiWorldBase(World):
    options_dataclass = RabiRibiOptions
    # pyright: ignore[reportIncompatibleVariableOverride]
    options: RabiRibiOptions
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
        self.update_minimum_number_of_constraints()
        self.detect_excluded_required_constraint()
        self.detect_conflicting_constraints()

    def update_minimum_number_of_constraints(self):
        if self.options.number_of_constraint_changes < len(self.options.required_constraints.value):
            logger.warning(
                f"Rabi-Ribi: Updating player {self.player} ({self.player_name})'s number of constraints changes "
                "to minimum required for their selected required constraints."
            )
            self.options.number_of_constraint_changes.value = len(
                self.options.required_constraints.value)

    def detect_excluded_required_constraint(self):
        exclude_required_constraints = [
            constraint
            for constraint in self.options.exclude_constraints
            if constraint in self.options.required_constraints
        ]
        if any(exclude_required_constraints):
            raise OptionError(
                f"Rabi-Ribi: A required template is also selected to be excluded: {exclude_required_constraints[0]}. "
                f"Player {self.player} ({self.player_name}) needs to update their selected templates.")

    def detect_conflicting_constraints(self):
        required_constraints = {
            constraint.logic_key
            for constraint in data.constraints
            if constraint.name in self.options.required_constraints
        }
        required_templates = {
            template
            for template in self.randomizer_data.template_constraints
            if template.name in required_constraints
        }

        # Build set of conflicting templates to compare against
        conflicting_templates = set()
        for template in required_templates:
            for conflict in template.conflicts_names:
                if conflict != template.name:
                    conflicting_templates.add(conflict)

        for template in required_templates:
            if template.name in conflicting_templates:
                template_name = data.get_constraint_by_logic_key(
                    template.name).name
                raise OptionError(
                    f"Rabi-Ribi: Conflicting required templates detected: "
                    f"{template_name} conflicts with one or more required templates. "
                    f"Player {self.player} ({self.player_name}) needs to disable one of these templates.")


    def _convert_options_to_existing_randomizer_args(self):
        args = parse_args()
        args.ap_options = self.options
        args.open_mode = True
        args.shuffle_gift_items = True
        args.shuffle_map_transitions = self.options.shuffle_map_transitions.value
        args.shuffle_start_location = self.options.shuffle_start_location.value
        args.constraint_changes = self.options.number_of_constraint_changes.value
        return args
