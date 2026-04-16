from typing import Any, cast, override

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart
from Options import CommonOptions, Option
from rule_builder import rules
from rule_builder.options import OPERATORS, REVERSE_OPERATORS, Operator

from .bases import RabiRibiWorldBase
from .constants import GAME_NAME
from .items import consumable_table, magic_table, recruit_table
from .names import ItemName
from .options import *

@dataclass()
class KnowledgeRule(rules.Rule[RabiRibiWorldBase], game = GAME_NAME):
    """Rule to check if the player has an knowledge level set or if the rule should be evaluated when out of logic."""
    value: int

    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        if world.options.knowledge >= self.value:
            return rules.True_().resolve(world)

        if getattr(world.multiworld, "generation_is_fake", False):
            return self.Resolved(
                self.value,
                player = world.player,
                caching_enabled = getattr(world, "rule_caching_enabled", False),
            )

        return rules.False_().resolve(world)

    class Resolved(rules.Rule.Resolved):
        value: int

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            return state.has(ItemName.glitched_logic, self.player)

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            deps = super().item_dependencies()
            deps.setdefault(ItemName.glitched_logic, set()).add(id(self))
            return deps

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            name = Knowledge.get_option_name(self.value)
            messages: list[JSONMessagePart] = [
                {"type": "color", "color": "yellow", "text": name},
            ]
            return messages

@dataclass()
class TrickDifficultyRule(rules.Rule[RabiRibiWorldBase], game = GAME_NAME):
    """Rule to check if the player has an trick difficulty set or if the rule should be evaluated when out of logic."""
    value: int

    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        if world.options.knowledge >= self.value:
            return rules.True_().resolve(world)

        if getattr(world.multiworld, "generation_is_fake", False):
            return self.Resolved(
                self.value,
                player = world.player,
                caching_enabled = getattr(world, "rule_caching_enabled", False),
            )

        return rules.False_().resolve(world)

    class Resolved(rules.Rule.Resolved):
        value: int

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            return state.has(ItemName.glitched_logic, self.player)

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            deps = super().item_dependencies()
            deps.setdefault(ItemName.glitched_logic, set()).add(id(self))
            return deps

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            name = TrickDifficulty.get_option_name(self.value)
            messages: list[JSONMessagePart] = [
                {"type": "color", "color": "yellow", "text": name},
            ]
            return messages

@dataclass()
class OutOfLogicOptionRule(rules.Rule[RabiRibiWorldBase], game = GAME_NAME):
    """Rule to check if the player has an option set or if the rule should be evaluated when out of logic."""
    name: str
    option: type[Option[Any]]
    value: Any
    operator: Operator = "eq"

    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        if self.check(world.options):
            return rules.True_().resolve(world)

        if getattr(world.multiworld, "generation_is_fake", False):
            return self.Resolved(
                self.name,
                player = world.player,
                caching_enabled = getattr(world, "rule_caching_enabled", False),
            )

        return rules.False_().resolve(world)

    def check(self, options: CommonOptions) -> bool:
        """Tests the given options dataclass to see if it passes this option filter"""
        option_name = next(
            (name for name, cls in options.__class__.type_hints.items() if cls is self.option),
            None,
        )
        if option_name is None:
            raise ValueError(f"Cannot find option {self.option.__name__} in options class {options.__class__.__name__}")
        opt = cast(Option[Any] | None, getattr(options, option_name, None))
        if opt is None:
            raise ValueError(f"Invalid option: {option_name}")

        fn = OPERATORS[self.operator]
        return fn(self.value, opt) if self.operator in REVERSE_OPERATORS else fn(opt, self.value)

    class Resolved(rules.Rule.Resolved):
        name: str

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            return state.has(ItemName.glitched_logic, self.player)

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            deps = super().item_dependencies()
            deps.setdefault(ItemName.glitched_logic, set()).add(id(self))
            return deps

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            messages: list[JSONMessagePart] = [
                {"type": "color", "color": "yellow", "text": self.name},
            ]
            return messages

