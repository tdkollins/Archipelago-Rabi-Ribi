"""
This module defines helper methods used for evaluating rules.
It's probably a little haphazardly sorted. but the method names are descriptive
enough for it not to be confusing.
"""

from typing import TYPE_CHECKING, Any, Set, override

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart
from Options import Option
from rule_builder import rules
from rule_builder.options import Operator

from .existing_randomizer.utility import OpBacktrack, OpLit, OpNot, OpOr, OpAnd
from .items import recruit_table, recruit_table_irisu
from .names import ItemName, LocationName
from .options import *
from .utility import GAME_NAME, convert_existing_rando_name_to_ap_name

if TYPE_CHECKING:
    from . import RabiRibiWorld

def has_3_magic_types():
    """Player has at least 3 types of magic"""
    # If playing with more than 5 Easter Eggs, Rainbow Shot could be used as a magic type
    return rules.HasGroupUnique("Magic", 2) | (rainbow_shot_in_logic() & rules.HasGroupUnique("Magic", 1))

def has_item_menu():
    """Player has access to the item menu"""
    return rules.Has("Chapter 1") | \
        (
            is_at_least_advanced_knowledge() &
            has_3_magic_types()
        )

def can_use_boost():
    """Player can use the boost skill at least once"""
    return rules.Has("Boost Unlock") | \
        (
            rules.HasAny("Shop Access", ItemName.rumi_donut) & \
            has_item_menu()
        )

def can_use_boost_many():
    """Player can use the boost skill multiple times"""
    return rules.Has("Shop Access") & has_item_menu()

def can_use_boost_boring():
    """Player can use the boost skill or farm boost meter"""
    return (rules.Has("Boost Unlock") & can_do_boring_tricks()) | \
        ((rules.Has("Shop Access") | rules.Has(ItemName.rumi_donut)) & has_item_menu())

def carrot_shooter_in_logic():
    """Player has Carrot Shooter and it's not out of logic by options"""
    return AllowedOutOfLogic(from_option(CarrotShooterInLogic, True)) & rules.Has(ItemName.carrot_shooter)

def rainbow_shot_in_logic():
    """Player has Rainbow Shot and it's not out of logic by options"""
    return AllowedOutOfLogic(from_option(RainbowShotInLogic, True)) & rules.Has(ItemName.easter_egg, count = 5)

def can_navigate_darkness_without_light_orb():
    """
    Player has darkness without light orb turned on.
    """
    return AllowedOutOfLogic(from_option(DarknessWithoutLightOrb, True))

def can_navigate_darkness():
    """
    Player has light orb or has option for darkness without light orb turned on
    """
    return can_navigate_darkness_without_light_orb() | rules.Has(ItemName.light_orb)

def can_navigate_underwater_without_water_orb():
    """Player has option for water without water orb turned on"""
    return AllowedOutOfLogic(from_option(UnderwaterWithoutWaterOrb, True))

def can_navigate_underwater():
    """Player has water orb or has option for water without water orb turned on"""
    return can_navigate_underwater_without_water_orb() | rules.Has(ItemName.water_orb)

def can_bunny_strike():
    """Player can use the bunny strike skill"""
    return rules.HasAll(ItemName.sliding_powder, ItemName.bunny_strike, ItemName.piko_hammer)

def can_bunny_whirl():
    """Player can use the bunny whirl skill"""
    return rules.HasAll(ItemName.bunny_whirl, ItemName.piko_hammer)

def can_air_dash():
    """Player can use air dash skill"""
    return rules.HasAll(ItemName.air_dash, ItemName.piko_hammer)

def can_air_dash_3():
    """Player can use the upgraded air dash skill"""
    return can_air_dash() & rules.Has("Shop Access")

def wall_jump_2():
    """Player can use the upgraded wall jump skill"""
    return rules.HasAll(ItemName.wall_jump, "Shop Access")

def can_hammer_roll():
    """Player can use the hammer roll skill"""
    return rules.HasAll(ItemName.hammer_roll, ItemName.bunny_whirl, ItemName.piko_hammer)

def can_hammer_roll_3():
    """Player can use the upgraded hammer roll skill"""
    return can_hammer_roll() & rules.HasAll("Shop Access", "Chapter 3")

