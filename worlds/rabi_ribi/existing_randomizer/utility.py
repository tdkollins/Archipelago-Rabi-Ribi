import hashlib
import json
import sys
import random
import re
import ast
import os
from collections import defaultdict
from typing import Callable, Dict, List, Set

from ..utility import load_text_file

### Enums
LOCATION_WARP = 0
LOCATION_MAJOR = 1
LOCATION_MINOR = 2

"""
Variable types:
1. Locations
    - Warp locations - locations with a warp stone
    - Major locations - must have unconstrained path to warp stone
    - Minor locations - cannot have autosave or save points within
2. Items (Item Locations)
3. Additional Items (Items without locations)
4. Pseudo Items
"""

# Structs

class Item(object):
    def __init__(self, position, areaid, itemid, name=None):
        self.areaid = areaid
        self.position = position
        self.itemid = itemid
        self.name = name

    # XXXX: Delete if unneeded
    def copy(self):
        item = Item(self.position, self.areaid, self.itemid)
        item.name = self.name
        return item

    # XXXX: Delete if unneeded
    def set_location(self, item):
        self.areaid = item.areaid
        self.position = item.position

    # XXXX: Delete if unneeded
    def __str__(self):
        x, y = self.position
        return '(%d,%d) : %d : %d : %s' % (x, y, self.areaid, self.itemid, self.name)

class MapTransition(object):
    def __init__(self, origin_location, area_current, entry_current, area_target,
            entry_target, walking_right, rect):
        self.origin_location = origin_location
        self.area_current = area_current
        self.entry_current = entry_current
        self.area_target = area_target
        self.entry_target = entry_target
        self.walking_right = walking_right
        self.rect = ast.literal_eval(rect)
        rect_x, rect_y, rect_width, rect_height = self.rect
        self.rect_x = rect_x
        self.rect_y = rect_y
        self.rect_width = rect_width
        self.rect_height = rect_height

class StartLocation(object):
    def __init__(self, area, position, weight, location):
        self.area = area
        self.position = ast.literal_eval(position)
        self.weight = weight
        self.location = location

_constraint_re = re.compile(r'[\(\)]|\bAND\b|\bOR\b|\bBACKTRACK_\d+\b') 
_impossible = {'IMPOSSIBLE'}
_always_check = {'DEFAULT'}
def get_prereq_literals(prereq):
    literals_str = _constraint_re.sub('', str( prereq ) )
    literals_set = set(literals_str.split())
    if('FALSE' in literals_set):
        return _impossible
    literals_set.discard('TRUE')
    if(len(literals_set) < 1):
        return _always_check
    return literals_set

# AP Change: Moved generate_progression_dict to after declaration of class GraphEdge

class EdgeConstraintData(object):
    def __init__(self, from_location, to_location, prereq_expression):
        self.from_location = from_location
        self.to_location = to_location
        self.prereq_expression = prereq_expression
        self.prereq_lambda = ExpressionLambda(prereq_expression).expression_lambda
        self.prereq_literals = get_prereq_literals( prereq_expression )

    def __str__(self):
        return '\n'.join([
            'From: %s' % self.from_location,
            'To: %s' % self.to_location,
            'Prereq: %s' % self.prereq_expression,
        ])

class ItemConstraintData(object):
    def __init__(self, item, from_location, entry_prereq, exit_prereq, alternate_entries, alternate_exits):
        self.item = item
        self.from_location = from_location
        # AP Change: Store the ExpressionLambda instead of the lambda function, so we can read the original logic
        self.entry_prereq = ExpressionLambda(entry_prereq)
        self.exit_prereq  = ExpressionLambda(exit_prereq)
        self.entry_progression = get_prereq_literals( entry_prereq )
        self.exit_progression  = get_prereq_literals(  exit_prereq )
        self.alternate_entries = alternate_entries
        self.alternate_exits = alternate_exits
        self.no_alternate_paths = (len(self.alternate_entries) + len(self.alternate_exits) == 0)

class TemplateConstraintData(object):
    def __init__(self, name, weight, template_file, changes):
        self.name = name
        self.weight = weight
        self.template_file = template_file
        self.changes = changes
        self.conflicts_names = []
        self.change_edge_set = set([(c.from_location, c.to_location) for c in changes]
                                + [(c.to_location, c.from_location) for c in changes])

    def conflicts_with(self, other):
        if other == self: return True
        return bool(self.change_edge_set.intersection(other.change_edge_set))

class GraphEdge(object):
    def __init__(self, edge_id, from_location, to_location, constraint, constraint_expr, backtrack_cost, progression={'DEFAULT'}):
        self.edge_id = edge_id
        self.from_location = from_location
        self.to_location = to_location
        self.satisfied = constraint
        # AP Change: Store the expression so we can read the original logic in AP
        self.satisfied_expr = constraint_expr
        self.progression = progression
        self.backtrack_cost = backtrack_cost

    def __str__(self):
        return '\n'.join([
            'From: %s' % self.from_location,
            'To: %s' % self.to_location,
            'ID: %s' % self.edge_id,
            'Cost: %s' % self.backtrack_cost,
        ])
    
