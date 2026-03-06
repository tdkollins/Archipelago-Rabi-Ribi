"""
This module defines helper methods used for evaluating rules.
It's probably a little haphazardly sorted. but the method names are descriptive
enough for it not to be confusing.
"""

from typing import TYPE_CHECKING, Set
from rule_builder import rules

from .custom_rules import HasEnoughAmuletFood, KnowledgeRule, TrickDifficultyRule, OutOfLogicOptionRule, from_option
from .existing_randomizer.utility import OpBacktrack, OpLit, OpNot, OpOr, OpAnd
from .items import recruit_table, recruit_table_irisu
from .names import ItemName, LocationName
from .options import *
from .utility import convert_existing_rando_name_to_ap_name

if TYPE_CHECKING:
    from . import RabiRibiWorld

is_at_least_hard_difficulty = TrickDifficultyRule(TrickDifficulty.option_hard)
is_at_least_v_hard_difficulty = TrickDifficultyRule(TrickDifficulty.option_v_hard)
is_at_least_extreme_difficulty = TrickDifficultyRule(TrickDifficulty.option_extreme)
is_at_least_stupid_difficulty = TrickDifficultyRule(TrickDifficulty.option_stupid)

is_at_least_intermediate_knowledge = KnowledgeRule(Knowledge.option_intermediate)
is_at_least_advanced_knowledge = KnowledgeRule(Knowledge.option_advanced)
is_at_least_obscure_knowledge = KnowledgeRule(Knowledge.option_obscure)

can_block_clip = OutOfLogicOptionRule("Block Clip", BlockClipsRequired, True)
can_semi_solid_clip = OutOfLogicOptionRule("Semisolid Clip", SemiSolidClipsRequired, True)
can_zip = OutOfLogicOptionRule("Zip", ZipsRequired, True)
can_bunstrike_zip = OutOfLogicOptionRule("Bunstrike Zip", BunstrikeZipsRequired, True)
can_do_boring_tricks = OutOfLogicOptionRule("Boring", BoringTricksRequired, True)
can_use_event_warps = OutOfLogicOptionRule("Event Warp Out of Logic", EventWarpsInLogic, True)
can_enter_plurkwood = OutOfLogicOptionRule("Plurkwood Out of Logic", IncludePlurkwood, True)

carrot_shooter_in_logic = \
    OutOfLogicOptionRule("Carrot Shooter Out of Logic", CarrotShooterInLogic, True) & rules.Has(ItemName.carrot_shooter)
rainbow_shot_in_logic = \
    OutOfLogicOptionRule("Rainbow Egg Out of Logic", RainbowShotInLogic, True) & rules.Has(ItemName.easter_egg, count = 5)

"""Player has darkness without light orb turned on."""
can_navigate_darkness_without_light_orb = \
    OutOfLogicOptionRule("Darkness Out of Logic", DarknessWithoutLightOrb, True)

"""Player has option for underwater without water orb turned on"""
can_navigate_underwater_without_water_orb = \
    OutOfLogicOptionRule("Underwater Out of Logic", UnderwaterWithoutWaterOrb, True)

"""Player has at least 3 types of magic"""
# If playing with more than 5 Easter Eggs, Rainbow Shot could be used as a magic type
has_3_magic_types = \
    rules.HasGroupUnique("Magic", 2) | \
    (rainbow_shot_in_logic & rules.HasGroupUnique("Magic", 1))

"""Player has access to the item menu"""
has_item_menu = \
    rules.Has("Chapter 1") | \
    (
        is_at_least_advanced_knowledge &
        has_3_magic_types
    )

"""Player can use the boost skill at least once"""
can_use_boost = \
    rules.Has("Boost Unlock") | \
    (
        rules.HasAny("Shop Access", ItemName.rumi_donut) & \
        has_item_menu
    )

"""Player can use the boost skill multiple times"""
can_use_boost_many = \
    rules.Has("Shop Access") & has_item_menu

"""Player can use the boost skill or farm boost meter"""
can_use_boost_boring = \
    (rules.Has("Boost Unlock") & can_do_boring_tricks) | \
    ((rules.Has("Shop Access") | rules.Has(ItemName.rumi_donut)) & has_item_menu)

