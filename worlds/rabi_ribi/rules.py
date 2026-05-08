from dataclasses import dataclass, field
import json
import pkgutil
import re
from rule_builder.rules import Rule
from typing import Any
from . import custom_rules as rules
from .bases import RabiRibiWorldBase
from .custom_rules import Macro, TownMemberCountRule, TownMemberCountIrisuRule
from .data import ConstraintChange, data
from .macros import rules_by_logic_key
from .names import ItemName, LocationName


@dataclass
class RegionConnection:
    edge: str
    prereq: str


@dataclass
class LocationConnection:
    item: str
    from_location: str
    entry_prereq: str
    exit_prereq: str
    alternate_entries: dict[str, str] = field(default_factory=dict)
    alternate_exits: dict[str, str] = field(default_factory=dict)


@dataclass
class TemplateConstraint:
    name: str
    weight: int
    changes: list[dict[Any, Any]] = field(default_factory=list)


def _read_file_and_convert_to_json(filename: str) -> list[Any]:
    def strip_comments(line):
        if '//' not in line: return line
        return line[:line.find('//')]

    file_bytes  = pkgutil.get_data(__name__, f"existing_randomizer/{filename}")
    assert(isinstance(file_bytes, bytes))

    # Convert the file to proper JSON by:
    # 1. Removing comments
    # 2. Adding commas to separate entries
    # 3. Surrounding with braces to make the data a list
    # Note: This is just copying what the existing randomizer was doing
    file_str = file_bytes.decode()
    lines = file_str.splitlines()
    lines = [strip_comments(line).strip() for line in lines]
    jsondata = ' '.join(lines)
    jsondata = re.sub(r',\s*}', '}', jsondata)
    jsondata = '},{'.join(re.split(r'}\s*{', jsondata))
    jsondata = '[' + jsondata + ']'
    return json.loads(jsondata)

_logic_re: re.Pattern[str] = re.compile('([()&|])')
def _parse_expression_logic(line: str, current_expression: Rule[RabiRibiWorldBase] = rules.True_()):
    line = line.replace('&&', '&').replace('||', '|')
    matches = (s.strip() for s in _logic_re.split(line))
    tokens: list[str | Macro | Rule[RabiRibiWorldBase]] = [s for s in matches if isinstance(s, str) and len(s) > 0]
    # Stack-based parsing. pop from [tokens], push into [stack]
    # We push an expression into [tokens] if we want to process it next iteration.
    tokens.reverse()
    stack = []
    while len(tokens) > 0:
        next = tokens.pop()
        if isinstance(next, Rule):
            if len(stack) == 0:
                stack.append(next)
                continue
            head = stack[-1]
            if head == '&':
                stack.pop()
                exp = stack.pop()
                assert isinstance(exp, Rule)
                tokens.append(exp & next)
            elif head == '|':
                stack.pop()
                exp = stack.pop()
                assert isinstance(exp, Rule)
                tokens.append(exp | next)
            else:
                stack.append(next)
        elif isinstance(next, str) and next in '(&|':
            stack.append(next)
        elif next == ')':
            exp = stack.pop()
            isinstance(exp, Rule)
            top = stack.pop()
            assert top == '('
            tokens.append(exp)
        else:
            # Literal parsing
            assert isinstance(next, str)
            if next.startswith('BACKTRACK_'):
                # Ignore backtracking in AP, as it does not add new regions
                # only paths to already visited ones
                tokens.append(rules.False_())
            elif next == 'current':
                assert isinstance(current_expression, Rule)
                tokens.append(current_expression)
            elif next in rules_by_logic_key:
                tokens.append(rules_by_logic_key[next])
            else:
                if next.startswith('r'): next = next[1:]
                if data.is_item_key(next):
                    tokens.append(rules.Has(data.get_item_ap_name(next)))
                elif data.is_region_key(next):
                    tokens.append(rules.CanReachRegion(data.get_region_ap_name(next)))
                else:
                    raise NotImplementedError('Unknown variable %s in expression: %s' % (next, line))
    assert len(stack) == 1
    return stack[0]

def _parse_region_connection(connection: RegionConnection):
    from_key, to_key = (x.strip() for x in connection.edge.split('->'))
    from_region = data.get_region_by_logic_key(from_key)
    from_region.connections[data.get_region_ap_name(to_key)] = _parse_expression_logic(connection.prereq)

def _parse_location_connection(connection: LocationConnection):
    location = data.get_location_by_logic_key(connection.item)
    if location.has_region:
        from_region = data.get_region_by_logic_key(connection.from_location)
        to_region = data.get_region_by_ap_name(location.name)

        from_region.connections[to_region.name] = _parse_expression_logic(connection.entry_prereq)
        to_region.connections[from_region.name] = _parse_expression_logic(connection.exit_prereq)

        if len(connection.alternate_entries) > 0:
            for entry, prereq in connection.alternate_entries.items():
                entry_region = data.get_region_by_logic_key(entry)
                entry_region.connections[to_region.name] = _parse_expression_logic(prereq)

        if len(connection.alternate_exits) > 0:
            for exit, prereq in connection.alternate_exits.items():
                exit_region = data.get_region_by_logic_key(exit)
                to_region.connections[exit_region.name] = _parse_expression_logic(prereq)


