"""
This module defines helper methods used for evaluating rule lambdas.
Its probably a little haphazardly sorted.. but the method names are descriptive
enough for it not to be confusing.
"""
from BaseClasses import CollectionState
from worlds.rabi_ribi.existing_randomizer.utility import OpLit, OpNot, OpOr, OpAnd

def has_3_magic_types(state: CollectionState, player: int):
    """Player has at least 3 types of magic"""
    total_magic = sum(1 for magic in [
        "Sunny Beam",
        "Chaos Rod",
        "Healing Staff",
        "Explode Shot",
        "Carrot Shooter"
    ] if state.has(magic, player)) + 1
    return total_magic >= 3

def has_item_menu(state: CollectionState, player: int):
    """Player has access to the item menu"""
    return state.has("Town Main", player) or \
        has_3_magic_types(state, player)

def can_use_boost(state: CollectionState, player: int):
    """Player can use the boost skill"""
    return state.has("Beach Main", player) or \
        (
            state.has("Town Shop", player) and
            has_item_menu(state, player)
        )

def explosives(state: CollectionState, player: int):
    """Player has explosives they can use anywhere"""
    return state.has("Carrot Bomb", player) or \
        (
            state.has("Carrot Shooter", player) and
            can_use_boost(state, player)
        )

def explosives_enemy(state: CollectionState, player: int):
    """Player has explosives or can explode an enemy nearby."""
    return state.has("Carrot Bomb", player) or state.has("Carrot Shooter", player)

def not_locked_to_prologue(state: CollectionState, player: int):
    """Player is out of prologue and has access to more areas."""
    # TODO: open mode option
    return can_reach_chapter_1(state, player)

def can_navigate_darkness(state: CollectionState, player: int):
    """
    Player has light orb or has option for darkness 
    without light orb turned on
    """
    # TODO: navigate without light orb option
    return state.has("Light Orb", player)

def can_navigate_underwater(state: CollectionState, player: int):
    """Player has water orb or has option for water without water orb turned on"""
    # TODO: navigate without water orb option
    return state.has("Water Orb", player)

def can_bunny_strike(state: CollectionState, player: int):
    """Player can use the bunny strike skill"""
    return state.has("Sliding Powder", player) and \
        state.has("Bunny Strike", player) and \
        state.has("Piko Hammer", player)

def can_bunny_whirl(state: CollectionState, player: int):
    """Player can use the bunny whirl skill"""
    return state.has("Bunny Whirl", player) and \
        state.has("Piko Hammer", player)

def can_air_dash(state: CollectionState, player: int):
    """Player can use air dash skill"""
    return state.has("Air Dash", player) and \
        state.has("Piko Hammer", player)

def can_air_dash_3(state: CollectionState, player: int):
    """Player can use the upgraded air dash skill"""
    return can_air_dash(state, player) and \
        state.has("Town Shop", player)

def wall_jump_2(state: CollectionState, player: int):
    """Player can use the upgraded wall jump skill"""
    return state.has("Wall Jump", player) and \
        state.has("Town Shop", player)

def can_hammer_roll(state: CollectionState, player: int):
    """Player can use the hammer roll skill"""
    return state.has("Hammer Roll", player) and \
        state.has("Bunny Whirl", player) and \
        state.has("Piko Hammer", player)

def can_hammer_roll_3(state: CollectionState, player: int):
    """Player can use the upgraded hammer roll skill"""
    return can_hammer_roll(state, player) and \
        state.has("Town Shop", player) and \
        can_reach_chapter_3(state, player)

def can_get_speed_boost_3(state: CollectionState, player: int):
    """Player can use the upgraded speed boost skill"""
    return state.has("Speed boost", player) and \
        state.has("Town Shop", player)

def can_bunny_amulet(state: CollectionState, player: int):
    """Player can use the bunny amulet skill"""
    return can_reach_chapter_2(state, player)

def can_bunny_amulet_2(state: CollectionState, player: int):
    """Player can use 2 bunny amulet skills"""
    return can_reach_chapter_3(state, player) or \
        (
            can_bunny_amulet(state, player) and \
            state.has ("Town Shop", player)
        )