def can_get_speed_boost_lv3():
    """Player can use the upgraded speed boost skill"""
    return rules.HasAll(ItemName.speed_boost, "Shop Access")

def can_charge_carrot_shooter_entry():
    """Player can open entrances with a fully charged carrot shooter shot"""
    return carrot_shooter_in_logic() & rules.Has(ItemName.charge_ring)

def can_bunny_amulet():
    """Player can use the bunny amulet skill"""
    return rules.HasAny(ItemName.bunny_amulet, "Chapter 2")

def can_bunny_amulet_2():
    """Player can use 2 bunny amulet skills"""
    return rules.Has("Chapter 3") | (can_bunny_amulet() & rules.Has("Shop Access"))

def can_bunny_amulet_3():
    """Player can use 3 bunny amulet skills"""
    return rules.Has("Chapter 4") | (can_bunny_amulet() & rules.Has("Shop Access"))

def can_bunny_amulet_4():
    """Player can use 4 bunny amulet skills"""
    return rules.And(
        can_bunny_amulet(),
        rules.Has(ItemName.rumi_recruit),
        options=[rules.OptionFilter(IncludePostGame, True)])

def can_recruit_cocoa():
    """Player can recruit Cocoa"""
    return rules.HasAll(ItemName.cocoa_1, ItemName.kotri_1) & \
        rules.CanReachRegion(LocationName.cave_cocoa)

def can_recruit_ashuri():
    """Player can recruit Ashuri"""
    return rules.HasAll("Chapter 1", ItemName.ashuri_2)

def can_recruit_saya():
    """Player can recruit Saya"""
    return rules.CanReachRegion(LocationName.evernight_saya)

def can_recruit_nieve_and_nixie():
    """Player can recruit Nieve & Nixie"""
    return rules.CanReachRegion(LocationName.palace_level_5) & \
        rules.CanReachRegion(LocationName.icy_summit_nixie)

def can_recruit_seana():
    """Player can recruit Seana"""
    return rules.HasAll(ItemName.seana_1,
        ItemName.vanilla_recruit,
        ItemName.chocolate_recruit,
        ItemName.cicini_recruit,
        ItemName.syaro_recruit,
        ItemName.nieve_recruit,
        ItemName.nixie_recruit)

def can_recruit_lilith():
    """Player can recruit Lilith"""
    return rules.Has(ItemName.cicini_recruit)

def can_recruit_chocolate():
    """Player can recruit Chocolate"""
    return rules.Has("Chapter 1")

def can_recruit_kotri():
    """Player can recruit Kotri"""
    return rules.Has(ItemName.kotri_2)

def can_recruit_keke_bunny():
    """Player can recruit Keke Bunny"""
    return rules.CanReachRegion(LocationName.town_main)

def can_recruit_irisu():
    """Player can recruit Irisu"""
    return rules.CanReachRegion(LocationName.warp_destination_hospital) & \
        rules.HasAll("Chapter 5", ItemName.miriam_recruit, ItemName.rumi_recruit) & \
        rules.HasFromListUnique(*recruit_table_irisu, count = 15)

def can_recruit_n_town_members(num_town_members: int):
    """
    Player can recruit a set number of town members
    
    :int num_town_members: the number of town members to satisfy the condition
    """
    return rules.HasFromListUnique(*recruit_table, count = num_town_members)

def can_be_speedy():
    """Player can buy the speedy buff"""
    return is_at_least_intermediate_knowledge() & \
        rules.HasAll(ItemName.cicini_recruit, "Chapter 1") & \
        can_recruit_n_town_members(3)

def can_use_speed_1():
    """Player can get level 1 speed"""
    return can_be_speedy() | rules.Has(ItemName.speed_boost)

def can_use_speed_2():
    """Player can get level 2 speed"""
    return can_get_speed_boost_lv3() | can_be_speedy()

def can_use_speed_3():
    """Player can get level 3 speed"""
    return can_get_speed_boost_lv3() | \
        (rules.Has(ItemName.speed_boost) & can_be_speedy())

