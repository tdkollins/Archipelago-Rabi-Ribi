"""
This module defines helper methods used for evaluating rule lambdas.
Its probably a little haphazardly sorted.. but the method names are descriptive
enough for it not to be confusing.
"""
from BaseClasses import CollectionState, Region
from typing import Callable, Dict, Set
from .existing_randomizer.utility import OpBacktrack, OpLit, OpNot, OpOr, OpAnd
from .options import RabiRibiOptions, TrickDifficulty, Knowledge
from .names import ItemName, LocationName
from .items import recruit_table, consumable_items, normal_consumable_items

def has_3_magic_types(state: CollectionState, player: int):
    """Player has at least 3 types of magic"""
    return state.count_group_unique("Magic", player) + 1 >= 3

def has_item_menu(state: CollectionState, player: int, options):
    """Player has access to the item menu"""
    return state.can_reach(LocationName.town_main, "Region", player) or \
        (
            is_at_least_advanced_knowledge(options) and
            has_3_magic_types(state, player)
        )

def can_use_boost(state: CollectionState, player: int, options):
    """Player can use the boost skill"""
    return state.can_reach(LocationName.beach_main, "Region", player) or \
        (
            state.can_reach(LocationName.town_shop, "Region", player) and
            has_item_menu(state, player, options)
        )

def carrot_shooter_in_logic(state: CollectionState, player: int, options):
    """Player has carrot shooter and its not out of logic by options"""
    return (options.carrot_shooter_in_logic.value) and state.has(ItemName.carrot_shooter, player)

def can_navigate_darkness(state: CollectionState, player: int, options):
    """
    Player has light orb or has option for darkness without light orb turned on
    """
    return state.has(ItemName.light_orb, player) or options.darkness_without_light_orb.value

def can_navigate_underwater(state: CollectionState, player: int, options):
    """Player has water orb or has option for water without water orb turned on"""
    return state.has(ItemName.water_orb, player) or options.underwater_without_water_orb.value

def can_bunny_strike(state: CollectionState, player: int):
    """Player can use the bunny strike skill"""
    return state.has(ItemName.sliding_powder, player) and \
        state.has(ItemName.bunny_strike, player) and \
        state.has(ItemName.piko_hammer, player)

def can_bunny_whirl(state: CollectionState, player: int):
    """Player can use the bunny whirl skill"""
    return state.has(ItemName.bunny_whirl, player) and \
        state.has(ItemName.piko_hammer, player)

def can_air_dash(state: CollectionState, player: int):
    """Player can use air dash skill"""
    return state.has(ItemName.air_dash, player) and \
        state.has(ItemName.piko_hammer, player)

def can_air_dash_3(state: CollectionState, player: int):
    """Player can use the upgraded air dash skill"""
    return can_air_dash(state, player) and \
        state.can_reach(LocationName.town_shop, "Region", player)

def wall_jump_2(state: CollectionState, player: int):
    """Player can use the upgraded wall jump skill"""
    return state.has(ItemName.wall_jump, player) and \
        state.can_reach(LocationName.town_shop, "Region", player)

def can_hammer_roll(state: CollectionState, player: int):
    """Player can use the hammer roll skill"""
    return state.has(ItemName.hammer_roll, player) and \
        state.has(ItemName.bunny_whirl, player) and \
        state.has(ItemName.piko_hammer, player)

def can_hammer_roll_3(state: CollectionState, player: int):
    """Player can use the upgraded hammer roll skill"""
    return can_hammer_roll(state, player) and \
        state.can_reach(LocationName.town_shop, "Region", player) and \
        state.has("Chapter 3", player)

def can_get_speed_boost_3(state: CollectionState, player: int):
    """Player can use the upgraded speed boost skill"""
    return state.has(ItemName.speed_boost, player) and \
        state.can_reach(LocationName.town_shop, "Region", player)

def can_charge_carrot_shooter_entry(state: CollectionState, player: int, options):
    """Player can open entrances with a fully charged carrot shooter shot"""
    return carrot_shooter_in_logic(state, player, options) and \
        state.has(ItemName.charge_ring, player)

def can_bunny_amulet(state: CollectionState, player: int):
    """Player can use the bunny amulet skill"""
    return state.has("Chapter 2", player)

def can_bunny_amulet_2(state: CollectionState, player: int):
    """Player can use 2 bunny amulet skills"""
    return state.has("Chapter 3", player) or \
        (
            can_bunny_amulet(state, player) and \
            state.can_reach(LocationName.town_shop, "Region", player)
        )