def can_bunny_amulet_3(state: CollectionState, player: int):
    """Player can use 3 bunny amulet skills"""
    return can_reach_chapter_4(state, player) or \
        (
            can_bunny_amulet(state, player) and \
            state.has ("Town Shop", player)
        )

def can_recruit_cocoa(state: CollectionState, player: int):
    """Player can recruit cocoa"""
    return state.has("Cocoa 1", player) and \
        state.has("Kotri 1", player) and \
        state.has("Cave Cocoa", player)

def can_recruit_ashuri(state: CollectionState, player: int):
    """Player can recruit ashuri"""
    return state.has("Riverbank Level3", player) and \
        state.has("Town Main", player) and \
        state.has("Spectral West", player)

def can_recruit_rita(state: CollectionState, player: int):
    """Player can recruit rita"""
    return state.has("Snowland Rita", player)

def can_recruit_cicini(state: CollectionState, player: int):
    """Player can recruit cicini"""
    return state.has("Spectral Cicini Room", player)

def can_recruit_saya(state: CollectionState, player: int):
    """Player can recruit saya"""
    return state.has("Evernight Saya", player) and \
        state.has("Evernight East of Warp", player)

def can_recruit_syaro(state: CollectionState, player: int):
    """Player can recruit syaro"""
    return state.has("System Interior Main", player)

def can_recruit_pandora(state: CollectionState, player: int):
    """Player can recruit pandora"""
    return state.has("Pyramid Main", player)

def can_recruit_nieve(state: CollectionState, player: int):
    """Player can recruit nieve"""
    return state.has("Palace Level 5", player) and \
        state.has("Icy Summit Main", player)

def can_recruit_nixie(state: CollectionState, player: int):
    """Player can recruit nixie"""
    return state.has("Palace Level 5", player) and \
        state.has("Icy Summit Main", player)

def can_recruit_aruraune(state: CollectionState, player: int):
    """Player can recruit aruraune"""
    return state.has("Forest Night West", player)

def can_recruit_seana(state: CollectionState, player: int):
    """Player can recruit seana"""
    return can_recruit_vanilla(state, player) and \
        can_recruit_chocolate(state, player) and \
        can_recruit_cicini(state, player) and \
        can_recruit_syaro(state, player) and \
        can_recruit_nieve(state, player) and \
        can_recruit_nixie(state, player) and \
        state.has("Aquarium East", player) and \
        state.has("Park Town Entrance"), player

def can_recruit_lilith(state: CollectionState, player: int):
    """Player can recruit lilith"""
    return state.has("Sky Island Main", player)

def can_recruit_vanilla(state: CollectionState, player: int):
    """Player can recruit vanilla"""
    return state.has("Sky Bridge East Lower", player)

def can_recruit_chocolate(state: CollectionState, player: int):
    """Player can recruit chocolate"""
    return can_reach_chapter_1(state, player) and \
        state.has("Ravine Chocolate", player)

def can_recruit_kotri(state: CollectionState, player: int):
    """Player can recruit lotri"""
    return state.has("Graveyard Kotri", player) and \
        state.has("Volcanic Main", player)

def can_recruit_keke_bunny(state: CollectionState, player: int):
    """Player can recruit keke bunny"""
    return state.has("Boss Keke Bunny", player) and \
        state.has("Plurkwood Main", player) and \
        state.has("Town Main", player)

def can_recruit_n_town_members(state: CollectionState, num_town_members: int, player: int):
    """
    Player can recruit a set number of town members
    
    :int num_town_members: the number of town members to satisfy the condition
    """
    total_recruitable = sum(1 for can_recruit in [
        can_recruit_cocoa,
        can_recruit_ashuri,
        can_recruit_rita,
        can_recruit_cicini,
        can_recruit_saya,
        can_recruit_syaro,
        can_recruit_pandora,
        can_recruit_nieve,
        can_recruit_nixie,
        can_recruit_aruraune,
        can_recruit_seana,
        can_recruit_lilith,
        can_recruit_vanilla,
        can_recruit_chocolate,
        can_recruit_kotri,
        can_recruit_keke_bunny,
    ] if can_recruit(state, player))
    return total_recruitable >= num_town_members