def can_use_speed_5():
    """
    Player can get level 5 speed.
    Level 4 is skipped, as you can always buy both speed boost upgrades
    and speedy gives the equivalent of 2 levels of movement speed.
    """
    return can_be_speedy() & can_get_speed_boost_lv3()

def can_reach_chapter_2():
    """Player can reach chapter 2"""
    return rules.Has("Chapter 1") & can_recruit_n_town_members(2)

def can_reach_chapter_3():
    """Player can reach chapter 3"""
    return rules.Has("Chapter 2") & can_recruit_n_town_members(4)

def can_reach_chapter_4():
    """Player can reach chapter 4"""
    return rules.Has("Chapter 3") & can_recruit_n_town_members(7)

def can_reach_chapter_5():
    """Player can reach chapter 5"""
    return rules.Has("Chapter 4") & can_recruit_n_town_members(10)

def can_reach_chapter_6():
    """Player can reach chapter 6"""
    return rules.Has("Chapter 5")

def can_reach_chapter_7():
    """Player can reach chapter 7"""
    return rules.Has("Chapter 6") & rules.Has(ItemName.rumi_recruit)

def can_move_out_of_prologue_areas():
    """Player can reach areas not locked to prologue"""
    # Open Mode always enabled.
    return rules.True_()

def can_reach_ribbon():
    """Player can reach Ribbon"""
    return rules.CanReachRegion(LocationName.spectral_warp)

def can_reach_keke_bunny():
    """Player can reach Keke Bunny"""
    return rules.CanReachRegion(LocationName.plurkwood_main)

def can_use_consumables():
    """Player can use consumable items"""
    return has_item_menu() & \
        (
            rules.HasGroupUnique("Consumables", count = 1) |
            can_purchase_food() |
            can_purchase_cocoa_bomb()
        )

def can_purchase_food():
    """Player can purchase food"""
    return rules.Has("Shop Access")

def can_purchase_cocoa_bomb():
    """Player can purchase food"""
    return rules.HasAll("Chapter 1", ItemName.cocoa_recruit) & \
        can_recruit_n_town_members(3)

def is_at_least_hard_difficulty():
    """Trick difficulty is at least hard"""
    return AllowedOutOfLogic(from_option(TrickDifficulty, TrickDifficulty.option_hard, "ge"))

def is_at_least_v_hard_difficulty():
    """Trick difficulty is at least very hard"""
    return AllowedOutOfLogic(from_option(TrickDifficulty, TrickDifficulty.option_v_hard, "ge"))

def is_at_least_extreme_difficulty():
    """Trick difficulty is at least extreme"""
    return AllowedOutOfLogic(from_option(TrickDifficulty, TrickDifficulty.option_extreme, "ge"))

def is_at_least_stupid_difficulty():
    """Trick difficulty is at least stupid"""
    return AllowedOutOfLogic(from_option(TrickDifficulty, TrickDifficulty.option_stupid, "ge"))

def is_at_least_intermediate_knowledge():
    """Knowledge is at least intermediate"""
    return AllowedOutOfLogic(from_option(Knowledge, Knowledge.option_intermediate, "ge"))

def is_at_least_advanced_knowledge():
    """Knowledge is at least advanced"""
    return AllowedOutOfLogic(from_option(Knowledge, Knowledge.option_advanced, "ge"))

def is_at_least_obscure_knowledge():
    """Knowledge is at least obscure"""
    return AllowedOutOfLogic(from_option(Knowledge, Knowledge.option_obscure, "ge"))

def can_block_clip():
    """Player can perform block clips."""
    return AllowedOutOfLogic(from_option(BlockClipsRequired, True))

def can_semi_solid_clip():
    """Player can perform semisolid clips."""
    return AllowedOutOfLogic(from_option(SemiSolidClipsRequired, True))

def can_zip():
    """Player can perform zips."""
    return AllowedOutOfLogic(from_option(ZipsRequired, True))

def can_bunstrike_zip():
    """Player can perform bunstrike zips."""
    return AllowedOutOfLogic(from_option(BunstrikeZipsRequired, True))

def can_do_boring_tricks():
    """Player can perform boring tricks."""
    return AllowedOutOfLogic(from_option(BoringTricksRequired, True))