def can_bunny_amulet_3(state: CollectionState, player: int):
    """Player can use 3 bunny amulet skills"""
    return state.has("Chapter 4", player) or \
        (
            can_bunny_amulet(state, player) and \
            state.can_reach(LocationName.town_shop, "Region", player)
        )

def can_bunny_amulet_4(state: CollectionState, player: int, options):
    """Player can use 4 bunny amulet skills"""
    # TODO: Add with post game
    return False
    # return options.post_game_allowed.value and \
    #     can_bunny_amulet(state, player) and \
    #     state.has(ItemName.rumi_recruit, player)

def can_recruit_cocoa(state: CollectionState, player: int):
    """Player can recruit cocoa"""
    return state.has(ItemName.cocoa_1, player) and \
        state.has(ItemName.kotri_1, player) and \
        state.can_reach(LocationName.cave_cocoa, "Region", player)

def can_recruit_ashuri(state: CollectionState, player: int):
    """Player can recruit ashuri"""
    return state.can_reach(LocationName.riverbank_level3, "Region", player) and \
        state.can_reach(LocationName.town_main, "Region", player) and \
        state.can_reach(LocationName.spectral_west, "Region", player)

def can_recruit_rita(state: CollectionState, player: int):
    """Player can recruit rita"""
    return state.can_reach(LocationName.snowland_rita, "Region", player)

def can_recruit_cicini(state: CollectionState, player: int):
    """Player can recruit cicini"""
    return state.can_reach(LocationName.spectral_cicini_room, "Region", player)

def can_recruit_saya(state: CollectionState, player: int):
    """Player can recruit saya"""
    return state.can_reach(LocationName.evernight_saya, "Region", player) and \
        state.can_reach(LocationName.evernight_east_of_warp, "Region", player)

def can_recruit_syaro(state: CollectionState, player: int):
    """Player can recruit syaro"""
    return state.can_reach(LocationName.system_interior_main, "Region", player)

def can_recruit_pandora(state: CollectionState, player: int):
    """Player can recruit pandora"""
    return state.can_reach(LocationName.pyramid_main, "Region", player)

def can_recruit_nieve(state: CollectionState, player: int):
    """Player can recruit nieve"""
    return state.can_reach(LocationName.palace_level_5, "Region", player) and \
        state.can_reach(LocationName.icy_summit_main, "Region", player)

def can_recruit_nixie(state: CollectionState, player: int):
    """Player can recruit nixie"""
    return state.can_reach(LocationName.palace_level_5, "Region", player) and \
        state.can_reach(LocationName.icy_summit_main, "Region", player)

def can_recruit_aruraune(state: CollectionState, player: int):
    """Player can recruit aruraune"""
    return state.can_reach(LocationName.forest_night_west, "Region", player)

def can_recruit_seana(state: CollectionState, player: int):
    """Player can recruit seana"""
    return state.has(ItemName.vanilla_recruit, player) and \
        state.has(ItemName.chocolate_recruit, player) and \
        state.has(ItemName.cicini_recruit, player) and \
        state.has(ItemName.syaro_recruit, player) and \
        state.has(ItemName.nieve_recruit, player) and \
        state.has(ItemName.nixie_recruit, player) and \
        state.can_reach(LocationName.aquarium_east, "Region", player) and \
        state.can_reach(LocationName.park_town_entrance, "Region", player)

def can_recruit_lilith(state: CollectionState, player: int):
    """Player can recruit lilith"""
    return state.can_reach(LocationName.sky_island_main, "Region", player)

def can_recruit_vanilla(state: CollectionState, player: int):
    """Player can recruit vanilla"""
    return state.can_reach(LocationName.sky_bridge_east_lower, "Region", player)

def can_recruit_chocolate(state: CollectionState, player: int):
    """Player can recruit chocolate"""
    return state.has("Chapter 1", player)and \
        state.can_reach(LocationName.ravine_chocolate, "Region", player)

def can_recruit_kotri(state: CollectionState, player: int):
    """Player can recruit kotri"""
    return state.has(ItemName.kotri_2, player) and \
        state.can_reach(LocationName.volcanic_main, "Region", player)

def can_recruit_keke_bunny(state: CollectionState, player: int):
    """Player can recruit keke bunny"""
    return state.can_reach(LocationName.plurkwood_main, "Region", player) and \
        state.can_reach(LocationName.town_main, "Region", player)

