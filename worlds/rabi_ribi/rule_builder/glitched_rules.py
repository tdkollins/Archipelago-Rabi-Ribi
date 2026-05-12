from abc import abstractmethod
from enum import Enum
from typing import Protocol, runtime_checkable

from BaseClasses import CollectionRule, CollectionState
from NetUtils import JSONMessagePart
from rule_builder import rules


class LogicState(Enum):
    CannotReach = 0
    InLogic = 1
    OutOfLogic = 2
    Explain = 3


def get_indentation(depth: int):
    hyphen = "- "
    spaces = depth * 4
    return "" if depth == 0 else f"{hyphen:>{spaces}}"


def evaluate_rule(rule: rules.Rule.Resolved, state: CollectionState | None, glitched_state: CollectionState | None) -> LogicState:
    if state is None:
        return LogicState.Explain
    if rule(state):
        return LogicState.InLogic
    if glitched_state is not None and rule(glitched_state):
        return LogicState.OutOfLogic
    return LogicState.CannotReach


def get_logic_color(result: LogicState) -> str:
    if result == LogicState.Explain:
        return "cyan"
    if result == LogicState.InLogic:
        return "green"
    if result == LogicState.OutOfLogic:
        return "yellow"
    return "salmon"


def get_out_of_logic_suffix(result: LogicState) -> list[JSONMessagePart]:
    suffix = " (Out of Logic)" if result == LogicState.OutOfLogic else ""
    return [{"type": "text", "text": suffix}]