def _parse_template_constraint(constraint: TemplateConstraint):
    data_constraint = data.get_constraint_by_logic_key(constraint.name)
    changes = [RegionConnection(**change) for change in constraint.changes]
    for change in changes:
        from_key, to_key = (x.strip() for x in change.edge.split('->'))
        from_region = data.get_region_by_logic_key(from_key)
        to_region = data.get_region_by_logic_key(to_key)
        current_rule = from_region.connections[to_region.name]
        rule = _parse_expression_logic(change.prereq, current_rule)
        data_constraint.changes.append(ConstraintChange(from_region.name, to_region.name, rule))


def parse_connections():
    region_connections: list[RegionConnection] = [
        RegionConnection(**item)
        for item in
        _read_file_and_convert_to_json("constraints_graph.txt")
    ]

    for connection in region_connections:
        _parse_region_connection(connection)

    location_connections: list[LocationConnection] = [
        LocationConnection(**item)
        for item in
        _read_file_and_convert_to_json("constraints.txt")
    ]

    for connection in location_connections:
        _parse_location_connection(connection)

    template_constraints: list[TemplateConstraint] = [
        TemplateConstraint(**item)
        for item in
        _read_file_and_convert_to_json("maptemplates/template_constraints.txt")
    ]

    for constraint in template_constraints:
        _parse_template_constraint(constraint)

    start_rando_template_constraints: list[TemplateConstraint] = [
        TemplateConstraint(**item)
        for item in
        _read_file_and_convert_to_json("maptemplates/start_rando_template_constraints.txt")
    ]

    for constraint in start_rando_template_constraints:
        _parse_template_constraint(constraint)


can_recruit_cocoa = \
    rules.HasAll(ItemName.cocoa_1, ItemName.kotri_1) & \
    rules.CanReachRegion(data.get_region_ap_name(LocationName.cave_cocoa))

can_recruit_ashuri = \
    rules.HasAll("Chapter 1", ItemName.ashuri_2)

can_recruit_saya = \
    rules.CanReachRegion(data.get_region_ap_name(LocationName.evernight_saya))

can_recruit_nieve_and_nixie = \
    rules.CanReachRegion(data.get_region_ap_name(LocationName.palace_level_5)) & \
    rules.CanReachRegion(data.get_region_ap_name(LocationName.icy_summit_nixie))

can_recruit_seana = rules.HasAll(
    ItemName.seana_1,
    ItemName.vanilla_recruit,
    ItemName.chocolate_recruit,
    ItemName.cicini_recruit,
    ItemName.syaro_recruit,
    ItemName.nieve_recruit,
    ItemName.nixie_recruit)

can_recruit_lilith = rules.Has(ItemName.cicini_recruit)

can_recruit_chocolate = rules.Has("Chapter 1")

can_recruit_kotri = rules.Has(ItemName.kotri_2)

can_recruit_keke_bunny = rules.CanReachRegion(data.get_region_ap_name(LocationName.town_main))

can_recruit_irisu = \
    rules.CanReachRegion(data.get_region_ap_name(LocationName.warp_destination_hospital)) & \
    rules.HasAll("Chapter 5", ItemName.miriam_recruit, ItemName.rumi_recruit) & \
    TownMemberCountIrisuRule()

can_reach_chapter_1 = Macro(
    rules.CanReachRegion(data.get_region_ap_name(LocationName.town_main)),
    "Chapter 1",
    "Player can reach Chapter 1"
)

can_reach_chapter_2 = Macro(
    (
        rules.CanReachRegion(data.get_region_ap_name(LocationName.town_main))
        & TownMemberCountRule(2)
    ),
    "Chapter 2",
    "Player can reach Chapter 2"
)

can_reach_chapter_3 = Macro(
    (
        rules.CanReachRegion(data.get_region_ap_name(LocationName.town_main))
        & TownMemberCountRule(4)
    ),
    "Chapter 3",
    "Player can reach Chapter 3"
)

can_reach_chapter_4 = Macro(
    (
        rules.CanReachRegion(data.get_region_ap_name(LocationName.town_main))
        & TownMemberCountRule(7)
    ),
    "Chapter 4",
    "Player can reach Chapter 4"
)

can_reach_chapter_5 = Macro(
    (
        rules.CanReachRegion(data.get_region_ap_name(LocationName.town_main))
        & TownMemberCountRule(10)
    ),
    "Chapter 5",
    "Player can reach Chapter 5"
)

can_reach_chapter_6 = Macro(
    can_reach_chapter_5,
    "Chapter 6",
    "Player can reach Chapter 6"
)

can_reach_chapter_7 = Macro(
    rules.Has(ItemName.rumi_recruit),
    "Chapter 7",
    "Player can reach Chapter 7"
)