def can_recruit_n_town_members(state: CollectionState, num_town_members: int, player: int):
    """
    Player can recruit a set number of town members
    
    :int num_town_members: the number of town members to satisfy the condition
    """
    return state.count_from_list_unique(recruit_table, player) > num_town_members

def can_be_speedy(state: CollectionState, player: int, options):
    """Player can buy the speedy buff"""
    return is_at_least_intermediate_knowledge(options) and \
        can_recruit_cicini(state, player) and \
        state.can_reach(LocationName.town_main, "Region", player) and \
        can_recruit_n_town_members(state, 3, player)

def can_use_speed_1(state: CollectionState, player: int, options):
    """Player can get level 1 speed"""
    return can_be_speedy(state, player, options) or \
        state.has(ItemName.speed_boost, player)

def can_use_speed_2(state: CollectionState, player: int, options):
    """Player can get level 2 speed"""
    return can_get_speed_boost_3(state, player) or \
        can_be_speedy(state, player, options)

def can_use_speed_3(state: CollectionState, player: int, options):
    """Player can get level 3 speed"""
    return can_get_speed_boost_3(state, player) or \
        (
            state.has(ItemName.speed_boost, player) and \
            can_be_speedy(state, player, options)
        )

def can_use_speed_5(state: CollectionState, player: int, options):
    """
    Player can get level 5 speed.
    Level 4 is skipped, as you can always buy both speed boost upgrades
    and speedy gives the equivalent of 2 levels of movement speed.
    """
    return can_be_speedy(state, player, options) and \
        can_get_speed_boost_3(state, player)

def can_reach_chapter_1(state: CollectionState, player: int):
    """Player can reach chapter 1"""
    return state.can_reach(LocationName.town_main, "Region", player)

def can_reach_chapter_2(state: CollectionState, player: int):
    """Player can reach chapter 2"""
    return state.can_reach(LocationName.town_main, "Region", player) and \
        can_recruit_n_town_members(state, 2, player)

def can_reach_chapter_3(state: CollectionState, player: int):
    """Player can reach chapter 3"""
    return state.can_reach(LocationName.town_main, "Region", player) and \
        can_recruit_n_town_members(state, 4, player)

def can_reach_chapter_4(state: CollectionState, player: int):
    """Player can reach chapter 4"""
    return state.can_reach(LocationName.town_main, "Region", player) and \
        can_recruit_n_town_members(state, 7, player)

def can_reach_chapter_5(state: CollectionState, player: int):
    """Player can reach chapter 5"""
    return state.can_reach(LocationName.town_main, "Region", player) and \
        can_recruit_n_town_members(state, 10, player)

def can_move_out_of_prologue_areas(state: CollectionState, player: int, options):
    """Player can reach areas not locked to prologue"""
    return state.has("Chapter 1", player) or (options.open_mode.value)

def can_reach_ashuri_2(state: CollectionState, player: int):
    """Player can reach Ashuri 2"""
    return state.can_reach(LocationName.riverbank_level3, "Region", player)

def can_reach_cocoa_1(state: CollectionState, player: int):
    """Player can reach Cocoa 1"""
    return state.can_reach(LocationName.forest_cocoa_room, "Region", player)

def can_reach_kotri_1(state: CollectionState, player: int):
    """Player can reach Kotri 1"""
    return state.can_reach(LocationName.park_kotri, "Region", player)

def can_reach_ribbon(state: CollectionState, player: int):
    """Player can reach Ribbon"""
    return state.can_reach(LocationName.spectral_warp, "Region", player)

def can_reach_keke_bunny(state: CollectionState, player: int):
    """Player can reach Keke Bunny"""
    return state.can_reach(LocationName.plurkwood_main, "Region", player)

def can_use_consumables(state: CollectionState, player: int, options):
    """Player can use consumable items"""
    return has_item_menu(state, player, options) and \
        state.has_from_list(consumable_items, player, 1)

def can_purchase_food(state: CollectionState, player: int):
    """Player can purchase food"""
    return state.can_reach(LocationName.town_shop, "Region", player)

def can_purchase_cocoa_bomb(state: CollectionState, player: int):
    """Player can purchase food"""
    return state.can_reach(LocationName.town_main, "Region", player) and \
        state.has(ItemName.cocoa_recruit, player) and \
        can_recruit_n_town_members(state, 3, player)

def is_at_least_hard_difficulty(options):
    """Trick difficulty is at least hard"""
    return options.trick_difficulty >= TrickDifficulty.option_hard

