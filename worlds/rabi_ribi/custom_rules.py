import dataclasses
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Iterable, Mapping, Never, Protocol, Self, TypeVar, cast, override, runtime_checkable

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart
from Options import CommonOptions, Option
from rule_builder import rules
from rule_builder.options import OPERATORS, REVERSE_OPERATORS, Operator, OptionFilter

from .bases import RabiRibiWorldBase
from .constants import GAME_NAME
from .items import item_groups, recruit_table, recruit_table_irisu
from .names import ItemName
from .options import *

class LogicState(Enum):
    CannotReach = 0
    InLogic = 1
    OutOfLogic = 2
    Explain = 3

def get_indent(depth: int):
    hyphen = "- "
    spaces = depth * 4
    return "" if depth == 0 else f"{hyphen:>{spaces}}"

def evaluate_rule(rule: rules.Rule.Resolved, state: CollectionState | None, glitched_state: CollectionState | None) -> LogicState:
    if state is None:
        return LogicState.Explain
    if rule(state): # type: ignore
        return LogicState.InLogic
    if glitched_state is not None and rule(glitched_state): # type: ignore
        return LogicState.OutOfLogic
    return LogicState.CannotReach

def get_color(result: LogicState) -> str:
    if result == LogicState.Explain:
        return "cyan"
    if result == LogicState.InLogic:
        return "green"
    if result == LogicState.OutOfLogic:
        return "yellow"
    return "salmon"

def get_prefix(result: LogicState, depth: int) -> list[JSONMessagePart]:
    indent = get_indent(depth)
    text = "Can " if result != LogicState.CannotReach else "Cannot "
    return [{"type": "text", "text": f"{indent}{text}"}]

def get_suffix(result: LogicState) -> list[JSONMessagePart]:
    suffix =  " (Out of Logic)" if result == LogicState.OutOfLogic else ""
    return [{"type": "text", "text": suffix}]