@runtime_checkable
class GlitchedLogicExplainer(Protocol):
    @abstractmethod
    def explain_rule_glitched(self, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
        pass


def rule_to_json(
    rule: CollectionRule | rules.Rule.Resolved | None,
    state: CollectionState,
    glitched_state: CollectionState,
    depth: int = 0,
) -> list[JSONMessagePart]:
    messages: list[JSONMessagePart] = []
    if isinstance(rule, GlitchedLogicExplainer):
        messages.extend(rule.explain_rule_glitched(
            state, glitched_state, depth))
    elif isinstance(rule, rules.And.Resolved):
        messages.extend(explain_rule_and(
            rule, state, glitched_state, depth))
    elif isinstance(rule, rules.Or.Resolved):
        messages.extend(explain_rule_or(
            rule, state, glitched_state, depth))
    elif isinstance(rule, rules.Has.Resolved):
        messages.extend(explain_rule_has(
            rule, state, glitched_state, depth))
    elif isinstance(rule, rules.HasAll.Resolved):
        messages.extend(explain_rule_has_all(
            rule, state, glitched_state, depth))
    elif isinstance(rule, rules.HasAny.Resolved):
        messages.extend(explain_rule_has_any(
            rule, state, glitched_state, depth))
    elif isinstance(rule, rules.CanReachRegion.Resolved):
        messages.extend(explain_rule_can_reach_region(
            rule, state, glitched_state, depth))
    elif isinstance(rule, rules.HasGroupUnique.Resolved):
        messages.extend(explain_rule_has_group_unique(
            rule, state, glitched_state, depth))
    return messages


def explain_rule_and(rule: rules.And.Resolved, state: CollectionState, glitched_state: CollectionState, depth: int) -> list[JSONMessagePart]:
    result = evaluate_rule(rule, state, glitched_state)
    indent = get_indentation(depth)
    suffix = get_out_of_logic_suffix(result)
    messages: list[JSONMessagePart] = [
        {"type": "text", "text": indent},
        {"type": "text", "text": "Missing" if result ==
            LogicState.CannotReach else "Has"},
        *suffix,
        {"type": "color", "color": "cyan", "text": " some" if result ==
            LogicState.CannotReach else " all"},
        {"type": "text", "text": " of:\n"},
    ]
    for idx, child in enumerate(rule.children):
        messages.extend(rule_to_json(child, state, glitched_state, depth + 1))
        if idx < (len(rule.children) - 1):
            messages.append({"type": "text", "text": "\n"})
    return messages


def explain_rule_or(rule: rules.Or.Resolved, state: CollectionState, glitched_state: CollectionState, depth: int) -> list[JSONMessagePart]:
    result = evaluate_rule(rule, state, glitched_state)
    indent = get_indentation(depth)
    suffix = get_out_of_logic_suffix(result)
    messages: list[JSONMessagePart] = [
        {"type": "text", "text": indent},
        {"type": "text", "text": "Missing" if result ==
            LogicState.CannotReach else "Has"},
        *suffix,
        {"type": "color", "color": "cyan", "text": " all" if result ==
            LogicState.CannotReach else " some"},
        {"type": "text", "text": " of:\n"},
    ]
    for idx, child in enumerate(rule.children):
        messages.extend(rule_to_json(child, state, glitched_state, depth + 1))
        if idx < (len(rule.children) - 1):
            messages.append({"type": "text", "text": "\n"})
    return messages


def explain_rule_has(rule: rules.Has.Resolved, state: CollectionState, glitched_state: CollectionState, depth: int) -> list[JSONMessagePart]:
    result = evaluate_rule(rule, state, glitched_state)
    indent = get_indentation(depth)
    verb = "Missing" if result == LogicState.CannotReach else "Has"
    messages: list[JSONMessagePart] = [
        {"type": "text", "text": f"{indent}{verb} "},
    ]
    if rule.count > 1:
        messages.append(
            {"type": "color", "color": "cyan", "text": str(rule.count)})
        messages.append({"type": "text", "text": "x "})
    if state:
        color = get_logic_color(result)
        messages.append(
            {"type": "color", "color": color, "text": rule.item_name})
    else:
        messages.append({"type": "item_name", "flags": 0b001,
                        "text": rule.item_name, "player": rule.player})
    messages.extend(get_out_of_logic_suffix(result))
    return messages


def explain_rule_has_all(rule: rules.HasAll.Resolved, state: CollectionState, glitched_state: CollectionState, depth: int) -> list[JSONMessagePart]:
    result = evaluate_rule(rule, state, glitched_state)
    indent = get_indentation(depth)
    child_indent = get_indentation(depth + 1)
    messages: list[JSONMessagePart] = []
    if result == LogicState.Explain:
        messages = [
            {"type": "text", "text": indent},
            {"type": "text", "text": "Has "},
            {"type": "color", "color": "cyan", "text": "all"},
            {"type": "text", "text": " of ("},
        ]
        for i, item in enumerate(rule.item_names):
            if i > 0:
                messages.append({"type": "text", "text": ", "})
            messages.append({"type": "item_name", "flags": 0b001,
                            "text": item, "player": rule.player})
        messages.append({"type": "text", "text": ")"})
        return messages

    assert state is not None
    assert glitched_state is not None
    found = [item for item in rule.item_names if state.has(item, rule.player)]
    out_of_logic = [
        item for item in rule.item_names if glitched_state.has(item, rule.player)]
    out_of_logic_only = [item for item in out_of_logic if item not in found]
    missing = [item for item in rule.item_names if item not in found] \
        if result == LogicState.InLogic \
        else [item for item in rule.item_names if item not in out_of_logic]

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
        messages.append(
            {"type": "text", "text": f"{child_indent}Out of Logic: "})
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
    return messages


def explain_rule_has_any(rule: rules.HasAny.Resolved, state: CollectionState | None, glitched_state: CollectionState | None, depth: int) -> list[JSONMessagePart]:
    result = evaluate_rule(rule, state, glitched_state)
    indent = get_indentation(depth)
    child_indent = get_indentation(depth + 1)
    messages: list[JSONMessagePart] = []
    if result == LogicState.Explain:
        messages = [
            {"type": "text", "text": indent},
            {"type": "text", "text": "Has "},
            {"type": "color", "color": "cyan", "text": "any"},
            {"type": "text", "text": " of ("},
        ]
        for i, item in enumerate(rule.item_names):
            if i > 0:
                messages.append({"type": "text", "text": ", "})
            messages.append({"type": "item_name", "flags": 0b001,
                            "text": item, "player": rule.player})
        messages.append({"type": "text", "text": ")"})
        return messages

    assert state is not None
    assert glitched_state is not None
    found = [item for item in rule.item_names if state.has(item, rule.player)]
    out_of_logic = [
        item for item in rule.item_names if glitched_state.has(item, rule.player)]
    out_of_logic_only = [item for item in out_of_logic if item not in found]
    missing = [item for item in rule.item_names if item not in found] \
        if result == LogicState.InLogic \
        else [item for item in rule.item_names if item not in out_of_logic]
    messages = [
        {"type": "text", "text": indent},
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
        messages.append(
            {"type": "text", "text": f"{child_indent}Out of Logic: "})
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
    return messages


def explain_rule_can_reach_region(rule: rules.CanReachRegion.Resolved, state: CollectionState, glitched_state: CollectionState, depth: int) -> list[JSONMessagePart]:
    result = evaluate_rule(rule, state, glitched_state)
    indent = get_indentation(depth)
    verb = "Cannot reach" if result == LogicState.CannotReach else "Reached"
    return [
        {"type": "text", "text": indent},
        {"type": "text", "text": f"{verb} region "},
        {"type": "color", "color": get_logic_color(
            result), "text": rule.region_name},
        *get_out_of_logic_suffix(result)
    ]


def explain_rule_has_group_unique(rule: rules.HasGroupUnique.Resolved, state: CollectionState, glitched_state: CollectionState, depth: int) -> list[JSONMessagePart]:
    result = evaluate_rule(rule, state, glitched_state)
    indent = get_indentation(depth)
    body: list[JSONMessagePart] = [{"type": "text", "text": "Has "}]
    if result == LogicState.Explain:
        body.append({"type": "color", "color": "cyan",
                    "text": str(rule.count)})
    else:
        assert state is not None
        assert glitched_state is not None
        if result == LogicState.OutOfLogic:
            count = glitched_state.count_group_unique(
                rule.item_name_group, rule.player)
        else:
            count = state.count_group_unique(rule.item_name_group, rule.player)
        body.append({"type": "color", "color": get_logic_color(
            result), "text": f"{count}/{rule.count}"})
    body.append({"type": "text", "text": " unique items from "})
    body.append({"type": "color", "color": "cyan",
                "text": rule.item_name_group})
    return [
        {"type": "text", "text": indent},
        *body,
        *get_out_of_logic_suffix(result)
    ]