class ExpressionLambda(object):
    def __init__(self, expression):
        self.expression = expression
        self.expression_compile = compile(expression.compile(), "<node>", mode= "eval")
        self.expression_lambda = lambda v : eval(self.expression_compile, None, {"variables": v})

class ExpressionData(object):
    def __init__(self, exp):
        self.exp = exp
        compiled = compile(exp.compile(), "<node>", mode= "eval")
        self.exp_lambda = lambda v : eval(compiled, None, {"variables": v})
        self.exp_literals = get_prereq_literals( exp )

class ConfigData(object):
    def __init__(self, knowledge, difficulty, settings):
        self.knowledge = knowledge
        self.difficulty = difficulty
        self.settings = settings

# AP Change: Moved method to after creation of class GraphEdge for typing
def generate_progression_dict(variables_list, edges:List[GraphEdge], keep_progression = True) -> Dict[str, Set[int]]:
    progression = defaultdict(set)
    for v in variables_list: 
        progression[v] = set()
    for edge in edges:
        for literal in edge.progression:
            progression[literal].add(edge.edge_id)
        if not keep_progression:
            del edge.progression #no longer needed, saves space
    return progression

# misc utility functions

def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z

def deterministic_set_zip(s1, s2):
    sorted1 = sorted(s1)
    sorted2 = sorted(s2)
    random.shuffle(sorted1)
    return zip(sorted1, sorted2)

def mean(values):
    values = tuple(values)
    return float(sum(values))/len(values)

_potion_re = re.compile('^[A-Z]*_UP_')
def is_potion(item_name):
    """
    AP Change: Include items ending in UP as potions.
    """
    return bool(_potion_re.match(item_name)) or item_name.endswith('_UP')

def is_egg(item_name):
    """
    AP Change: Include items named EASTER_EGG as eggs.
    """
    return item_name is not None and (item_name.startswith('EGG_') or item_name == 'EASTER_EGG')


# Index Conversions

def to_position(index):
    y = index%200
    x = index//200
    return x,y

def to_index(position):
    x, y = position
    return x*200 + y

def xy_to_index(x, y):
    return x*200 + y
    
def to_tile_index(x, y):
    return x*18 + y


# Expression Parsing

def parse_expression_lambda(line, variable_names_set, default_expressions, current_expression=None):
    expression = parse_expression(line, variable_names_set, default_expressions, current_expression)
    evaluate = ExpressionLambda(expression)
    return evaluate.expression_lambda

# & - and
# | - or
# !/~ - not
# ( ) - parentheses
# throws errors if parsing fails
def parse_expression(line, variable_names_set, default_expressions={}, current_expression=None):
    try:
        # the str(line) cast is used because sometimes <line> is a u'unicode string' on unix machines.
        return parse_expression_logic(str(line), variable_names_set, default_expressions, current_expression)
    except Exception as e:
        print_err('Error parsing expression:')
        print_err(line)
        raise e

# Used in string parsing. We only have either strings or expressions
isExpr = lambda s : not type(s) is str
_logic_re = re.compile('([()&|!~])')
def parse_expression_logic(line, variable_names_set, default_expressions, current_expression):
    line = line.replace('&&', '&').replace('||', '|')
    tokens = (s.strip() for s in _logic_re.split(line))
    tokens = [s for s in tokens if s]
    # Stack-based parsing. pop from [tokens], push into [stack]
    # We push an expression into [tokens] if we want to process it next iteration.
    tokens.reverse()
    stack = []
    while len(tokens) > 0:
        next = tokens.pop()
        if isExpr(next):
            if len(stack) == 0:
                stack.append(next)
                continue
            head = stack[-1]
            if head == '&':
                stack.pop()
                exp = stack.pop()
                assert isExpr(exp)
                tokens.append(OpAnd(exp, next))
            elif head == '|':
                stack.pop()
                exp = stack.pop()
                assert isExpr(exp)
                tokens.append(OpOr(exp, next))
            elif head in '!~':
                stack.pop()
                tokens.append(OpNot(next))
            else:
                stack.append(next)
        elif next in '(&|!~':
            stack.append(next)
        elif next == ')':
            exp = stack.pop()
            assert isExpr(exp)
            top = stack.pop()
            assert top == '('
            tokens.append(exp)
        else: # string literal
            # Literal parsing
            if next.startswith('BACKTRACK_'):
                nSteps = int(next[next.rfind('_')+1:])
                tokens.append(OpBacktrack(nSteps))
            elif next == 'current':
                tokens.append(current_expression)
            elif next in default_expressions:
                tokens.append(default_expressions[next])
            else:
                if next.startswith('r'): next = next[1:]
                if next not in variable_names_set:
                    fail('Unknown variable %s in expression: %s' % (next, line))
                else:
                    tokens.append(OpLit(next))
    assert len(stack) == 1
    return stack[0]