def is_at_least_v_hard_difficulty(options):
    """Trick difficulty is at least very hard"""
    return options.trick_difficulty >= TrickDifficulty.option_v_hard

def is_at_least_extreme_difficulty(options):
    """Trick difficulty is at least extreme"""
    return options.trick_difficulty >= TrickDifficulty.option_extreme

def is_at_least_stupid_difficulty(options):
    """Trick difficulty is at least stupid"""
    return options.trick_difficulty >= TrickDifficulty.option_stupid

def is_at_least_intermediate_knowledge(options):
    """Knowledge is at least intermediate"""
    return options.knowledge >= Knowledge.option_intermediate

def is_at_least_advanced_knowledge(options):
    """Knowledge is at least advanced"""
    return options.knowledge >= Knowledge.option_advanced

def is_at_least_obscure_knowledge(options):
    """Knowledge is at least obscure"""
    return options.knowledge >= Knowledge.option_obscure

def has_enough_amulet_food(state: CollectionState, player: int, options, num_amulet_food: int):
    """Player can utilize enough items to perform a trick"""
    amulet = 0
    food = 0

    if can_bunny_amulet_4(state, player, options):
        amulet = 4
    elif can_bunny_amulet_3(state, player):
        amulet = 3
    elif can_bunny_amulet_2(state, player):
        amulet = 2
    elif can_bunny_amulet(state, player):
        amulet = 1
    
    if has_item_menu(state, player, options):
        if state.has(ItemName.rumi_donut, player):
            food = 1
            # Eating a Rumi Donut gives an amulet charge
            if can_bunny_amulet(state, player):
                amulet += 1
            food += state.count_from_list_unique(normal_consumable_items, player)
            if amulet >= 4 and state.has(ItemName.kotri_recruit, player) and \
                can_recruit_n_town_members(state, 3, player):
                amulet += 1
    return (amulet + food) >= num_amulet_food

def has_many_amulet_food(state: CollectionState, player: int, options):
    """Player has access to many consumables due to being able to reach the town shop"""
    return has_item_menu(state, player, options) and \
        state.can_reach(LocationName.town_shop, "Region", player) and \
        can_bunny_amulet(state, player)

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

