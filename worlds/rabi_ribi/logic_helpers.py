"""
This module defines helper methods used for evaluating rule lambdas.
Its probably a little haphazardly sorted.. but the method names are descriptive
enough for it not to be confusing.
"""
from BaseClasses import CollectionState, Region
from worlds.rabi_ribi.existing_randomizer.utility import OpLit, OpNot, OpOr, OpAnd
from worlds.rabi_ribi.options import TrickDifficulty, Knowledge
from typing import Dict

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
    return state.can_reach("Town Main", "Region", player) or \
        has_3_magic_types(state, player)

def can_use_boost(state: CollectionState, player: int):
    """Player can use the boost skill"""
    return state.can_reach("Beach Main", "Region", player) or \
        (
            state.can_reach("Town Shop", "Region", player) and
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

def can_navigate_darkness(state: CollectionState, player: int, options):
    """
    Player has light orb or has option for darkness without light orb turned on
    """
    return state.has("Light Orb", player) or options.darkness_without_light_orb.value

def can_navigate_underwater(state: CollectionState, player: int, options):
    """Player has water orb or has option for water without water orb turned on"""
    return state.has("Water Orb", player) or options.underwater_without_water_orb.value

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
        state.can_reach("Town Shop", "Region", player)

def wall_jump_2(state: CollectionState, player: int):
    """Player can use the upgraded wall jump skill"""
    return state.has("Wall Jump", player) and \
        state.can_reach("Town Shop", "Region", player)

def can_hammer_roll(state: CollectionState, player: int):
    """Player can use the hammer roll skill"""
    return state.has("Hammer Roll", player) and \
        state.has("Bunny Whirl", player) and \
        state.has("Piko Hammer", player)

def can_hammer_roll_3(state: CollectionState, player: int):
    """Player can use the upgraded hammer roll skill"""
    return can_hammer_roll(state, player) and \
        state.can_reach("Town Shop", "Region", player) and \
        state.has("Chapter 3", player)

def can_get_speed_boost_3(state: CollectionState, player: int):
    """Player can use the upgraded speed boost skill"""
    return state.has("Speed boost", player) and \
        state.can_reach("Town Shop", "Region", player)

def can_bunny_amulet(state: CollectionState, player: int):
    """Player can use the bunny amulet skill"""
    return state.has("Chapter 2", player)

def can_bunny_amulet_2(state: CollectionState, player: int):
    """Player can use 2 bunny amulet skills"""
    return state.has("Chapter 3", player) or \
        (
            can_bunny_amulet(state, player) and \
            state.can_reach("Town Shop", "Region", player)
        )

def can_bunny_amulet_3(state: CollectionState, player: int):
    """Player can use 3 bunny amulet skills"""
    return state.has("Chapter 4", player) or \
        (
            can_bunny_amulet(state, player) and \
            state.can_reach("Town Shop", "Region", player)
        )

def can_recruit_cocoa(state: CollectionState, player: int):
    """Player can recruit cocoa"""
    return state.has("Cocoa 1", player) and \
        state.has("Kotri 1", player) and \
        state.can_reach("Cave Cocoa", "Region", player)

def can_recruit_ashuri(state: CollectionState, player: int):
    """Player can recruit ashuri"""
    return state.can_reach("Riverbank Level3", "Region", player) and \
        state.can_reach("Town Main", "Region", player) and \
        state.can_reach("Spectral West", "Region", player)

def can_recruit_rita(state: CollectionState, player: int):
    """Player can recruit rita"""
    return state.can_reach("Snowland Rita", "Region", player)

def can_recruit_cicini(state: CollectionState, player: int):
    """Player can recruit cicini"""
    return state.can_reach("Spectral Cicini Room", "Region", player)

def can_recruit_saya(state: CollectionState, player: int):
    """Player can recruit saya"""
    return state.can_reach("Evernight Saya", "Region", player) and \
        state.can_reach("Evernight East Of Warp", "Region", player)

def can_recruit_syaro(state: CollectionState, player: int):
    """Player can recruit syaro"""
    return state.can_reach("System Interior Main", "Region", player)

def can_recruit_pandora(state: CollectionState, player: int):
    """Player can recruit pandora"""
    return state.can_reach("Pyramid Main", "Region", player)

def can_recruit_nieve(state: CollectionState, player: int):
    """Player can recruit nieve"""
    return state.can_reach("Palace Level 5", "Region", player) and \
        state.can_reach("Icy Summit Main", "Region", player)

def can_recruit_nixie(state: CollectionState, player: int):
    """Player can recruit nixie"""
    return state.can_reach("Palace Level 5", "Region", player) and \
        state.can_reach("Icy Summit Main", "Region", player)

def can_recruit_aruraune(state: CollectionState, player: int):
    """Player can recruit aruraune"""
    return state.can_reach("Forest Night West", "Region", player)

def can_recruit_seana(state: CollectionState, player: int):
    """Player can recruit seana"""
    return state.has("Vanilla Recruit", player) and \
        state.has("Chocolate Recruit", player) and \
        state.has("Cicini Recruit", player) and \
        state.has("Syaro Recruit", player) and \
        state.has("Nieve Recruit", player) and \
        state.has("Nixie Recruit", player) and \
        state.can_reach("Aquarium East", "Region", player) and \
        state.can_reach("Park Town Entrance", "Region", player)

def can_recruit_lilith(state: CollectionState, player: int):
    """Player can recruit lilith"""
    return state.can_reach("Sky Island Main", "Region", player)

def can_recruit_vanilla(state: CollectionState, player: int):
    """Player can recruit vanilla"""
    return state.can_reach("Sky Bridge East Lower", "Region", player)

def can_recruit_chocolate(state: CollectionState, player: int):
    """Player can recruit chocolate"""
    return state.has("Chapter 1", player)and \
        state.can_reach("Ravine Chocolate", "Region", player)

def can_recruit_kotri(state: CollectionState, player: int):
    """Player can recruit kotri"""
    return state.has("Kotri 2", player) and \
        state.can_reach("Volcanic Main", "Region", player)

def can_recruit_keke_bunny(state: CollectionState, player: int):
    """Player can recruit keke bunny"""
    return state.can_reach("Plurkwood Main", "Region", player) and \
        state.can_reach("Town Main", "Region", player)

def can_recruit_n_town_members(state: CollectionState, num_town_members: int, player: int):
    """
    Player can recruit a set number of town members
    
    :int num_town_members: the number of town members to satisfy the condition
    """
    return state.count_group("Town Members", player) > num_town_members

def can_be_speedy(state: CollectionState, player: int):
    """Player can buy the speed up buff"""
    return can_recruit_cicini(state, player) and \
        state.can_reach("Town Main", "Region", player) and \
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
    """Player can reach chapter 1"""
    return state.can_reach("Town Main", "Region", player)

def can_reach_chapter_2(state: CollectionState, player: int):
    """Player can reach chapter 2"""
    return state.can_reach("Town Main", "Region", player) and \
        can_recruit_n_town_members(state, 2, player)

def can_reach_chapter_3(state: CollectionState, player: int):
    """Player can reach chapter 3"""
    return state.can_reach("Town Main", "Region", player) and \
        can_recruit_n_town_members(state, 4, player)

def can_reach_chapter_4(state: CollectionState, player: int):
    """Player can reach chapter 4"""
    return state.can_reach("Town Main", "Region", player) and \
        can_recruit_n_town_members(state, 7, player)

def can_reach_chapter_5(state: CollectionState, player: int):
    """Player can reach chapter 5"""
    return state.can_reach("Town Main", "Region", player) and \
        can_recruit_n_town_members(state, 10, player)

def can_move_out_of_prologue_areas(state: CollectionState, player: int, options):
    """Player can reach areas not locked to prologue"""
    return state.has("Chapter 1", player) or (options.open_mode.value)

def can_reach_ashuri_2(state: CollectionState, player: int):
    """Player can reach Ashuri 2"""
    return state.can_reach("Riverbank Level3", "Region", player)

def can_reach_cocoa_1(state: CollectionState, player: int):
    """Player can reach Cocoa 1"""
    return state.can_reach("Forest Cocoa Room", "Region", player)

def can_reach_kotri_1(state: CollectionState, player: int):
    """Player can reach Kotri 1"""
    return state.can_reach("Park Kotri", "Region", player)

def can_reach_ribbon(state: CollectionState, player: int):
    """Player can reach ribbon"""
    return state.can_reach("Spectral Warp", "Region", player)

def is_at_least_hard_difficulty(options):
    """Trick difficulty is at least hard"""
    return options.trick_difficulty >= TrickDifficulty.option_hard

def is_at_least_v_hard_difficulty(options):
    """Trick difficulty is at least hard"""
    return options.trick_difficulty >= TrickDifficulty.option_v_hard

def is_at_least_stupid_difficulty(options):
    """Trick difficulty is at least hard"""
    return options.trick_difficulty >= TrickDifficulty.option_stupid

def is_at_least_intermediate_knowledge(options):
    """Knowledge is at least intermediate"""
    return options.knowledge >= Knowledge.option_intermediate

def is_at_least_advanced_knowledge(options):
    """Knowledge is at least advanced"""
    return options.knowledge >= Knowledge.option_advanced

def has_enough_amulet_food(state: CollectionState, player: int, num_amulet_food: int):
    return state.can_reach("Town Shop", "Region", player) or \
        (num_amulet_food == 1 and can_bunny_amulet(state, player)) or \
        (num_amulet_food == 2 and can_bunny_amulet_2(state, player)) or \
        (num_amulet_food == 3 and can_bunny_amulet_3(state, player)) or \
        (num_amulet_food >= 4 and (
            state.can_reach("Town Shop", "Region", player) and \
            has_item_menu(state, player) and \
            can_bunny_amulet(state, player)
        ))

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

def convert_ap_name_to_existing_rando_name(name):
    """
    Converts a name from the existing randomizer to AP.
    This converts from capitalized underscore seperation to Captialization with spaces.
    E.g. My Item Name -> MY_ITEM_NAME

    :string name: The name to convert
    """
    existing_rando_name = name.split(" ")
    existing_rando_name = "_".join(existing_rando_name).upper()
    return existing_rando_name

def convert_existing_rando_rule_to_ap_rule(existing_rule: object, player: int, regions: Dict[int, Dict[str, Region]], options):
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
            "Tm Cocoa": lambda state: state.has("Cocoa Recruit", player),
            "Tm Ashuri": lambda state: state.has("Ashuri Recruit", player),
            "Tm Rita": lambda state: state.has("Rita Recruit", player),
            "Tm Cicini": lambda state: state.has("Cicini Recruit", player),
            "Tm Saya": lambda state: state.has("Saya Recruit", player),
            "Tm Syaro": lambda state: state.has("Syaro Recruit", player),
            "Tm Pandora": lambda state: state.has("Pandora Recruit", player),
            "Tm Nieve": lambda state: state.has("Nieve Recruit", player),
            "Tm Nixie": lambda state: state.has("Nixie Recruit", player),
            "Tm Aruraune": lambda state: state.has("Aruraune Recruit", player),
            "Tm Seana": lambda state: state.has("Seana Recruit", player),
            "Tm Lilith": lambda state: state.has("Lilith Recruit", player),
            "Tm Vanilla": lambda state: state.has("Vanilla Recruit", player),
            "Tm Chocolate": lambda state: state.has("Chocolate Recruit", player),
            "Tm Kotri": lambda state: state.has("Kotri Recruit", player),
            "Tm Keke Bunny": lambda state: state.has("Keke Bunny Recruit", player),
            "Speedy": lambda state: can_be_speedy(state, player),
            "Speed1": lambda state: can_use_speed_1(state, player),
            "Speed2": lambda state: can_use_speed_2(state, player),
            "Speed3": lambda state: can_use_speed_3(state, player),
            "Speed5": lambda state: can_use_speed_5(state, player),
            "3 Magic Types": lambda state: has_3_magic_types(state, player),
            "Item Menu": lambda state: has_item_menu(state, player),
            "Chapter 1": lambda state: state.has("Chapter 1", player),
            "Chapter 2": lambda state: state.has("Chapter 2", player),
            "Chapter 3": lambda state: state.has("Chapter 3", player),
            "Chapter 4": lambda state: state.has("Chapter 4", player),
            "Chapter 5": lambda state: state.has("Chapter 5", player),
            "Boost": lambda state: can_use_boost(state, player),
            "Boost Many": lambda state: can_use_boost(state, player),
            "Darkness": lambda state: can_navigate_darkness(state, player, options),
            "Underwater": lambda state: can_navigate_underwater(state, player, options),
            "Prologue Trigger": lambda state: can_move_out_of_prologue_areas(state, player, options),
            "Cocoa 1": lambda state: can_reach_cocoa_1(state, player),
            "Kotri 1": lambda state: can_reach_kotri_1(state, player),
            "Ashuri 2": lambda state: can_reach_ashuri_2(state, player),
            "Boss Ribbon": lambda state: can_reach_ribbon(state, player),
            "Difficulty Hard": lambda _: is_at_least_hard_difficulty(options),
            "Difficulty Stupid": lambda _: is_at_least_stupid_difficulty(options),
            "Difficulty V Hard": lambda _: is_at_least_v_hard_difficulty(options),
            "Knowledge Intermediate": lambda _: is_at_least_intermediate_knowledge(options),
            "Knowledge Advanced": lambda _: is_at_least_advanced_knowledge(options),
            "Amulet Food": lambda state: has_enough_amulet_food(state, player, 1),
            "2 Amulet Food": lambda state: has_enough_amulet_food(state, player, 2),
            "3 Amulet Food": lambda state: has_enough_amulet_food(state, player, 3),
            "Many Amulet Food": lambda state: has_enough_amulet_food(state, player, 4),
            "Open Mode": lambda _: options.open_mode.value,
            "Block Clips Required": lambda _: options.block_clips_required.value,
            "Semisolid Clips Required": lambda _: options.semi_solid_clips_required.value,
            "Zip Required": lambda _: options.zips_required.value
        }
        if literal in literal_eval_map:
            return literal_eval_map[literal]
        elif literal.endswith("tm"):
            num_town_members = int(literal[:-2:])
            return lambda state: can_recruit_n_town_members(state, num_town_members, player)
        elif literal in regions:
            return lambda state: state.can_reach(literal, "Region", player)
        return lambda state: state.has(literal, player)
    elif isinstance(existing_rule, OpNot):
        expr = convert_existing_rando_rule_to_ap_rule(existing_rule.expr, player, regions, options)
        return lambda state: not expr(state)
    elif isinstance(existing_rule, OpOr):
        expr_l = convert_existing_rando_rule_to_ap_rule(existing_rule.exprL, player, regions, options)
        expr_r = convert_existing_rando_rule_to_ap_rule(existing_rule.exprR, player, regions, options)
        return lambda state: expr_l(state) or expr_r(state)
    elif isinstance(existing_rule, OpAnd):
        expr_l = convert_existing_rando_rule_to_ap_rule(existing_rule.exprL, player, regions, options)
        expr_r = convert_existing_rando_rule_to_ap_rule(existing_rule.exprR, player, regions, options)
        return lambda state: expr_l(state) and expr_r(state)
    raise ValueError("Invalid Expression recieved.")