"""Player has light orb or has option for darkness without light orb turned on"""
can_navigate_darkness = \
    can_navigate_darkness_without_light_orb | rules.Has(ItemName.light_orb)

"""Player has water orb or has option for water without water orb turned on"""
can_navigate_underwater = \
    can_navigate_underwater_without_water_orb | rules.Has(ItemName.water_orb)

"""Player can use the bunny strike skill"""
can_bunny_strike = \
    rules.HasAll(ItemName.sliding_powder, ItemName.bunny_strike, ItemName.piko_hammer)

"""Player can use the bunny whirl skill"""
can_bunny_whirl = \
    rules.HasAll(ItemName.bunny_whirl, ItemName.piko_hammer)

"""Player can use air dash skill"""
can_air_dash = \
    rules.HasAll(ItemName.air_dash, ItemName.piko_hammer)

"""Player can use the upgraded air dash skill"""
can_air_dash_3 = \
    can_air_dash & rules.Has("Shop Access")

"""Player can use the upgraded wall jump skill"""
wall_jump_2 = \
    rules.HasAll(ItemName.wall_jump, "Shop Access")

"""Player can use the hammer roll skill"""
can_hammer_roll = \
    rules.HasAll(ItemName.hammer_roll, ItemName.bunny_whirl, ItemName.piko_hammer)

"""Player can use the upgraded hammer roll skill"""
can_hammer_roll_3 = \
    can_hammer_roll & rules.HasAll("Shop Access", "Chapter 3")

"""Player can purchase the upgraded speed boost skill"""
can_get_speed_boost_lv3 = \
    rules.HasAll(ItemName.speed_boost, "Shop Access")

"""Player can open entrances with a fully charged carrot shooter shot"""
can_charge_carrot_shooter_entry = \
    carrot_shooter_in_logic & rules.Has(ItemName.charge_ring)

"""Player can use the bunny amulet"""
can_bunny_amulet = \
    rules.HasAny(ItemName.bunny_amulet, "Chapter 2")

"""Player can use the bunny amulet twice"""
can_bunny_amulet_2 = \
    rules.Has("Chapter 3") | (can_bunny_amulet & rules.Has("Shop Access"))

"""Player can use the bunny amulet 3 times"""
can_bunny_amulet_3 = \
    rules.Has("Chapter 4") | (can_bunny_amulet & rules.Has("Shop Access"))

"""Player can use the bunny amulet 4 times"""
can_bunny_amulet_4 = rules.And(
    can_bunny_amulet,
    rules.Has(ItemName.rumi_recruit),
    options=[rules.OptionFilter(IncludePostGame, True)])

"""Player can recruit Cocoa"""
can_recruit_cocoa = \
    rules.HasAll(ItemName.cocoa_1, ItemName.kotri_1) & \
    rules.CanReachRegion(LocationName.cave_cocoa)

"""Player can recruit Ashuri"""
can_recruit_ashuri = \
    rules.HasAll("Chapter 1", ItemName.ashuri_2)

"""Player can recruit Saya"""
can_recruit_saya = \
    rules.CanReachRegion(LocationName.evernight_saya)

"""Player can recruit Nieve & Nixie"""
can_recruit_nieve_and_nixie = \
    rules.CanReachRegion(LocationName.palace_level_5) & \
    rules.CanReachRegion(LocationName.icy_summit_nixie)

"""Player can recruit Seana"""
can_recruit_seana = rules.HasAll(
    ItemName.seana_1,
    ItemName.vanilla_recruit,
    ItemName.chocolate_recruit,
    ItemName.cicini_recruit,
    ItemName.syaro_recruit,
    ItemName.nieve_recruit,
    ItemName.nixie_recruit)

"""Player can recruit Lilith"""
can_recruit_lilith = rules.Has(ItemName.cicini_recruit)

"""Player can recruit Chocolate"""
can_recruit_chocolate = rules.Has("Chapter 1")

"""Player can recruit Kotri"""
can_recruit_kotri = rules.Has(ItemName.kotri_2)