@dataclass()
class HasEnoughAmuletFood(rules.Rule[RabiRibiWorldBase], game = GAME_NAME):
    """Rule to check if the player can utilize enough items to perform a trick."""
    num_amulet_food: int

    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        has_advanced_knowledge = world.options.knowledge.value >= Knowledge.option_advanced
        rainbow_shot_in_logic_enabled = bool(world.options.rainbow_shot_in_logic.value)
        return self.Resolved(
            self.num_amulet_food,
            has_advanced_knowledge,
            rainbow_shot_in_logic_enabled,
            player = world.player,
            caching_enabled = getattr(world, "rule_caching_enabled", False)
        )

    class Resolved(rules.Rule.Resolved):
        num_amulet_food: int
        has_advanced_knowledge: bool
        rainbow_shot_in_logic_enabled: bool

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            amulet = self.count_amulet_charges(state)
            food = 0

            if self.has_item_menu(state):
                if state.has(ItemName.rumi_donut, self.player) or state.has("Shop Access", self.player):
                    food = 1
                    # Eating a Rumi Donut gives an amulet charge
                    if self.can_bunny_amulet(state):
                        amulet += 1
                    food += self.count_normal_consumable_items(state)
                    # Kotri's buff can save enough amulet charge for an additional amulet use
                    if amulet >= 4 and state.has(ItemName.kotri_recruit, self.player) and \
                        state.has_from_list_unique(recruit_table, self.player, 3):
                        amulet += 1

            return (amulet + food) >= self.num_amulet_food

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            deps = super().item_dependencies()
            deps.setdefault(ItemName.bunny_amulet, set()).add(id(self))
            deps.setdefault(ItemName.easter_egg, set()).add(id(self))
            deps.setdefault(ItemName.glitched_logic, set()).add(id(self))

            deps.setdefault("Chapter 1", set()).add(id(self))
            deps.setdefault("Chapter 2", set()).add(id(self))
            deps.setdefault("Chapter 3", set()).add(id(self))
            deps.setdefault("Chapter 4", set()).add(id(self))
            deps.setdefault("Shop Access", set()).add(id(self))

            for consumable in consumable_table.keys():
                deps.setdefault(consumable, set()).add(id(self))
            for recruit in recruit_table:
                deps.setdefault(recruit, set()).add(id(self))
            for magic in magic_table.keys():
                deps.setdefault(magic, set()).add(id(self))

            return deps

        def count_amulet_charges(self, state: CollectionState) -> int:
            """Counts the number of amulet charges the player has"""
            if state.has(ItemName.bunny_amulet, self.player) or state.has("Chapter 2", self.player):
                if state.has(ItemName.rumi_recruit, self.player):
                    return 4
                if state.has("Shop Access", self.player) or state.has("Chapter 4", self.player):
                    return 3
                if state.has("Chapter 3", self.player):
                    return 2
                return 1
            return 0

        def count_normal_consumable_items(self, state: CollectionState) -> int:
            """Counts which normal consumable items the player can reach, either from locations or purchases."""
            consumables = 0
            if state.has(ItemName.rumi_cake, self.player) or state.has("Shop Access", self.player):
                consumables += 1
            if state.has(ItemName.cocoa_bomb, self.player) or self.can_purchase_cocoa_bomb(state):
                consumables += 1
            if state.has(ItemName.gold_carrot, self.player):
                consumables += 1
            return consumables

        def can_purchase_cocoa_bomb(self, state: CollectionState) -> bool:
            """Player can purchase cocoa bomb"""
            return state.has("Chapter 1", self.player) and \
                state.has(ItemName.cocoa_recruit, self.player) and \
                state.has_from_list_unique(recruit_table, self.player, 3)

        def can_bunny_amulet(self, state: CollectionState) -> bool:
            """Player can use the bunny amulet"""
            return state.has(ItemName.rumi_cake, self.player) or state.has("Shop Access", self.player)

        def has_item_menu(self, state: CollectionState) -> bool:
            """Player has access to the item menu"""
            return state.has("Chapter 1", self.player) or \
                (self.is_at_least_advanced_knowledge(state) and self.has_3_magic_types(state))

        def has_3_magic_types(self, state: CollectionState) -> bool:
            """Player has at least 3 types of magic"""
            # If playing with more than 5 Easter Eggs, Rainbow Shot could be used as a magic type
            return state.has_group_unique("Magic", self.player, 2) or \
                (self.rainbow_shot_in_logic(state) and state.has_group_unique("Magic", self.player, 1))

        def is_at_least_advanced_knowledge(self, state: CollectionState) -> bool:
            """Knowledge is at least advanced"""
            return self.has_advanced_knowledge or state.has(ItemName.glitched_logic, self.player)

        def rainbow_shot_in_logic(self, state: CollectionState) -> bool:
            """Player has Rainbow Shot and it's not out of logic by options"""
            return (self.rainbow_shot_in_logic_enabled or state.has(ItemName.glitched_logic, self.player)) and \
                state.has(ItemName.easter_egg, self.player, count = 5)

def from_option(option: type[Option], value: Any, operator: Operator = "eq") -> rules.Rule:
    return rules.True_(options=[rules.OptionFilter(option, value, operator)])