def can_be_speedy(state: CollectionState, player: int):
    """Player can buy the speed up buff"""
    return can_recruit_cicini(state, player) and \
        state.has("Town Main", player) and \
        can_recruit_n_town_members(state, 3, player)

def can_use_speed_1(state: CollectionState, player: int):
    """Player can has level 1 speed"""
    return can_be_speedy(state, player) or \
        state.has("Speed Boost", player)

def can_use_speed_2(state: CollectionState, player: int):
    """Player can get level 2 speed"""
    return can_get_speed_boost_3(state, player) or \
        state.has("Speed Boost", player)

def can_use_speed_3(state: CollectionState, player: int):
    """Player can get level 3 speed"""
    return can_get_speed_boost_3(state, player) or \
        (
            state.has("Speed Boost", player) and \
            can_be_speedy(state, player)
        )

def can_use_speed_5(state: CollectionState, player: int):
    """
    Player can get level 5 speed

    I dont know why 4 was skipped but its not in the original randomizer.
    """
    return can_be_speedy(state, player) and \
        can_get_speed_boost_3(state, player)

def can_reach_chapter_1(state: CollectionState, player: int):
    """Player can complete chapter 1"""
    return state.has("Town Main", player)

def can_reach_chapter_2(state: CollectionState, player: int):
    """Player can complete chapter 2"""
    return state.has("Town Main", player) and \
        can_recruit_n_town_members(state, 2, player)

def can_reach_chapter_3(state: CollectionState, player: int):
    """Player can complete chapter 3"""
    return state.has("Town Main", player) and \
        can_recruit_n_town_members(state, 4, player)

def can_reach_chapter_4(state: CollectionState, player: int):
    """Player can complete chapter 4"""
    return state.has("Town Main", player) and \
        can_recruit_n_town_members(state, 6, player)

def can_reach_chapter_5(state: CollectionState, player: int):
    """Player can complete chapter 5"""
    return state.has("Town Main", player) and \
        can_recruit_n_town_members(state, 10, player)


####################################################
#           Utility used by other modules
####################################################

def convert_existing_rando_name_to_ap_name(name):
    """
    Converts a name from the existing randomizer to AP.
    This converts from capitalized underscore seperation to Captialization with spaces.
    E.g. MY_ITEM_NAME -> My Item Name

    :string name: The name to convert
    """
    ap_name = name.split("_")
    ap_name = " ".join(word.capitalize() for word in ap_name)
    return ap_name