"""Player can recruit Keke Bunny"""
can_recruit_keke_bunny = rules.CanReachRegion(LocationName.town_main)

"""Player can recruit Irisu"""
can_recruit_irisu = \
    rules.CanReachRegion(LocationName.warp_destination_hospital) & \
    rules.HasAll("Chapter 5", ItemName.miriam_recruit, ItemName.rumi_recruit) & \
    rules.HasFromListUnique(*recruit_table_irisu, count = 15)

def can_recruit_n_town_members(num_town_members: int):
    """
    Player can recruit a set number of town members
    
    :int num_town_members: the number of town members to satisfy the condition
    """
    return rules.HasFromListUnique(*recruit_table, count = num_town_members)

"""Player can buy the speedy buff"""
can_be_speedy = \
    is_at_least_intermediate_knowledge & \
    rules.HasAll(ItemName.cicini_recruit, "Chapter 1") & \
    can_recruit_n_town_members(3)

"""Player can get level 1 speed"""
can_use_speed_1 = \
     can_be_speedy | rules.Has(ItemName.speed_boost)

"""Player can get level 2 speed"""
can_use_speed_2 = \
    can_get_speed_boost_lv3 | can_be_speedy

"""Player can get level 3 speed"""
can_use_speed_3 = \
    can_get_speed_boost_lv3 | \
    (rules.Has(ItemName.speed_boost) & can_be_speedy)

"""
Player can get level 5 speed.
Level 4 is skipped, as you can always buy both speed boost upgrades
and speedy gives the equivalent of 2 levels of movement speed.
"""
can_use_speed_5 = can_be_speedy & can_get_speed_boost_lv3

"""Player can reach chapter 2"""
can_reach_chapter_2 = rules.Has("Chapter 1") & can_recruit_n_town_members(2)

"""Player can reach chapter 3"""
can_reach_chapter_3 = rules.Has("Chapter 2") & can_recruit_n_town_members(4)

"""Player can reach chapter 4"""
can_reach_chapter_4 = rules.Has("Chapter 3") & can_recruit_n_town_members(7)

"""Player can reach chapter 5"""
can_reach_chapter_5 = rules.Has("Chapter 4") & can_recruit_n_town_members(10)

"""Player can reach chapter 6"""
can_reach_chapter_6 = rules.Has("Chapter 5")

"""Player can reach chapter 7"""
can_reach_chapter_7 = rules.Has("Chapter 6") & rules.Has(ItemName.rumi_recruit)

"""Player can reach areas not locked to prologue"""
# Open Mode always enabled.
can_move_out_of_prologue_areas = rules.True_()

"""Player can reach Ribbon"""
can_reach_ribbon = rules.CanReachRegion(LocationName.spectral_warp)

"""Player can reach Keke Bunny"""
can_reach_keke_bunny = rules.CanReachRegion(LocationName.plurkwood_main)

"""Player can purchase food"""
can_purchase_food = rules.Has("Shop Access")

"""Player can purchase cocoa bombs"""
can_purchase_cocoa_bomb = \
    rules.HasAll("Chapter 1", ItemName.cocoa_recruit) & \
    can_recruit_n_town_members(3)

"""Player can use consumable items"""
can_use_consumables = \
    has_item_menu & \
    (
        rules.HasGroupUnique("Consumables", count = 1) |
        can_purchase_food |
        can_purchase_cocoa_bomb
    )

"""Player has access to many consumables due to being able to reach the town shop"""
has_many_amulet_food = \
    rules.And(has_item_menu, rules.Has("Shop Access"), can_bunny_amulet)

####################################################
#           Utility used by other modules
####################################################