@runtime_checkable
class GlitchedLogicMixIn(Protocol):
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass

    def get_rule_tree_message(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
        return list()

    def explain_rule_glitched(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
        assert isinstance(self, rules.Rule.Resolved)
        if self.always_true:
            return []
        result = evaluate_rule(self, state, glitched_state)
        return (
            get_prefix(result, depth)
            + self.get_rule_tree_message(state, glitched_state, depth + 1)
            + get_suffix(result)
        )

class CustomRuleRegisterProtocolMeta(rules.CustomRuleRegister, type(Protocol)):
    pass

@dataclasses.dataclass()
class True_(rules.True_[RabiRibiWorldBase], game=GAME_NAME):
    class Resolved(rules.True_.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
        @override
        def get_rule_tree_message(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            return self.explain_json(state)

@dataclasses.dataclass()
class False_(rules.False_[RabiRibiWorldBase], game=GAME_NAME):
    class Resolved(rules.False_.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
        @override
        def get_rule_tree_message(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            return self.explain_json(state)

@dataclasses.dataclass(init=False)
class RabiRibiAnd(rules.NestedRule[RabiRibiWorldBase], game=GAME_NAME):
    """A rule that only returns true when all child rules evaluate as true"""

    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        children_to_process = [c.resolve(world) for c in self.children]
        clauses: list[rules.Rule.Resolved] = []
        items: dict[str, int] = {}
        true_rule: rules.Rule.Resolved | None = None

        while children_to_process:
            child = children_to_process.pop(0)
            if child.always_false:
                # false always wins
                return child
            if child.always_true:
                # dedupe trues
                true_rule = child
                continue
            if isinstance(child, RabiRibiAnd.Resolved):
                children_to_process.extend(child.children)
                continue

            if isinstance(child, Has.Resolved):
                if child.item_name not in items or items[child.item_name] < child.count:
                    items[child.item_name] = child.count
            elif isinstance(child, HasAll.Resolved):
                for item in child.item_names:
                    if item not in items:
                        items[item] = 1
            elif isinstance(child, rules.HasAllCounts.Resolved):
                raise NotImplementedError("Rabi-Ribi missing HasAllCounts")
            else:
                clauses.append(child)

        if not clauses and not items:
            return true_rule or False_().resolve(world)

        if len(items) == 1:
            item, count = next(iter(items.items()))
            clauses.append(Has(item, count).resolve(world))
        elif items and all(count == 1 for count in items.values()):
            clauses.append(HasAll(*items).resolve(world))
        elif items:
            raise NotImplementedError("Rabi-Ribi missing HasAllCounts")

        if len(clauses) == 1:
            return clauses[0]

        return RabiRibiAnd.RabiRibiResolved(
            tuple(clauses),
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    class RabiRibiResolved(rules.NestedRule.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
        @override
        def explain_rule_glitched(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            indent = get_indent(depth)
            suffix = get_suffix(result)
            messages: list[JSONMessagePart] = [
                {"type": "text", "text": indent},
                {"type": "text", "text": "Missing" if result == LogicState.CannotReach else "Has"},
                *suffix,
                {"type": "color", "color": "cyan", "text": " some" if result == LogicState.CannotReach else " all"},
                {"type": "text", "text": " of:\n"},
            ]
            for idx, child in enumerate(self.children):
                assert isinstance(child, GlitchedLogicMixIn)
                messages.extend(child.explain_rule_glitched(state, glitched_state, depth + 1))
                if idx < (len(self.children) - 1):
                    messages.append({"type": "text", "text": "\n"})
            return messages


@dataclasses.dataclass(init=False)
class RabiRibiOr(rules.NestedRule[RabiRibiWorldBase], game=GAME_NAME):
    """A rule that returns true when any child rule evaluates as true"""

    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        children_to_process = [c.resolve(world) for c in self.children]
        clauses: list[rules.Rule.Resolved] = []
        items: dict[str, int] = {}

        while children_to_process:
            child = children_to_process.pop(0)
            if child.always_true:
                # true always wins
                return child
            if child.always_false:
                # falses can be ignored
                continue
            if isinstance(child, RabiRibiOr.Resolved):
                children_to_process.extend(child.children)
                continue

            if isinstance(child, Has.Resolved):
                if child.item_name not in items or child.count < items[child.item_name]:
                    items[child.item_name] = child.count
            elif isinstance(child, HasAny.Resolved):
                for item in child.item_names:
                    items[item] = 1
            elif isinstance(child, rules.HasAnyCount.Resolved):
                raise NotImplementedError("Rabi-Ribi missing HasAnyCount")
            else:
                clauses.append(child)

        if not clauses and not items:
            return False_().resolve(world)

        if len(items) == 1:
            item, count = next(iter(items.items()))
            clauses.append(Has(item, count).resolve(world))
        elif items and all(count == 1 for count in items.values()):
            clauses.append(HasAny(*items).resolve(world))
        elif items:
            raise NotImplementedError("Rabi-Ribi missing HasAnyCount")

        if len(clauses) == 1:
            return clauses[0]

        return RabiRibiOr.RabiRibiResolved(
            tuple(clauses),
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    class RabiRibiResolved(rules.NestedRule.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
        @override
        def explain_rule_glitched(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            indent = get_indent(depth)
            suffix = get_suffix(result)
            messages: list[JSONMessagePart] = [
                {"type": "text", "text": indent},
                {"type": "text", "text": "Missing" if result == LogicState.CannotReach else "Has"},
                *suffix,
                {"type": "color", "color": "cyan", "text": " all" if result == LogicState.CannotReach else " some"},
                {"type": "text", "text": " of:\n"},
            ]
            for idx, child in enumerate(self.children):
                assert isinstance(child, GlitchedLogicMixIn)
                messages.extend(child.explain_rule_glitched(state, glitched_state, depth + 1))
                if idx < (len(self.children) - 1):
                    messages.append({"type": "text", "text": "\n"})
            return messages

@dataclasses.dataclass()
class Rule(rules.Rule[RabiRibiWorldBase], game = GAME_NAME):
    """Base class for a static rule used to generate an access rule"""

    options: Iterable[OptionFilter] = dataclasses.field(default=(), kw_only=True)
    """An iterable of OptionFilters to restrict what options are required for this rule to be active"""

    filtered_resolution: bool = dataclasses.field(default=False, kw_only=True)
    """If this rule should default to True or False when filtered by its options"""

    game_name: ClassVar[str]
    """The name of the game this rule belongs to, default rules belong to 'Archipelago'"""

    @override
    def __and__(self, other: "rules.Rule[Any] | Iterable[OptionFilter] | OptionFilter") -> rules.Rule[RabiRibiWorldBase]:
        """Combines two rules or a rule and an option filter into an And rule"""
        if isinstance(other, OptionFilter):
            other = (other,)
        if isinstance(other, Iterable):
            if not other:
                return self
            return rules.Filtered(self, options=other)
        if self.options == other.options:
            if isinstance(self, RabiRibiAnd):
                if isinstance(other, RabiRibiAnd):
                    return RabiRibiAnd(*self.children, *other.children, options=self.options)
                return RabiRibiAnd(*self.children, other, options=self.options)
            if isinstance(other, RabiRibiAnd):
                return RabiRibiAnd(self, *other.children, options=other.options)
        return RabiRibiAnd(self, other)


    @override
    def __rand__(self, other: "rules.Rule[Any] | Iterable[OptionFilter] | OptionFilter") -> rules.Rule[RabiRibiWorldBase]:
        return self.__and__(other)

    @override
    def __or__(self, other: "rules.Rule[Any] | Iterable[OptionFilter] | OptionFilter") -> rules.Rule[RabiRibiWorldBase]:
        """Combines two rules or a rule and an option filter into an Or rule"""
        if isinstance(other, OptionFilter):
            other = (other,)
        if isinstance(other, Iterable):
            if not other:
                return self
            return RabiRibiOr(self, True_(options=other))
        if self.options == other.options:
            if isinstance(self, RabiRibiOr):
                if isinstance(other, RabiRibiOr):
                    return RabiRibiOr(*self.children, *other.children, options=self.options)
                return RabiRibiOr(*self.children, other, options=self.options)
            if isinstance(other, RabiRibiOr):
                return RabiRibiOr(self, *other.children, options=self.options)
        return RabiRibiOr(self, other)

    @override
    def __ror__(self, other: "rules.Rule[Any] | Iterable[OptionFilter] | OptionFilter") -> rules.Rule[RabiRibiWorldBase]:
        return self.__or__(other)


class Has(rules.Has[RabiRibiWorldBase], game = GAME_NAME):
    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        return self.RabiRibiResolved(
            self.item_name,
            self.count,
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    @override
    class RabiRibiResolved(rules.Has.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
        @override
        def get_rule_tree_message(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            verb = "Missing " if result == LogicState.CannotReach else "Has "
            messages: list[JSONMessagePart] = [{"type": "text", "text": verb}]
            if self.count > 1:
                messages.append({"type": "color", "color": "cyan", "text": str(self.count)})
                messages.append({"type": "text", "text": "x "})
            if state:
                color = get_color(result)
                messages.append({"type": "color", "color": color, "text": self.item_name})
            else:
                messages.append({"type": "item_name", "flags": 0b001, "text": self.item_name, "player": self.player})
            return messages

class HasAll(rules.HasAll[RabiRibiWorldBase], game = GAME_NAME):
    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        if len(self.item_names) == 0:
            # match state.has_all
            return True_().resolve(world)
        if len(self.item_names) == 1:
            return Has(self.item_names[0]).resolve(world)
        return self.RabiRibiResolved(
            self.item_names,
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    @override
    class RabiRibiResolved(rules.HasAll.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
        @override
        def explain_rule_glitched(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            indent = get_indent(depth)
            child_indent = get_indent(depth + 1)
            messages: list[JSONMessagePart] = []
            if result == LogicState.Explain:
                messages = [
                    {"type": "text", "text": "Has "},
                    {"type": "color", "color": "cyan", "text": "all"},
                    {"type": "text", "text": " of ("},
                ]
                for i, item in enumerate(self.item_names):
                    if i > 0:
                        messages.append({"type": "text", "text": ", "})
                    messages.append({"type": "item_name", "flags": 0b001, "text": item, "player": self.player})
                messages.append({"type": "text", "text": ")"})
                return messages

            assert state is not None
            assert glitched_state is not None
            found = [item for item in self.item_names if state.has(item, self.player)]
            out_of_logic = [item for item in self.item_names if glitched_state.has(item, self.player)]
            out_of_logic_only = [item for item in out_of_logic if item not in found]
            missing = [item for item in self.item_names if item not in found] \
                if result == LogicState.InLogic \
                else [item for item in self.item_names if item not in out_of_logic]

            messages = [
                {"type": "text", "text": indent},
                {"type": "text", "text": "Has " if not missing else "Missing "},
                {"type": "color", "color": "cyan", "text": "all" if not missing else "some"},
                {"type": "text", "text": " of\n"},
            ]
            if found:
                messages.append({"type": "text", "text": f"{child_indent}Found: "})
                for i, item in enumerate(found):
                    if i > 0:
                        messages.append({"type": "text", "text": ", "})
                    messages.append({"type": "color", "color": "green", "text": item})
                if missing or out_of_logic_only:
                    messages.append({"type": "text", "text": "\n"})

            if out_of_logic_only:
                messages.append({"type": "text", "text": f"{child_indent}Out of Logic: "})
                for i, item in enumerate(out_of_logic_only):
                    if i > 0:
                        messages.append({"type": "text", "text": ", "})
                    messages.append({"type": "color", "color": "yellow", "text": item})
                if missing:
                    messages.append({"type": "text", "text": "\n"})

            if missing:
                messages.append({"type": "text", "text": f"{child_indent}Missing: "})
                for i, item in enumerate(missing):
                    if i > 0:
                        messages.append({"type": "text", "text": ", "})
                    messages.append({"type": "color", "color": "salmon", "text": item})
            messages.append({"type": "text", "text": "\n"})
            return messages

class HasAny(rules.HasAny[RabiRibiWorldBase], game = GAME_NAME):
    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        if len(self.item_names) == 0:
            # match state.has_any
            return False_().resolve(world)
        if len(self.item_names) == 1:
            return Has(self.item_names[0]).resolve(world)
        return self.RabiRibiResolved(
            self.item_names,
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    @override
    class RabiRibiResolved(rules.HasAny.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
        @override
        def explain_rule_glitched(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            indent = get_indent(depth)
            child_indent = get_indent(depth + 1)
            messages: list[JSONMessagePart] = []
            if result == LogicState.Explain:
                messages = [
                {"type": "text", "text": indent},
                    {"type": "text", "text": "Has "},
                    {"type": "color", "color": "cyan", "text": "any"},
                    {"type": "text", "text": " of ("},
                ]
                for i, item in enumerate(self.item_names):
                    if i > 0:
                        messages.append({"type": "text", "text": ", "})
                    messages.append({"type": "item_name", "flags": 0b001, "text": item, "player": self.player})
                messages.append({"type": "text", "text": ")"})
                return messages

            assert state is not None
            assert glitched_state is not None
            found = [item for item in self.item_names if state.has(item, self.player)]
            out_of_logic = [item for item in self.item_names if glitched_state.has(item, self.player)]
            out_of_logic_only = [item for item in out_of_logic if item not in found]
            missing = [item for item in self.item_names if item not in found] \
                if result == LogicState.InLogic \
                else [item for item in self.item_names if item not in out_of_logic]
            messages = [
                {"type": "text", "text": "Has " if out_of_logic else "Missing "},
                {"type": "color", "color": "cyan", "text": "some" if out_of_logic else "all"},
                {"type": "text", "text": " of:\n"},
            ]
            if found:
                messages.append({"type": "text", "text": f"{child_indent}Found: "})
                for i, item in enumerate(found):
                    if i > 0:
                        messages.append({"type": "text", "text": ", "})
                    messages.append({"type": "color", "color": "green", "text": item})
                if missing or out_of_logic_only:
                    messages.append({"type": "text", "text": "\n"})

            if out_of_logic_only:
                messages.append({"type": "text", "text": f"{child_indent}Out of Logic: "})
                for i, item in enumerate(out_of_logic_only):
                    if i > 0:
                        messages.append({"type": "text", "text": ", "})
                    messages.append({"type": "color", "color": "yellow", "text": item})
                if missing:
                    messages.append({"type": "text", "text": "\n"})

            if missing:
                messages.append({"type": "text", "text": f"{child_indent}Missing: "})
                for i, item in enumerate(missing):
                    if i > 0:
                        messages.append({"type": "text", "text": ", "})
                    messages.append({"type": "color", "color": "salmon", "text": item})
            messages.append({"type": "text", "text": "\n"})
            return messages

class CanReachRegion(rules.CanReachRegion[RabiRibiWorldBase], game = GAME_NAME):
    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        return self.RabiRibiResolved(
            self.region_name,
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    @override
    class RabiRibiResolved(rules.CanReachRegion.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
        @override
        def get_rule_tree_message(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            if result == LogicState.OutOfLogic:
                verb = "Cannot reach"
            else:
                verb = "Reached"
            return [
                {"type": "text", "text": f"{verb} region "},
                {"type": "color", "color": get_color(result), "text": self.region_name},
            ]

class HasGroupUnique(rules.HasGroupUnique[RabiRibiWorldBase], game = GAME_NAME):
    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        item_names = tuple(sorted(world.item_name_groups[self.item_name_group]))
        return self.RabiRibiResolved(
            self.item_name_group,
            item_names,
            self.count,
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    @override
    class RabiRibiResolved(rules.HasGroupUnique.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
        @override
        def get_rule_tree_message(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            messages: list[JSONMessagePart] = [{"type": "text", "text": "Has "}]
            if result == LogicState.Explain:
                messages.append({"type": "color", "color": "cyan", "text": str(self.count)})
            else:
                assert state is not None
                assert glitched_state is not None
                if result == LogicState.OutOfLogic:
                    count = glitched_state.count_group_unique(self.item_name_group, self.player)
                else:
                    count = state.count_group_unique(self.item_name_group, self.player)
                messages.append({"type": "color", "color": get_color(result), "text": f"{count}/{self.count}"})
            messages.append({"type": "text", "text": " unique items from "})
            messages.append({"type": "color", "color": "cyan", "text": self.item_name_group})
            return messages

@dataclass()
class KnowledgeRule(rules.Rule[RabiRibiWorldBase], game = GAME_NAME):
    """Rule to check if the player has an knowledge level set or if the rule should be evaluated when out of logic."""
    value: int

    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        if world.options.knowledge >= self.value:
            return True_().resolve(world)

        if getattr(world.multiworld, "generation_is_fake", False):
            return self.Resolved(
                self.value,
                player = world.player,
                caching_enabled = getattr(world, "rule_caching_enabled", False),
            )

        return False_().resolve(world)

    class Resolved(rules.Rule.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
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
        def get_rule_tree_message(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            name = Knowledge.get_option_name(self.value)
            return [{"type": "color", "color": get_color(result), "text": name}]

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
        if world.options.trick_difficulty >= self.value:
            return True_().resolve(world)

        if getattr(world.multiworld, "generation_is_fake", False):
            return self.Resolved(
                self.value,
                player = world.player,
                caching_enabled = getattr(world, "rule_caching_enabled", False),
            )

        return False_().resolve(world)

    class Resolved(rules.Rule.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
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
        def get_rule_tree_message(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            name = Knowledge.get_option_name(self.value)
            return [{"type": "color", "color": get_color(result), "text": name}]

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
            return True_().resolve(world)

        if getattr(world.multiworld, "generation_is_fake", False):
            return self.Resolved(
                self.name,
                player = world.player,
                caching_enabled = getattr(world, "rule_caching_enabled", False),
            )

        return False_().resolve(world)

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

    class Resolved(rules.Rule.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
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
        def get_rule_tree_message(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            return [{"type": "color", "color": get_color(result), "text": self.name}]

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            messages: list[JSONMessagePart] = [
                {"type": "color", "color": "yellow", "text": self.name},
            ]
            return messages

@dataclass
class MagicTypesRule(rules.Rule[RabiRibiWorldBase], game = GAME_NAME):
    """Rule to check if the player can use enough magic types."""
    num_magic_types: int

    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        return self.Resolved(
            self.num_magic_types,
            bool(world.options.rainbow_shot_in_logic.value),
            player = world.player,
            caching_enabled = getattr(world, "rule_caching_enabled", False)
        )

    class Resolved(rules.Rule.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
        num_magic_types: int
        rainbow_shot_in_logic_enabled: bool

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            curr_magic_types = self._count_magic_types(state)
            return curr_magic_types >= self.num_magic_types

        def _count_magic_types(self, state:CollectionState) -> int:
            curr_magic_types = state.count_group_unique("Magic", self.player)
            if self._rainbow_shot_in_logic(state):
                curr_magic_types += 1
            return curr_magic_types

        def _rainbow_shot_in_logic(self, state: CollectionState) -> bool:
            """Player has Rainbow Shot and it's not out of logic by options"""
            return (
                (
                    self.rainbow_shot_in_logic_enabled
                    or state.has(ItemName.glitched_logic, self.player)
                )
                and state.has(ItemName.easter_egg, self.player, count = 5)
            )

        def _rainbow_shot_out_of_logic(self, state: CollectionState) -> bool:
            return (
                not self.rainbow_shot_in_logic_enabled
                and state.has(ItemName.glitched_logic, self.player)
                and state.has(ItemName.easter_egg, self.player, count = 5)
            )

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            deps = super().item_dependencies()
            for recruit in recruit_table:
                deps.setdefault(recruit, set()).add(id(self))
            return deps

        @override
        def get_rule_tree_message(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            messages: list[JSONMessagePart] = []
            if result == LogicState.Explain:
                messages = [
                    {"type": "text", "text": "Has "},
                    {"type": "color", "color": "cyan", "text": str(self.num_magic_types)},
                    {"type": "text", "text": " Magic Types"},
                ]
            else:
                assert state is not None
                assert glitched_state is not None
                curr_magic_types = self._count_magic_types(state)
                messages = [
                    {"type": "text", "text": "Has "},
                    {
                        "type": "color",
                        "color": get_color(result),
                        "text": f"{curr_magic_types}/{self.num_magic_types}",
                    },
                    {"type": "text", "text": " Magic Types"},
                ]
            return messages

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            messages: list[JSONMessagePart] = []
            if state is None:
                messages = [
                    {"type": "text", "text": "Has "},
                    {"type": "color", "color": "cyan", "text": str(self.num_magic_types)},
                    {"type": "text", "text": " Magic Types"},
                ]
            else:
                curr_magic_types = self._count_magic_types(state)
                color = (
                    "green" if curr_magic_types > self.num_magic_types
                    else "yellow" if curr_magic_types == self.num_magic_types and self._rainbow_shot_out_of_logic(state)
                    else "salmon"
                )
                messages = [
                    {"type": "text", "text": "Has "},
                    {
                        "type": "color",
                        "color": color,
                        "text": f"{curr_magic_types}/{self.num_magic_types}",
                    },
                    {"type": "text", "text": " Magic Types"},
                ]
            return messages


@dataclass
class TownMemberCountRule(rules.Rule[RabiRibiWorldBase], game = GAME_NAME):
    """Rule to check if the player can reach enough town members for an event."""
    num_town_members: int

    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        return self.Resolved(
            self.num_town_members,
            player = world.player,
            caching_enabled = getattr(world, "rule_caching_enabled", False)
        )

    class Resolved(rules.Rule.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
        num_town_members: int

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            return state.has_from_list_unique(recruit_table, self.player, self.num_town_members)

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            deps = super().item_dependencies()
            for recruit in recruit_table:
                deps.setdefault(recruit, set()).add(id(self))
            return deps

        @override
        def get_rule_tree_message(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            messages: list[JSONMessagePart] = []
            if result == LogicState.Explain:
                messages = [
                    {"type": "text", "text": "Has "},
                    {"type": "color", "color": "cyan", "text": str(self.num_town_members)},
                    {"type": "text", "text": " Town Members"},
                ]
            else:
                assert state is not None
                assert glitched_state is not None
                if result == LogicState.OutOfLogic:
                    curr_town_members = glitched_state.count_from_list_unique(recruit_table, self.player)
                else:
                    curr_town_members = state.count_from_list_unique(recruit_table, self.player)
                messages = [
                    {"type": "text", "text": "Has "},
                    {
                        "type": "color",
                        "color": get_color(result),
                        "text": f"{curr_town_members}/{self.num_town_members}",
                    },
                    {"type": "text", "text": " Town Members"},
                ]
            return messages

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            messages: list[JSONMessagePart] = []
            if state is None:
                messages = [
                    {"type": "text", "text": "Has "},
                    {"type": "color", "color": "cyan", "text": str(self.num_town_members)},
                    {"type": "text", "text": " Town Members"},
                ]
            else:
                curr_town_members = state.count_from_list_unique(recruit_table, self.player)
                color = "green" if curr_town_members >= self.num_town_members else "salmon"
                messages = [
                    {"type": "text", "text": "Has "},
                    {
                        "type": "color",
                        "color": color,
                        "text": f"{curr_town_members}/{self.num_town_members}",
                    },
                    {"type": "text", "text": " Town Members"},
                ]
            return messages

@dataclass
class TownMemberCountIrisuRule(rules.Rule[RabiRibiWorldBase], game = GAME_NAME):
    """Rule to check if the player can reach enough town members to fight Irisu."""
    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        return self.Resolved(
            player = world.player,
            caching_enabled = getattr(world, "rule_caching_enabled", False)
        )

    class Resolved(rules.Rule.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
        @override
        def _evaluate(self, state: CollectionState) -> bool:
            return state.has_from_list_unique(recruit_table_irisu, self.player, 15)

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            deps = super().item_dependencies()
            for recruit in recruit_table_irisu:
                deps.setdefault(recruit, set()).add(id(self))
            return deps

        @override
        def get_rule_tree_message(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            messages: list[JSONMessagePart] = []
            if result == LogicState.Explain:
                messages = [
                    {"type": "text", "text": "Has "},
                    {"type": "color", "color": "cyan", "text": "15"},
                    {"type": "text", "text": " Main Game Town Members"},
                ]
            else:
                assert state is not None
                assert glitched_state is not None
                if result == LogicState.OutOfLogic:
                    curr_town_members = glitched_state.count_from_list_unique(recruit_table, self.player)
                else:
                    curr_town_members = state.count_from_list_unique(recruit_table, self.player)
                messages = [
                    {"type": "text", "text": "Has "},
                    {
                        "type": "color",
                        "color": get_color(result),
                        "text": f"{curr_town_members}/15",
                    },
                    {"type": "text", "text": " Main Game Town Members"},
                ]
            return messages

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            messages: list[JSONMessagePart] = []
            if state is None:
                messages = [
                    {"type": "text", "text": "Has "},
                    {"type": "color", "color": "cyan", "text": "15"},
                    {"type": "text", "text": " Main Game Town Members"},
                ]
            else:
                curr_town_members = state.count_from_list_unique(recruit_table_irisu, self.player)
                color = "green" if curr_town_members >= 15 else "salmon"
                messages = [
                    {"type": "text", "text": "Has "},
                    {
                        "type": "color",
                        "color": color,
                        "text": f"{curr_town_members}/{15}",
                    },
                    {"type": "text", "text": " Main Game Town Members"},
                ]
            return messages

@dataclass()
class HasEnoughAmuletFoodRule(rules.Rule[RabiRibiWorldBase], game = GAME_NAME):
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

    class Resolved(rules.Rule.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
        num_amulet_food: int
        has_advanced_knowledge: bool
        rainbow_shot_in_logic_enabled: bool

        def _count_amulet_food(self, state):
            amulet = self._count_amulet_charges(state)
            food = 0

            if self._has_item_menu(state):
                if state.has(ItemName.rumi_donut, self.player) or state.has("Shop Reachable", self.player):
                    food = 1
                    # Eating a Rumi Donut gives an amulet charge
                    if self._can_bunny_amulet(state):
                        amulet += 1
                    food += self._count_normal_consumable_items(state)
                    # Kotri's buff can save enough amulet charge for an additional amulet use
                    if amulet >= 4 and state.has(ItemName.kotri_recruit, self.player) and \
                        state.has_from_list_unique(recruit_table, self.player, 3):
                        amulet += 1
            return (amulet + food)

        def _count_amulet_charges(self, state: CollectionState) -> int:
            """Counts the number of amulet charges the player has"""
            if state.has(ItemName.bunny_amulet, self.player) or state.has("Chapter 2", self.player):
                if state.has(ItemName.rumi_recruit, self.player):
                    return 4
                if state.has("Shop Reachable", self.player) or state.has("Chapter 4", self.player):
                    return 3
                if state.has("Chapter 3", self.player):
                    return 2
                return 1
            return 0

        def _count_normal_consumable_items(self, state: CollectionState) -> int:
            """Counts which normal consumable items the player can reach, either from locations or purchases."""
            consumables = 0
            if state.has(ItemName.rumi_cake, self.player) or state.has("Shop Reachable", self.player):
                consumables += 1
            if state.has(ItemName.cocoa_bomb, self.player) or self._can_purchase_cocoa_bomb(state):
                consumables += 1
            if state.has(ItemName.gold_carrot, self.player):
                consumables += 1
            return consumables

        def _can_purchase_cocoa_bomb(self, state: CollectionState) -> bool:
            """Player can purchase cocoa bomb"""
            return state.has("Chapter 1", self.player) and \
                state.has(ItemName.cocoa_recruit, self.player) and \
                state.has_from_list_unique(recruit_table, self.player, 3)

        def _can_bunny_amulet(self, state: CollectionState) -> bool:
            """Player can use the bunny amulet"""
            return state.has(ItemName.rumi_cake, self.player) or state.has("Shop Reachable", self.player)

        def _has_item_menu(self, state: CollectionState) -> bool:
            """Player has access to the item menu"""
            return state.has("Chapter 1", self.player) or \
                (self._is_at_least_advanced_knowledge(state) and self._has_3_magic_types(state))

        def _has_3_magic_types(self, state: CollectionState) -> bool:
            """Player has at least 3 types of magic"""
            # If playing with more than 5 Easter Eggs, Rainbow Shot could be used as a magic type
            return state.has_group_unique("Magic", self.player, 2) or \
                (self._rainbow_shot_in_logic(state) and state.has_group_unique("Magic", self.player, 1))

        def _is_at_least_advanced_knowledge(self, state: CollectionState) -> bool:
            """Knowledge is at least advanced"""
            return self.has_advanced_knowledge or state.has(ItemName.glitched_logic, self.player)

        def _rainbow_shot_in_logic(self, state: CollectionState) -> bool:
            """Player has Rainbow Shot and it's not out of logic by options"""
            return (self.rainbow_shot_in_logic_enabled or state.has(ItemName.glitched_logic, self.player)) and \
                state.has(ItemName.easter_egg, self.player, count = 5)

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            curr_amulet_food = self._count_amulet_food(state)
            return curr_amulet_food >= self.num_amulet_food

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
            deps.setdefault("Shop Reachable", set()).add(id(self))

            for consumable in item_groups["Consumables"]:
                deps.setdefault(consumable, set()).add(id(self))
            for recruit in recruit_table:
                deps.setdefault(recruit, set()).add(id(self))
            for magic in item_groups["Magic"]:
                deps.setdefault(magic, set()).add(id(self))

            return deps

        @override
        def get_rule_tree_message(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            messages: list[JSONMessagePart] = []
            if result == LogicState.Explain:
                messages = [
                    {"type": "text", "text": "Has "},
                    {"type": "color", "color": "cyan", "text": str(self.num_amulet_food)},
                    {"type": "text", "text": " Amulet/Food"},
                ]
            else:
                assert state is not None
                assert glitched_state is not None
                if result == LogicState.OutOfLogic:
                    curr_amulet_food = self._count_amulet_food(glitched_state)
                else:
                    curr_amulet_food = self._count_amulet_food(state)
                messages = [
                    {"type": "text", "text": "Has "},
                    {
                        "type": "color",
                        "color": get_color(result),
                        "text": f"{curr_amulet_food}/{self.num_amulet_food}",
                    },
                    {"type": "text", "text": " Amulet/Food"},
                ]
            return messages

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            messages: list[JSONMessagePart] = []
            if state is None:
                messages = [
                    {"type": "text", "text": "Has "},
                    {"type": "color", "color": "cyan", "text": str(self.num_amulet_food)},
                    {"type": "text", "text": " Amulet/Food"},
                ]
            else:
                curr_amulet_food = self._count_amulet_food(state)
                color = "green" if self(state) else "salmon"
                messages = [
                    {"type": "text", "text": "Has "},
                    {
                        "type": "color",
                        "color": color,
                        "text": f"{curr_amulet_food}/{self.num_amulet_food}",
                    },
                    {"type": "text", "text": " Amulet/Food"},
                ]
            return messages

        @override
        def explain_str(self, state: CollectionState | None = None) -> str:
            suffix = ""
            if state is not None:
                suffix = " ✓" if self(state) else " ✕"
            return f"Has {self.num_amulet_food} Amulet/Food{suffix}"

        @override
        def __str__(self) -> str:
            return f"Has {self.num_amulet_food} Amulet/Food"

def from_option(option: type[Option], value: Any, operator: Operator = "eq") -> rules.Rule[RabiRibiWorldBase]:
    return True_(options=[rules.OptionFilter(option, value, operator)])

@dataclass()
class Macro(rules.WrapperRule[RabiRibiWorldBase], game=GAME_NAME):
    name: str
    description: str = ""

    @override
    def _instantiate(self, world: RabiRibiWorldBase) -> rules.Rule.Resolved:
        if rule := world.rule_macros.get(self.name):
            return rule
        rule = self.Resolved(
            self.child.resolve(world),
            self.name,
            self.description,
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )
        world.rule_macros[self.name] = rule
        return rule

    @override
    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.child}]"

    class Resolved(rules.WrapperRule.Resolved, GlitchedLogicMixIn, metaclass=CustomRuleRegisterProtocolMeta):
        name: str
        description: str = ""

        @override
        def get_rule_tree_message(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, glitched_state)
            return [{"type": "color", "color": get_color(result), "text": str(self)}]

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            result = evaluate_rule(self, state, None)
            return [{"type": "color", "color": get_color(result), "text": str(self)}]

        @override
        def explain_str(self, state: CollectionState | None = None) -> str:
            result = evaluate_rule(self, state, None)
            suffix = " ✕" if result == LogicState.CannotReach else " ✓"
            return f"{self.name}{suffix}"

        @override
        def __str__(self) -> str:
            return self.name