def convert_existing_rando_rule_to_ap_rule(existing_rule: object, player: int):
    """
    This method converts a rule from the existing randomizer to a lambda which can be passed to AP.
    The existing randomizer evaluates a defined logic expression, which it seperates into 5 classes:
        - OpLit
        - OpAnd
        - OpOr
        - OpNot
        - OpBacktrack
    For simplicity, I did not implement backtrack (yet), since its kind of hacky, complex, 
    and theres not too much benefit (used in 3 non-critical places).

    OpLit is used to evaluate a single literal statement. This can be having an item, or
    can be more complex (e.g. conjunction of literals), which is combined into a single literal
    in the existing randomizer. For the more complicated literals, Ive defined methods above to
    translate them, and placed them in the below "literal_eval_map". If its not in the below map,
    assume the literal is an item which we can check the state for.

    The other Ops are self explanatory, and are translated accordingly.

    :obj existing_rule: The existing rule as an OpX object.
    :player int: the relevant player

    :returns: An evaluatable labmda with one argument (for state)

    :raises ValueError: the passed in existing_rule is not a valid OpX object.
    """
    if isinstance(existing_rule, OpLit):
        literal = convert_existing_rando_name_to_ap_name(existing_rule.name)
        literal_eval_map = {
            "True": lambda _: True,
            "None": lambda _: True,
            "False": lambda _: False,
            "Impossible": lambda _: False,
            "Explosives Enemy": lambda state: explosives_enemy(state, player),
            "Bunny Strike": lambda state: can_bunny_strike(state, player), 
            "Bunny Whirl": lambda state: can_bunny_whirl(state, player), 
            "Wall Jump Lv2": lambda state: wall_jump_2(state, player),
            "Hammer Roll Lv3": lambda state: can_hammer_roll_3(state, player),
            "Hammer Roll": lambda state: can_hammer_roll(state, player),
            "Air Dash Lv3": lambda state: can_air_dash_3(state, player),
            "Air Dash": lambda state: can_air_dash(state, player),
            "Speed Boost Lv3": lambda state: can_get_speed_boost_3(state, player),
            "Bunny Amulet": lambda state: can_bunny_amulet(state, player),
            "Bunny Amulet Lv2": lambda state: can_bunny_amulet_2(state, player),
            "Bunny Amulet Lv3": lambda state: can_bunny_amulet_3(state, player),
            "Piko Hammer Leveled": lambda state: state.has("Piko Hammer", player),
            "Carrot Bomb Entry": lambda state: state.has("Carrot Bomb", player),
            "Carrot Shooter Entry": lambda state: state.has("Carrot Shooter", player),
            "Tm Cocoa": lambda state: can_recruit_cocoa(state, player),
            "Tm Ashuri": lambda state: can_recruit_ashuri(state, player),
            "Tm Rita": lambda state: can_recruit_rita(state, player),
            "Tm Cicini": lambda state: can_recruit_cicini(state, player),
            "Tm Saya": lambda state: can_recruit_saya(state, player),
            "Tm Syaro": lambda state: can_recruit_syaro(state, player),
            "Tm Pandora": lambda state: can_recruit_pandora(state, player),
            "Tm Nieve": lambda state: can_recruit_nieve(state, player),
            "Tm Nixie": lambda state: can_recruit_nixie(state, player),
            "Tm Aruraune": lambda state: can_recruit_aruraune(state, player),
            "Tm Seana": lambda state: can_recruit_seana(state, player),
            "Tm Lilith": lambda state: can_recruit_lilith(state, player),
            "Tm Vanilla": lambda state: can_recruit_vanilla(state, player),
            "Tm Chocolate": lambda state: can_recruit_chocolate(state, player),
            "Tm Kotri": lambda state: can_recruit_kotri(state, player),
            "Tm Keke Bunny": lambda state: can_recruit_keke_bunny(state, player),
            "Speedy": lambda state: can_be_speedy(state, player),
            "Speed1": lambda state: can_use_speed_1(state, player),
            "Speed2": lambda state: can_use_speed_2(state, player),
            "Speed3": lambda state: can_use_speed_3(state, player),
            "Speed5": lambda state: can_use_speed_5(state, player),
            "3 Magic Types": lambda state: has_3_magic_types(state, player),
            "Item Menu": lambda state: has_item_menu(state, player),
            "Chapter 1": lambda state: can_reach_chapter_1(state, player),
            "Chapter 2": lambda state: can_reach_chapter_2(state, player),
            "Chapter 3": lambda state: can_reach_chapter_3(state, player),
            "Chapter 4": lambda state: can_reach_chapter_4(state, player),
            "Chapter 5": lambda state: can_reach_chapter_5(state, player),
            "Boost": lambda state: can_use_boost(state, player),
            "Boost Many": lambda state: can_use_boost(state, player),
            "Darkness": lambda state: can_navigate_darkness(state, player),
            "Underwater": lambda state: can_navigate_underwater(state, player),
        }
        if literal in literal_eval_map:
            return literal_eval_map[literal]
        elif literal.endswith("tm"):
            num_town_members = int(literal[:-2:])
            return lambda state: can_recruit_n_town_members(state, num_town_members, player)
        return lambda state: state.has(literal, player)
    elif isinstance(existing_rule, OpNot):
        expr = convert_existing_rando_rule_to_ap_rule(existing_rule.expr, player)
        return lambda state: not expr(state)
    elif isinstance(existing_rule, OpOr):
        expr_l = convert_existing_rando_rule_to_ap_rule(existing_rule.exprL, player)
        expr_r = convert_existing_rando_rule_to_ap_rule(existing_rule.exprR, player)
        return lambda state: expr_l(state) or expr_r(state)
    elif isinstance(existing_rule, OpAnd):
        expr_l = convert_existing_rando_rule_to_ap_rule(existing_rule.exprL, player)
        expr_r = convert_existing_rando_rule_to_ap_rule(existing_rule.exprR, player)
        return lambda state: expr_l(state) and expr_r(state)
    raise ValueError("Invalid Expression recieved.")