def convert_existing_rando_rule_to_ap_rule(existing_rule: object, player: int, regions: Set[str], options: RabiRibiOptions) -> Callable[[CollectionState], bool]:
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
            "Carrot Shooter": lambda state: carrot_shooter_in_logic(state, player, options),
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
            "Piko Hammer Leveled": lambda state: state.has(ItemName.piko_hammer, player),
            "Carrot Bomb Entry": lambda state: state.has(ItemName.carrot_bomb, player),
            "Carrot Shooter Entry": lambda state: carrot_shooter_in_logic(state, player, options),
            "Charge Carrot Shooter Entry": lambda state: can_charge_carrot_shooter_entry(state, player, options),
            "Tm Cocoa": lambda state: state.has(ItemName.cocoa_recruit, player),
            "Tm Ashuri": lambda state: state.has(ItemName.ashuri_recruit, player),
            "Tm Rita": lambda state: state.has(ItemName.rita_recruit, player),
            "Tm Cicini": lambda state: state.has(ItemName.cicini_recruit, player),
            "Tm Saya": lambda state: state.has(ItemName.saya_recruit, player),
            "Tm Syaro": lambda state: state.has(ItemName.syaro_recruit, player),
            "Tm Pandora": lambda state: state.has(ItemName.pandora_recruit, player),
            "Tm Nieve": lambda state: state.has(ItemName.nieve_recruit, player),
            "Tm Nixie": lambda state: state.has(ItemName.nixie_recruit, player),
            "Tm Aruraune": lambda state: state.has(ItemName.aruraune_recruit, player),
            "Tm Seana": lambda state: state.has(ItemName.seana_recruit, player),
            "Tm Lilith": lambda state: state.has(ItemName.lilith_recruit, player),
            "Tm Vanilla": lambda state: state.has(ItemName.vanilla_recruit, player),
            "Tm Chocolate": lambda state: state.has(ItemName.chocolate_recruit, player),
            "Tm Kotri": lambda state: state.has(ItemName.kotri_recruit, player),
            "Tm Keke Bunny": lambda state: state.has(ItemName.keke_bunny_recruit, player),
            "Speedy": lambda state: can_be_speedy(state, player, options),
            "Speed1": lambda state: can_use_speed_1(state, player, options),
            "Speed2": lambda state: can_use_speed_2(state, player, options),
            "Speed3": lambda state: can_use_speed_3(state, player, options),
            "Speed5": lambda state: can_use_speed_5(state, player, options),
            "3 Magic Types": lambda state: has_3_magic_types(state, player),
            "Item Menu": lambda state: has_item_menu(state, player, options),
            "Chapter 1": lambda state: state.has("Chapter 1", player),
            "Chapter 2": lambda state: state.has("Chapter 2", player),
            "Chapter 3": lambda state: state.has("Chapter 3", player),
            "Chapter 4": lambda state: state.has("Chapter 4", player),
            "Chapter 5": lambda state: state.has("Chapter 5", player),
            "Chapter 6": lambda state: state.has("Chapter 6", player),
            "Chapter 7": lambda state: state.has("Chapter 7", player),
            "Boost": lambda state: can_use_boost(state, player, options),
            "Boost Many": lambda state: can_use_boost(state, player, options),
            "Darkness": lambda state: can_navigate_darkness(state, player, options),
            "Darkness Without Light Orb": lambda _: options.darkness_without_light_orb.value,
            "Underwater": lambda state: can_navigate_underwater(state, player, options),
            "Underwater Without Water Orb": lambda _: options.underwater_without_water_orb.value,
            "Prologue Trigger": lambda state: can_move_out_of_prologue_areas(state, player, options),
            "Cocoa 1": lambda state: can_reach_cocoa_1(state, player),
            "Kotri 1": lambda state: can_reach_kotri_1(state, player),
            "Ashuri 2": lambda state: can_reach_ashuri_2(state, player),
            "Boss Ribbon": lambda state: can_reach_ribbon(state, player),
            "Difficulty Hard": lambda _: is_at_least_hard_difficulty(options),
            "Difficulty V Hard": lambda _: is_at_least_v_hard_difficulty(options),
            "Difficulty Extreme": lambda _: is_at_least_extreme_difficulty(options),
            "Difficulty Stupid": lambda _: is_at_least_stupid_difficulty(options),
            "Knowledge Intermediate": lambda _: is_at_least_intermediate_knowledge(options),
            "Knowledge Advanced": lambda _: is_at_least_advanced_knowledge(options),
            "Knowledge Obscure": lambda _: is_at_least_obscure_knowledge(options),
            "Consumable Use": lambda state: can_use_consumables(state, player, options),
            "Rumi Donut": lambda state: can_purchase_food(state, player),
            "Rumi Cake": lambda state: can_purchase_food(state, player),
            "Cocoa Bomb": lambda state: can_purchase_cocoa_bomb(state, player),
            "Amulet Food": lambda state: has_enough_amulet_food(state, player, options, 1),
            "2 Amulet Food": lambda state: has_enough_amulet_food(state, player, options, 2),
            "3 Amulet Food": lambda state: has_enough_amulet_food(state, player, options, 3),
            "4 Amulet Food": lambda state: has_enough_amulet_food(state, player, options, 4),
            "6 Amulet Food": lambda state: has_enough_amulet_food(state, player, options, 6),
            "Many Amulet Food": lambda state: has_many_amulet_food(state, player, options),
            "Open Mode": lambda _: options.open_mode.value,
            "Block Clips Required": lambda _: options.block_clips_required.value,
            "Semisolid Clips Required": lambda _: options.semi_solid_clips_required.value,
            "Zip Required": lambda _: options.zips_required.value,
            "Plurkwood Reachable": lambda _: options.plurkwood_reachable.value,
            "Boss Keke Bunny" : lambda state: can_reach_keke_bunny(state, player),
            "Event Warps Required" : lambda _: options.event_warps_in_logic.value,
            # TODO: Add options for missing settings and states
            "Boring Tricks Required": lambda _: False,
            "Bunstrike Zip Required": lambda _: False,
            "Post Irisu Allowed": lambda _: False,
            "Post Game Allowed": lambda _: False,
            "Halloween Reachable": lambda _: False,
            "Warp Destination Reachable": lambda _: False,
            "Tm Irisu": lambda _: False,
            "Tm Miriam": lambda _: False,
            "Tm Rumi": lambda _: False,
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
    # TODO: Convert backtracking logic to be handled in AP
    elif isinstance(existing_rule, OpBacktrack):
        return lambda _: False
    raise ValueError("Invalid Expression recieved.")