literal_eval_map: dict[str, rules.Rule["RabiRibiWorld"]] = {
    "True": rules.True_(),
    "None": rules.True_(),
    "False": rules.False_(),
    "Impossible": rules.False_(),
    "Carrot Shooter": carrot_shooter_in_logic,
    "Explosives With Carrot Shooter": carrot_shooter_in_logic,
    "Bunny Strike": can_bunny_strike,
    "Bunny Whirl": can_bunny_whirl,
    "Wall Jump Lv2": wall_jump_2,
    "Hammer Roll Lv3": can_hammer_roll_3,
    "Hammer Roll": can_hammer_roll,
    "Air Dash Lv3": can_air_dash_3,
    "Air Dash": can_air_dash,
    "Speed Boost Lv3": can_get_speed_boost_lv3,
    "Bunny Amulet": can_bunny_amulet,
    "Bunny Amulet Lv2": can_bunny_amulet_2,
    "Bunny Amulet Lv3": can_bunny_amulet_3,
    "Piko Hammer Leveled": rules.Has(ItemName.piko_hammer),
    "Carrot Bomb Entry": rules.Has(ItemName.carrot_bomb),
    "Carrot Shooter Entry": carrot_shooter_in_logic,
    "Charge Carrot Shooter Entry": can_charge_carrot_shooter_entry,
    "Tm Cocoa": rules.Has(ItemName.cocoa_recruit),
    "Tm Ashuri": rules.Has(ItemName.ashuri_recruit),
    "Tm Rita": rules.Has(ItemName.rita_recruit),
    "Tm Cicini": rules.Has(ItemName.cicini_recruit),
    "Tm Saya": rules.Has(ItemName.saya_recruit),
    "Tm Syaro": rules.Has(ItemName.syaro_recruit),
    "Tm Pandora": rules.Has(ItemName.pandora_recruit),
    "Tm Nieve": rules.Has(ItemName.nieve_recruit),
    "Tm Nixie": rules.Has(ItemName.nixie_recruit),
    "Tm Aruraune": rules.Has(ItemName.aruraune_recruit),
    "Tm Seana": rules.Has(ItemName.seana_recruit),
    "Tm Lilith": rules.Has(ItemName.lilith_recruit),
    "Tm Vanilla": rules.Has(ItemName.vanilla_recruit),
    "Tm Chocolate": rules.Has(ItemName.chocolate_recruit),
    "Tm Kotri": rules.Has(ItemName.kotri_recruit),
    "Tm Keke Bunny": rules.Has(ItemName.keke_bunny_recruit),
    "Tm Miriam": rules.Has(ItemName.miriam_recruit),
    "Tm Rumi": rules.Has(ItemName.rumi_recruit),
    "Tm Irisu": rules.Has(ItemName.irisu_recruit),
    "Speedy": can_be_speedy,
    "Speed1": can_use_speed_1,
    "Speed2": can_use_speed_2,
    "Speed3": can_use_speed_3,
    "Speed5": can_use_speed_5,
    "3 Magic Types": has_3_magic_types,
    "Item Menu": has_item_menu,
    "Chapter 1": rules.Has("Chapter 1"),
    "Chapter 2": rules.Has("Chapter 2"),
    "Chapter 3": rules.Has("Chapter 3"),
    "Chapter 4": rules.Has("Chapter 4"),
    "Chapter 5": rules.Has("Chapter 5"),
    "Chapter 6": rules.Has("Chapter 6"),
    "Chapter 7": rules.Has("Chapter 7"),
    "Boost": can_use_boost,
    "Boost Many": can_use_boost_many,
    "Boost Boring": can_use_boost_boring,
    "Darkness": can_navigate_darkness,
    "Darkness Without Light Orb": can_navigate_darkness_without_light_orb,
    "Underwater": can_navigate_underwater,
    "Underwater Without Water Orb": can_navigate_underwater_without_water_orb,
    "Prologue Trigger": can_move_out_of_prologue_areas,
    "Cocoa 1": rules.Has(ItemName.cocoa_1),
    "Kotri 1": rules.Has(ItemName.kotri_1),
    "Ashuri 2": rules.Has(ItemName.ashuri_2),
    "Boss Ribbon": can_reach_ribbon,
    "Difficulty Hard": is_at_least_hard_difficulty,
    "Difficulty V Hard": is_at_least_v_hard_difficulty,
    "Difficulty Extreme": is_at_least_extreme_difficulty,
    "Difficulty Stupid": is_at_least_stupid_difficulty,
    "Knowledge Intermediate": is_at_least_intermediate_knowledge,
    "Knowledge Advanced": is_at_least_advanced_knowledge,
    "Knowledge Obscure": is_at_least_obscure_knowledge,
    "Boring Tricks Required": can_do_boring_tricks,
    "Bunstrike Zip Required": can_bunstrike_zip,
    "Consumable Use": can_use_consumables,
    "Amulet Food": HasEnoughAmuletFood(1),
    "2 Amulet Food": HasEnoughAmuletFood(2),
    "3 Amulet Food": HasEnoughAmuletFood(3),
    "4 Amulet Food": HasEnoughAmuletFood(4),
    "6 Amulet Food": HasEnoughAmuletFood(6),
    "Many Amulet Food": has_many_amulet_food,
    "Open Mode": rules.True_(),
    "Block Clips Required": can_block_clip,
    "Semisolid Clips Required": can_semi_solid_clip,
    "Zip Required": can_zip,
    "Plurkwood Reachable": can_enter_plurkwood,
    "Warp Destination Reachable": from_option(IncludeWarpDestination, True),
    "Post Game Allowed": from_option(IncludePostGame, True),
    "Post Irisu Allowed": from_option(IncludePostIrisu, True),
    "Halloween Reachable": from_option(IncludeHalloween, True),
    "Boss Keke Bunny" : can_reach_keke_bunny,
    "Event Warps Required" : can_use_event_warps,
}