def can_use_event_warps():
    """Player can use event warps."""
    return AllowedOutOfLogic(from_option(EventWarpsInLogic, True))

def can_enter_plurkwood():
    """Player can enter plurkwood."""
    return AllowedOutOfLogic(from_option(IncludePlurkwood, True))

def has_many_amulet_food():
    """Player has access to many consumables due to being able to reach the town shop"""
    return rules.And(has_item_menu(), rules.Has("Shop Access"), can_bunny_amulet())

@dataclass()
class HasEnoughAmuletFood(rules.Rule["RabiRibiWorld"], game = GAME_NAME):
    """Rule to check if the player can utilize enough items to perform a trick."""
    num_amulet_food: int

    @override
    def _instantiate(self, world: "RabiRibiWorld") -> rules.Rule.Resolved:
        amulet = 0
        food = 0

        if can_bunny_amulet_4().resolve(world):
            amulet = 4
        elif can_bunny_amulet_3().resolve(world):
            amulet = 3
        elif can_bunny_amulet_2().resolve(world):
            amulet = 2
        elif can_bunny_amulet().resolve(world):
            amulet = 1

        if has_item_menu().resolve(world):
            if rules.Or(rules.Has(ItemName.rumi_donut), can_purchase_food()).resolve(world):
                food = 1
                # Eating a Rumi Donut gives an amulet charge
                if can_bunny_amulet().resolve(world):
                    amulet += 1
                food += self.count_normal_consumable_items(world)
                if amulet >= 4 and rules.Has(ItemName.kotri_recruit).resolve(world) and \
                    can_recruit_n_town_members(3).resolve(world):
                    amulet += 1

        return rules.True_().resolve(world) if (amulet + food) >= self.num_amulet_food else rules.False_().resolve(world)

    def count_normal_consumable_items(self, world: "RabiRibiWorld"):
        """Counts which normal consumable items the player can reach, either from locations or purchases."""
        consumables = 0
        if rules.Or(rules.Has(ItemName.rumi_cake), can_purchase_food()).resolve(world):
            consumables += 1
        if rules.Or(rules.Has(ItemName.cocoa_bomb), can_purchase_cocoa_bomb()).resolve(world):
            consumables += 1
        if rules.Has(ItemName.gold_carrot).resolve(world):
            consumables += 1
        return consumables

def from_option(option: type[Option], value: Any, operator: Operator = "eq") -> rules.Rule:
    return rules.True_(options=[rules.OptionFilter(option, value, operator)])

@dataclass()
class AllowedOutOfLogic(rules.WrapperRule["RabiRibiWorld"], game=GAME_NAME):
    @override
    def _instantiate(self, world: "RabiRibiWorld") -> rules.Rule.Resolved:
        if getattr(world.multiworld, "generation_is_fake", False):
            return self.Resolved(
                self.child.resolve(world),
                player=world.player,
                caching_enabled=getattr(world, "rule_caching_enabled", False),
            )
        return self.child.resolve(world)

    class Resolved(rules.WrapperRule.Resolved):
        @override
        def _evaluate(self, state: CollectionState) -> bool:
            return state.has(ItemName.glitched_logic, self.player) and self.child(state)

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            deps = super().item_dependencies()
            deps.setdefault(ItemName.glitched_logic, set()).add(id(self))
            return deps

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            messages: list[JSONMessagePart] = [
                {"type": "color", "color": "yellow", "text": "Out of Logic ["},
            ]
            messages.extend(self.child.explain_json(state))
            messages.append({"type": "color", "color": "yellow", "text": "]"})
            return messages