class OpLit(object):
    def __init__(self, name):
        self.name = name
    def compile(self):
        return "variables['%s']" % self.name
    def evaluate(self, variables):
        return variables[self.name]
    def __str__(self):
        return self.name
    __repr__ = __str__

class OpNot(object):
    def __init__(self, expr):
        self.expr = expr
    def compile(self):
        return "(not %s)" % self.expr.compile()
    def evaluate(self, variables):
        return not self.expr.evaluate(variables)
    def __str__(self):
        return '(NOT %s)' % self.expr
    __repr__ = __str__

class OpOr(object):
    def __init__(self, exprL, exprR):
        self.exprL = exprL
        self.exprR = exprR
    def compile(self):
        return "(%s or %s)" % (self.exprL.compile(), self.exprR.compile())
    def evaluate(self, variables):
        return self.exprL.evaluate(variables) or self.exprR.evaluate(variables)
    def __str__(self):
        return '(%s OR %s)' % (self.exprL, self.exprR)
    __repr__ = __str__

class OpAnd(object):
    def __init__(self, exprL, exprR):
        self.exprL = exprL
        self.exprR = exprR
    def compile(self):
        return "(%s and %s)" % (self.exprL.compile(), self.exprR.compile())
    def evaluate(self, variables):
        return self.exprL.evaluate(variables) and self.exprR.evaluate(variables)
    def __str__(self):
        return '(%s AND %s)' % (self.exprL, self.exprR)
    __repr__ = __str__

def backtrackEvaluate(variables, nSteps):
    # Yes, we're cheating by putting backtrack data in variables lol.
    if not variables['IS_BACKTRACKING']: return False
    untraversable_edges, outgoing_edges, edges = variables['BACKTRACK_DATA']
    current_node, target_node = variables['BACKTRACK_GOALS']
    reachable = set((current_node,))
    frontier = set(((current_node,0),))
    frontier_next = set()

    while len(frontier) > 0:
        for node, distance in frontier:
            for edge_id in outgoing_edges[node]:
                if edge_id in untraversable_edges: continue
                target_location = edges[edge_id].to_location
                new_cost = distance + edges[edge_id].backtrack_cost
                if new_cost > nSteps: continue
                if target_location == target_node: return True
                if target_location in reachable: continue
                frontier_next.add((target_location, new_cost))
                reachable.add(target_location)
        frontier.clear()
        frontier, frontier_next = frontier_next, frontier
    return False
    
class OpBacktrack(object):
    def __init__(self, nSteps):
        self.nSteps = nSteps
    def evaluate(self, variables):
        return backtrackEvaluate(variables, self.nSteps)
    def __str__(self):
        return 'BACKTRACK_%d' % self.nSteps
    def compile(self):
        return "backtrackEvaluate(variables, %d)" % self.nSteps
    __repr__ = __str__


# Error Handling

def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, flush=True, **kwargs)

def fail(message):
    print_err(message)
    sys.exit(1)

def print_ln(*args, **kwargs):
    print(*args, flush=True, **kwargs)


# File Parsing

def print_error(error, jsondata):
    import re
    pos = int(re.findall('char ([\\d]*)', error.__str__())[0])
    VIEW_RANGE = 100
    start = max(pos-VIEW_RANGE, 0)
    end = min(pos+VIEW_RANGE, len(jsondata))
    print_err('File parsing error')
    print_err(error)
    print_err('Error location:')
    print_err(jsondata[start:pos])
    print_err(jsondata[pos:end])

def parse_json(jsondata):
    try:
        return json.loads(jsondata)
    except ValueError as e:
        print_error(e, jsondata)
        raise e

def read_file_and_strip_comments(filename):
    def strip_comments(line):
        if '//' not in line: return line
        return line[:line.find('//')]
    # AP Change: Use pkgutil to read data from .apworld
    f = load_text_file(filename)
    lines = f.splitlines()
    lines = [strip_comments(line).strip() for line in lines]
    return lines



# Misc commands

def string_to_integer_seed(args):
    seed = None
    try:
        seed = int(args.seed, base=16)
    except ValueError:
        s = '%s_hd:%s' % (args.seed, args.hide_difficulty)
        seed = int(hashlib.md5(s.encode('utf-8')).hexdigest(), base=16)
    return seed

def hash_map_files(areaids, maps_dir):
    hash  = hashlib.md5()

    for areaid in sorted(areaids):
        hash.update(str(areaid).encode('utf-8'))
        filename = '%s/area%d.map' % (maps_dir, areaid) 
        if not os.path.isfile(filename):
            fail('file %s does not exist!' % filename)
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash.update(chunk)
            
    digest = hash.hexdigest()
    return ('%s-%s' % (digest[:4], digest[4:8])).upper()

def hash_maps(output_dir):
    areaids = get_default_areaids()
    hash_digest = hash_map_files(areaids, output_dir)
    print_ln('Hash: %s' % hash_digest)

# AP Change: Moved method from dataparser.py to avoid circular dependency
def get_default_areaids():
    return list(range(10))