def convert_existing_rando_rule_to_ap_rule(existing_rule: object, player: int, regions: Set[str], options: RabiRibiOptions) -> rules.Rule["RabiRibiWorld"]:
    """
    This method converts a rule from the existing randomizer to a lambda which can be passed to AP.
    The existing randomizer evaluates a defined logic expression, which it seperates into 5 classes:
        - OpLit
        - OpAnd
        - OpOr
        - OpNot
        - OpBacktrack

    OpBacktrack exists in the standalone randomizer for two-way entrances that can only be opened
    from one side. Since AP logic assumes the player can warp to the starting location,
    these entrances add nothing to the graph & can be safely ignored.

    OpLit is used to evaluate a single literal statement. This can be having an item, |
    can be more complex (e.g. conjunction of literals), which is combined into a single literal
    in the existing randomizer. For the more complicated literals, Ive defined methods above to
    translate them, & placed them in the below "literal_eval_map". If its not in the below map,
    assume the literal is an item which we can check the state for.

    The other Ops are self explanatory, & are translated accordingly.

    :obj existing_rule: The existing rule as an OpX object.
    :player int: the relevant player

    :returns: An evaluatable labmda with one argument (for state)

    :raises ValueError: the passed in existing_rule is not a valid OpX object.
    """
    if isinstance(existing_rule, OpLit):
        literal = convert_existing_rando_name_to_ap_name(existing_rule.name)
        if literal in literal_eval_map:
            return literal_eval_map[literal]
        elif literal.endswith("tm"):
            num_town_members = int(literal[:-2:])
            return can_recruit_n_town_members(num_town_members)
        elif literal in regions:
            return rules.CanReachRegion(literal)
        return rules.Has(literal)
    elif isinstance(existing_rule, OpNot):
        raise NotImplementedError("Negation is not handled by logic")
    elif isinstance(existing_rule, OpOr):
        expr_l = convert_existing_rando_rule_to_ap_rule(existing_rule.exprL, player, regions, options)
        expr_r = convert_existing_rando_rule_to_ap_rule(existing_rule.exprR, player, regions, options)
        return expr_l | expr_r
    elif isinstance(existing_rule, OpAnd):
        expr_l = convert_existing_rando_rule_to_ap_rule(existing_rule.exprL, player, regions, options)
        expr_r = convert_existing_rando_rule_to_ap_rule(existing_rule.exprR, player, regions, options)
        return expr_l & expr_r
    elif isinstance(existing_rule, OpBacktrack):
        # Ignore backtracking, as backtracking entrances would require the exit to already be available as a region.
        return rules.False_()
    raise ValueError("Invalid Expression recieved.")