####################################################
#           Utility used by other modules
####################################################

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
        literal_eval_map: dict[str, rules.Rule[RabiRibiWorld]] = {
            "True": rules.True_(),
            "None": rules.True_(),
            "False": rules.False_(),
            "Impossible": rules.False_(),
            "Carrot Shooter": carrot_shooter_in_logic(),
            "Explosives With Carrot Shooter": carrot_shooter_in_logic(),
            "Bunny Strike": can_bunny_strike(),
            "Bunny Whirl": can_bunny_whirl(),
            "Wall Jump Lv2": wall_jump_2(),
            "Hammer Roll Lv3": can_hammer_roll_3(),
            "Hammer Roll": can_hammer_roll(),
            "Air Dash Lv3": can_air_dash_3(),
            "Air Dash": can_air_dash(),
            "Speed Boost Lv3": can_get_speed_boost_lv3(),
            "Bunny Amulet": can_bunny_amulet(),
            "Bunny Amulet Lv2": can_bunny_amulet_2(),
            "Bunny Amulet Lv3": can_bunny_amulet_3(),
            "Piko Hammer Leveled": rules.Has(ItemName.piko_hammer),
            "Carrot Bomb Entry": rules.Has(ItemName.carrot_bomb),
            "Carrot Shooter Entry": carrot_shooter_in_logic(),
            "Charge Carrot Shooter Entry": can_charge_carrot_shooter_entry(),
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
            "Speedy": can_be_speedy(),
            "Speed1": can_use_speed_1(),
            "Speed2": can_use_speed_2(),
            "Speed3": can_use_speed_3(),
            "Speed5": can_use_speed_5(),
            "3 Magic Types": has_3_magic_types(),
            "Item Menu": has_item_menu(),
            "Chapter 1": rules.Has("Chapter 1"),
            "Chapter 2": rules.Has("Chapter 2"),
            "Chapter 3": rules.Has("Chapter 3"),
            "Chapter 4": rules.Has("Chapter 4"),
            "Chapter 5": rules.Has("Chapter 5"),
            "Chapter 6": rules.Has("Chapter 6"),
            "Chapter 7": rules.Has("Chapter 7"),
            "Boost": can_use_boost(),
            "Boost Many": can_use_boost_many(),
            "Boost Boring": can_use_boost_boring(),
            "Darkness": can_navigate_darkness(),
            "Darkness Without Light Orb": can_navigate_darkness_without_light_orb(),
            "Underwater": can_navigate_underwater(),
            "Underwater Without Water Orb": can_navigate_underwater_without_water_orb(),
            "Prologue Trigger": can_move_out_of_prologue_areas(),
            "Cocoa 1": rules.Has(ItemName.cocoa_1),
            "Kotri 1": rules.Has(ItemName.kotri_1),
            "Ashuri 2": rules.Has(ItemName.ashuri_2),
            "Boss Ribbon": can_reach_ribbon(),
            "Difficulty Hard": is_at_least_hard_difficulty(),
            "Difficulty V Hard": is_at_least_v_hard_difficulty(),
            "Difficulty Extreme": is_at_least_extreme_difficulty(),
            "Difficulty Stupid": is_at_least_stupid_difficulty(),
            "Knowledge Intermediate": is_at_least_intermediate_knowledge(),
            "Knowledge Advanced": is_at_least_advanced_knowledge(),
            "Knowledge Obscure": is_at_least_obscure_knowledge(),
            "Boring Tricks Required": can_do_boring_tricks(),
            "Bunstrike Zip Required": can_bunstrike_zip(),
            "Consumable Use": can_use_consumables(),
            "Amulet Food": HasEnoughAmuletFood(1),
            "2 Amulet Food": HasEnoughAmuletFood(2),
            "3 Amulet Food": HasEnoughAmuletFood(3),
            "4 Amulet Food": HasEnoughAmuletFood(4),
            "6 Amulet Food": HasEnoughAmuletFood(6),
            "Many Amulet Food": has_many_amulet_food(),
            "Open Mode": rules.True_(),
            "Block Clips Required": can_block_clip(),
            "Semisolid Clips Required": can_semi_solid_clip(),
            "Zip Required": can_zip(),
            "Plurkwood Reachable": can_enter_plurkwood(),
            "Warp Destination Reachable": from_option(IncludeWarpDestination, True),
            "Post Game Allowed": from_option(IncludePostGame, True),
            "Post Irisu Allowed": from_option(IncludePostIrisu, True),
            "Halloween Reachable": from_option(IncludeHalloween, True),
            "Boss Keke Bunny" : can_reach_keke_bunny(),
            "Event Warps Required" : can_use_event_warps(),
        }
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
