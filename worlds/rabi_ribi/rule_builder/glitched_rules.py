from enum import Enum

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart
from rule_builder import rules


from typing import Protocol, runtime_checkable


class LogicState(Enum):
    CannotReach = 0
    InLogic = 1
    OutOfLogic = 2
    Explain = 3


def get_suffix(result: LogicState) -> list[JSONMessagePart]:
    suffix =  " (Out of Logic)" if result == LogicState.OutOfLogic else ""
    return [{"type": "text", "text": suffix}]


def get_indent(depth: int):
    hyphen = "- "
    spaces = depth * 4
    return "" if depth == 0 else f"{hyphen:>{spaces}}"


def get_prefix(result: LogicState, depth: int) -> list[JSONMessagePart]:
    indent = get_indent(depth)
    text = "Can " if result != LogicState.CannotReach else "Cannot "
    return [{"type": "text", "text": f"{indent}{text}"}]


def evaluate_rule(rule: rules.Rule.Resolved, state: CollectionState | None, glitched_state: CollectionState | None) -> LogicState:
    if state is None:
        return LogicState.Explain
    if rule(state): # type: ignore
        return LogicState.InLogic
    if glitched_state is not None and rule(glitched_state): # type: ignore
        return LogicState.OutOfLogic
    return LogicState.CannotReach


@runtime_checkable
class GlitchedLogicExplainer(Protocol):
    def explain_rule_glitched(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
        assert isinstance(self, rules.Rule.Resolved)
        if self.always_true:
            return []
        result = evaluate_rule(self, state, glitched_state)
        return [
            *get_prefix(result, depth),
            *get_suffix(result)
        ]


def get_logic_color(result: LogicState) -> str:
    if result == LogicState.Explain:
        return "cyan"
    if result == LogicState.InLogic:
        return "green"
    if result == LogicState.OutOfLogic:
        return "yellow"
    return "salmon"